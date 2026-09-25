import csv
import random
import tempfile
import unittest
import warnings
from pathlib import Path

from par_buddy import GroupGenerator


class GroupGenerationSimulationTests(unittest.TestCase):
    """Exercise group generation against varied golf rosters."""

    def write_roster(self, player_count, female_count=None, inactive_count=0):
        if female_count is None:
            female_count = max(2, player_count // 3)

        roster_file = tempfile.NamedTemporaryFile(
            mode="w",
            newline="",
            suffix=".csv",
            delete=False,
            encoding="utf-8",
        )
        roster_path = Path(roster_file.name)

        def remove_roster():
            try:
                roster_path.unlink()
            except FileNotFoundError:
                pass

        self.addCleanup(remove_roster)

        writer = csv.writer(roster_file)
        writer.writerow(["name", "ranking", "gender", "playing"])
        female_indices = set(
            random.Random(player_count).sample(range(player_count), female_count)
        )
        for index in range(player_count):
            gender = "Female" if index in female_indices else "Male"
            playing = "no" if index < inactive_count else "yes"
            ranking = (index % 4) + 1
            writer.writerow([f"Player {index + 1}", ranking, gender, playing])
        roster_file.close()
        return roster_file.name

    def assert_valid_groups(self, generator):
        active_names = [player.name for player in generator.active_players]
        assigned_players = [player for group in generator.groups for player in group]
        assigned_names = [player.name for player in assigned_players]

        self.assertEqual(len(assigned_names), len(active_names))
        self.assertCountEqual(assigned_names, active_names)
        self.assertEqual(len(assigned_names), len(set(assigned_names)))

        for group in generator.groups:
            self.assertIn(len(group), (3, 4))
            captain_count = sum(player.ranking == 1 for player in group)
            self.assertGreaterEqual(captain_count, 1)
            self.assertLessEqual(captain_count, 2)

    def expected_group_sizes(self, player_count):
        remainder = player_count % 4
        if remainder == 0:
            return [4] * (player_count // 4)
        if remainder == 1:
            self.assertGreaterEqual(player_count, 9)
            return [4] * ((player_count - 9) // 4) + [3, 3, 3]
        if remainder == 2:
            return [4] * ((player_count - 6) // 4) + [3, 3]
        return [4] * ((player_count - 3) // 4) + [3]

    def test_rosters_from_40_through_80_players(self):
        for player_count in range(40, 81):
            for seed in range(3):
                with self.subTest(player_count=player_count, seed=seed):
                    roster_path = self.write_roster(player_count)
                    generator = GroupGenerator(roster_path)
                    generator.read_csv()

                    with warnings.catch_warnings(record=True) as caught_warnings:
                        warnings.simplefilter("always")
                        random.seed(seed)
                        generator.create_groups()

                    self.assert_valid_groups(generator)
                    self.assertEqual(
                        sorted(len(group) for group in generator.groups),
                        sorted(self.expected_group_sizes(player_count)),
                    )
                    for group in generator.groups:
                        female_count = sum(
                            player.gender.lower() == "female"
                            for player in group
                        )
                        if female_count == 1:
                            self.assertTrue(caught_warnings)
                        else:
                            self.assertTrue(female_count == 0 or female_count >= 2)

    def test_group_sizes_follow_player_conservation(self):
        for player_count in list(range(3, 5)) + list(range(6, 41)):
            with self.subTest(player_count=player_count):
                roster_path = self.write_roster(player_count, female_count=0)
                generator = GroupGenerator(roster_path)
                generator.read_csv()
                random.seed(42)
                generator.create_groups()

                self.assertEqual(
                    sorted(len(group) for group in generator.groups),
                    sorted(self.expected_group_sizes(player_count)),
                )

    def test_insufficient_captains_are_rejected(self):
        roster_path = self.write_roster(12, female_count=0)
        with open(roster_path, newline="", encoding="utf-8") as roster_file:
            rows = list(csv.reader(roster_file))
        for row in rows[2:]:
            row[1] = "2"
        rows[1][1] = "1"
        with open(roster_path, "w", newline="", encoding="utf-8") as roster_file:
            csv.writer(roster_file).writerows(rows)

        generator = GroupGenerator(roster_path)
        generator.read_csv()
        with self.assertRaisesRegex(ValueError, "rank 1"):
            generator.create_groups()

    def test_inactive_players_are_not_assigned(self):
        roster_path = self.write_roster(40, female_count=16, inactive_count=4)
        generator = GroupGenerator(roster_path)
        generator.read_csv()
        random.seed(100)
        generator.create_groups()

        self.assertEqual(len(generator.active_players), 36)
        self.assert_valid_groups(generator)
        self.assertNotIn("Player 1", [p.name for g in generator.groups for p in g])

    def test_unavoidable_single_female_group_warns(self):
        roster_path = self.write_roster(40, female_count=1)
        generator = GroupGenerator(roster_path)
        generator.read_csv()

        with warnings.catch_warnings(record=True) as caught_warnings:
            warnings.simplefilter("always")
            random.seed(200)
            generator.create_groups()

        self.assert_valid_groups(generator)
        self.assertTrue(
            any("single female" in str(warning.message) for warning in caught_warnings)
        )


if __name__ == "__main__":
    unittest.main()
