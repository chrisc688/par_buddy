#!/usr/bin/env python3
"""
Par Buddy - Random Group Generator for Players with Rankings

This script reads a CSV file containing player names, rankings (1-3), and playing status,
then creates randomized groups of 4 players (or 3 for balancing) and outputs the results to HTML.
"""

import csv
import random
import argparse
import sys
from pathlib import Path
from typing import List, Dict, Tuple


class Player:
    """Represents a player with name, ranking, gender, and playing status."""
    
    def __init__(self, name: str, ranking: int, gender: str, playing: str):
        self.name = name.strip()
        self.ranking = int(ranking)
        self.gender = gender.strip()
        self.playing = playing.strip().lower()
    
    def __repr__(self):
        return f"Player('{self.name}', {self.ranking}, '{self.gender}', '{self.playing}')"


class GroupGenerator:
    """Handles the logic for creating random groups from player data."""
    
    def __init__(self, csv_file_path: str):
        self.csv_file_path = csv_file_path
        self.all_players: List[Player] = []
        self.active_players: List[Player] = []
        self.groups: List[List[Player]] = []
    
    def read_csv(self) -> None:
        """Read and validate the CSV file."""
        try:
            with open(self.csv_file_path, 'r', newline='', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                
                # Create case-insensitive column mapping
                fieldnames = reader.fieldnames or []
                column_map = {}
                for field in fieldnames:
                    column_map[field.lower()] = field
                
                # Check required columns (case-insensitive)
                required_columns = {'name', 'ranking', 'playing'}
                available_columns = set(column_map.keys())
                
                if not required_columns.issubset(available_columns):
                    missing = required_columns - available_columns
                    raise ValueError(f"Missing required columns: {missing}")
                
                # Check if gender column exists
                has_gender = 'gender' in available_columns
                
                for row_num, row in enumerate(reader, start=2):  # Start at 2 for header
                    try:
                        # Get column values using case-insensitive mapping
                        name_col = column_map['name']
                        ranking_col = column_map['ranking']
                        playing_col = column_map['playing']
                        gender_col = column_map.get('gender', '') if has_gender else ''
                        
                        # Validate ranking
                        ranking = int(row[ranking_col])
                        if ranking not in [1, 2, 3, 4]:  # Allow rank 4 as seen in hasg_golf_roster.csv
                            raise ValueError(f"Row {row_num}: Ranking must be 1, 2, 3, or 4, got {ranking}")
                        
                        # Validate playing status
                        playing = row[playing_col].strip().lower()
                        if playing not in ['yes', 'no']:
                            raise ValueError(f"Row {row_num}: Playing must be 'yes' or 'no', got '{row[playing_col]}'")
                        
                        # Validate name
                        name = row[name_col].strip()
                        if not name:
                            raise ValueError(f"Row {row_num}: Name cannot be empty")
                        
                        # Get gender if available
                        gender = row[gender_col].strip() if has_gender and gender_col else ''
                        
                        player = Player(name, ranking, gender, playing)
                        self.all_players.append(player)
                        
                        if player.playing == 'yes':
                            self.active_players.append(player)
                    
                    except (ValueError, KeyError) as e:
                        raise ValueError(f"Error processing row {row_num}: {e}")
        
        except FileNotFoundError:
            raise FileNotFoundError(f"CSV file not found: {self.csv_file_path}")
        except Exception as e:
            raise Exception(f"Error reading CSV file: {e}")
    
    def create_groups(self) -> None:
        """Create randomized groups from active players with ranking-aware distribution.
        
        Each group will have 1-2 rank 1 players (preferring 1), with remaining spots
        filled by rank 2, rank 3 and rank 4 players.
        """
        if len(self.active_players) < 3:
            raise ValueError(f"Not enough active players to form groups. Need at least 3, got {len(self.active_players)}")
        
        # Separate players by ranking and shuffle each group
        rank_1_players = [p for p in self.active_players if p.ranking == 1]
        rank_2_players = [p for p in self.active_players if p.ranking == 2]
        rank_3_players = [p for p in self.active_players if p.ranking == 3]
        rank_4_players = [p for p in self.active_players if p.ranking == 4]
        
        # Separate rank 1 players by gender for better distribution
        rank_1_male = [p for p in rank_1_players if p.gender.lower() == 'male']
        rank_1_female = [p for p in rank_1_players if p.gender.lower() == 'female']
        
        # Shuffle each gender group separately
        random.shuffle(rank_1_male)
        random.shuffle(rank_1_female)
        
        # Interleave rank 1 players to promote gender balance
        rank_1_players = []
        max_rank_1 = max(len(rank_1_male), len(rank_1_female))
        for i in range(max_rank_1):
            if i < len(rank_1_female):
                rank_1_players.append(rank_1_female[i])
            if i < len(rank_1_male):
                rank_1_players.append(rank_1_male[i])
        
        random.shuffle(rank_2_players)
        random.shuffle(rank_3_players)
        random.shuffle(rank_4_players)
        
        # Calculate optimal group sizes - prefer more groups of 3 to better distribute rank 1 players
        total_players = len(self.active_players)
        rank_1_count = len(rank_1_players)
        
        # Strategy: Create enough groups so each can have exactly 1 rank 1 player when possible
        # If we have more rank 1 players than the minimum groups needed, create more groups of 3
        
        # Minimum groups needed based on total players (assuming groups of 4)
        min_groups_of_4 = total_players // 4
        remainder = total_players % 4
        
        # Calculate how many groups we'd need to give each rank 1 player their own group
        ideal_groups_for_rank_1 = rank_1_count
        
        # Determine group distribution to better accommodate rank 1 players
        if ideal_groups_for_rank_1 <= min_groups_of_4 + (1 if remainder > 0 else 0):
            # We can accommodate rank 1 players with standard grouping
            if remainder == 0:
                groups_of_4 = total_players // 4
                groups_of_3 = 0
            elif remainder == 1:
                groups_of_4 = (total_players // 4) - 1
                groups_of_3 = 2
            elif remainder == 2:
                groups_of_4 = (total_players // 4) - 1
                groups_of_3 = 2
            else:  # remainder == 3
                groups_of_4 = total_players // 4
                groups_of_3 = 1
        else:
            # We have more rank 1 players than standard groups - create more groups of 3
            # Try to create enough groups to give each rank 1 player their own group
            target_groups = min(ideal_groups_for_rank_1, total_players // 3)  # Can't have groups smaller than 3
            
            # Calculate mix of group sizes to reach target number of groups
            # Start with all groups of 3, then convert some to groups of 4 if needed
            groups_of_3 = target_groups
            remaining_players = total_players - (groups_of_3 * 3)
            
            if remaining_players > 0:
                # We have leftover players, need to adjust
                if remaining_players <= groups_of_3:
                    # Convert some groups of 3 to groups of 4
                    groups_to_convert = remaining_players
                    groups_of_4 = groups_to_convert
                    groups_of_3 = groups_of_3 - groups_to_convert
                else:
                    # Need to add more groups - fall back to standard logic
                    groups_of_4 = total_players // 4
                    groups_of_3 = 1 if total_players % 4 == 3 else 2 if total_players % 4 in [1, 2] else 0
            else:
                groups_of_4 = 0
        
        total_groups = groups_of_4 + groups_of_3
        
        # Check if we have any rank 1 players
        if len(rank_1_players) == 0:
            raise ValueError("No rank 1 players available. Each group should have at least one rank 1 player.")
        
        # Initialize groups with their target sizes
        group_sizes = [4] * groups_of_4 + [3] * groups_of_3
        self.groups = [[] for _ in range(total_groups)]
        
        # Phase 1: Distribute rank 1 players (1 per group initially)
        rank_1_index = 0
        for i in range(total_groups):
            if rank_1_index < len(rank_1_players):
                self.groups[i].append(rank_1_players[rank_1_index])
                rank_1_index += 1
        
        # Phase 2: Distribute remaining rank 1 players (max 1 more per group)
        group_index = 0
        while rank_1_index < len(rank_1_players) and group_index < total_groups:
            # Only add a second rank 1 player if the group currently has exactly 1
            current_rank_1_count = sum(1 for p in self.groups[group_index] if p.ranking == 1)
            if current_rank_1_count == 1:
                self.groups[group_index].append(rank_1_players[rank_1_index])
                rank_1_index += 1
            group_index += 1
        
        # If we still have rank 1 players left, we have too many
        if rank_1_index < len(rank_1_players):
            remaining_rank_1 = len(rank_1_players) - rank_1_index
            raise ValueError(f"Too many rank 1 players. Have {len(rank_1_players)} rank 1 players "
                           f"but can only accommodate {rank_1_index} (max 2 per group in {total_groups} groups).")
        
        # Phase 3: Fill remaining slots with rank 2, rank 3, and rank 4 players
        # Separate by gender for better distribution
        rank_2_male = [p for p in rank_2_players if p.gender.lower() == 'male']
        rank_2_female = [p for p in rank_2_players if p.gender.lower() == 'female']
        rank_3_male = [p for p in rank_3_players if p.gender.lower() == 'male']
        rank_3_female = [p for p in rank_3_players if p.gender.lower() == 'female']
        rank_4_male = [p for p in rank_4_players if p.gender.lower() == 'male']
        rank_4_female = [p for p in rank_4_players if p.gender.lower() == 'female']
        
        # Create combined lists prioritizing female distribution
        all_remaining_players = []
        
        # Add players in a way that promotes gender balance
        max_len = max(len(rank_2_male), len(rank_2_female), len(rank_3_male), 
                     len(rank_3_female), len(rank_4_male), len(rank_4_female))
        
        for i in range(max_len):
            # Add one from each category if available, prioritizing females for balance
            if i < len(rank_2_female):
                all_remaining_players.append(rank_2_female[i])
            if i < len(rank_2_male):
                all_remaining_players.append(rank_2_male[i])
            if i < len(rank_3_female):
                all_remaining_players.append(rank_3_female[i])
            if i < len(rank_3_male):
                all_remaining_players.append(rank_3_male[i])
            if i < len(rank_4_female):
                all_remaining_players.append(rank_4_female[i])
            if i < len(rank_4_male):
                all_remaining_players.append(rank_4_male[i])
        
        # Shuffle the combined list to add randomness while maintaining gender balance
        random.shuffle(all_remaining_players)
        
        # Distribute players to groups
        player_index = 0
        for i, target_size in enumerate(group_sizes):
            current_size = len(self.groups[i])
            remaining_slots = target_size - current_size
            
            # Fill remaining slots
            while remaining_slots > 0 and player_index < len(all_remaining_players):
                self.groups[i].append(all_remaining_players[player_index])
                player_index += 1
                remaining_slots -= 1
        
        # Verify all players have been assigned
        total_assigned = sum(len(group) for group in self.groups)
        if total_assigned != len(self.active_players):
            raise ValueError(f"Player assignment error: {total_assigned} assigned, {len(self.active_players)} total active players")
        
        # Verify no group has more than 2 rank 1 players
        for i, group in enumerate(self.groups):
            rank_1_count = sum(1 for p in group if p.ranking == 1)
            if rank_1_count > 2:
                raise ValueError(f"Group {i+1} has {rank_1_count} rank 1 players, maximum allowed is 2")
    
    def get_statistics(self) -> Dict:
        """Get summary statistics about players and groups."""
        total_players = len(self.all_players)
        active_players = len(self.active_players)
        inactive_players = total_players - active_players
        
        # Count by ranking for active players
        ranking_counts = {1: 0, 2: 0, 3: 0, 4: 0}
        for player in self.active_players:
            if player.ranking in ranking_counts:
                ranking_counts[player.ranking] += 1
        
        return {
            'total_players': total_players,
            'active_players': active_players,
            'inactive_players': inactive_players,
            'total_groups': len(self.groups),
            'ranking_counts': ranking_counts,
            'group_sizes': [len(group) for group in self.groups]
        }


class HTMLGenerator:
    """Generates HTML output for the groups."""
    
    def __init__(self, generator: GroupGenerator):
        self.generator = generator
    
    def generate_html(self, output_file: str) -> None:
        """Generate HTML file with group assignments."""
        stats = self.generator.get_statistics()
        
        html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Par Buddy - Random Group Assignments</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f5f5f5;
        }}
        .header {{
            text-align: center;
            margin-bottom: 30px;
            background: white;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        }}
        .stats {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin-bottom: 30px;
        }}
        .stat-card {{
            background: white;
            padding: 15px;
            border-radius: 8px;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
            text-align: center;
        }}
        .stat-number {{
            font-size: 2em;
            font-weight: bold;
            color: #2c3e50;
        }}
        .stat-label {{
            color: #7f8c8d;
            margin-top: 5px;
        }}
        .groups-container {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }}
        .group {{
            background: white;
            border-radius: 10px;
            padding: 20px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            border-left: 5px solid #3498db;
        }}
        .group-header {{
            font-size: 1.3em;
            font-weight: bold;
            margin-bottom: 15px;
            color: #2c3e50;
            border-bottom: 2px solid #ecf0f1;
            padding-bottom: 10px;
        }}
        .player {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 8px 0;
            border-bottom: 1px solid #ecf0f1;
        }}
        .player:last-child {{
            border-bottom: none;
        }}
        .player-name {{
            font-weight: 500;
        }}
        .player-ranking {{
            background: #3498db;
            color: white;
            padding: 4px 8px;
            border-radius: 15px;
            font-size: 0.9em;
            font-weight: bold;
        }}
        .ranking-1 {{ background: #e74c3c; }}
        .ranking-2 {{ background: #f39c12; }}
        .ranking-3 {{ background: #27ae60; }}
        .inactive-players {{
            background: white;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
            border-left: 5px solid #95a5a6;
        }}
        .inactive-header {{
            font-size: 1.2em;
            font-weight: bold;
            margin-bottom: 15px;
            color: #7f8c8d;
        }}
        .inactive-player {{
            display: inline-block;
            background: #ecf0f1;
            padding: 5px 10px;
            margin: 3px;
            border-radius: 15px;
            font-size: 0.9em;
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>🏌️ Par Buddy - Random Group Assignments</h1>
        <p>Generated on {self._get_timestamp()}</p>
    </div>
    
    <div class="stats">
        <div class="stat-card">
            <div class="stat-number">{stats['total_players']}</div>
            <div class="stat-label">Total Players</div>
        </div>
        <div class="stat-card">
            <div class="stat-number">{stats['active_players']}</div>
            <div class="stat-label">Playing This Week</div>
        </div>
        <div class="stat-card">
            <div class="stat-number">{stats['total_groups']}</div>
            <div class="stat-label">Groups Formed</div>
        </div>
    </div>
    
    <div class="groups-container">
"""
        
        # Add groups
        for i, group in enumerate(self.generator.groups, 1):
            html_content += f"""        <div class="group">
            <div class="group-header">Group {i} ({len(group)} players)</div>
"""
            # Sort players by last name alphabetically
            def get_last_name(player):
                name_parts = player.name.strip().split()
                return name_parts[-1].lower() if name_parts else player.name.lower()
            
            sorted_group = sorted(group, key=get_last_name)
            
            for player in sorted_group:
                # Only show ranking badge for rank 1 players (Captains)
                if player.ranking == 1:
                    rank_badge = f'<span class="player-ranking ranking-{player.ranking}">Captain</span>'
                else:
                    rank_badge = ''
                
                # Show gender indicator if available
                gender_indicator = ''
                if player.gender:
                    gender_symbol = '♀' if player.gender.lower() == 'female' else '♂' if player.gender.lower() == 'male' else ''
                    if gender_symbol:
                        gender_indicator = f' {gender_symbol}'
                
                html_content += f"""            <div class="player">
                <span class="player-name">{player.name}{gender_indicator}</span>
                {rank_badge}
            </div>
"""
            html_content += "        </div>\n"
        
        html_content += "    </div>\n"
        
        # Add inactive players section if any
        inactive_players = [p for p in self.generator.all_players if p.playing == 'no']
        if inactive_players:
            html_content += f"""    <div class="inactive-players">
        <div class="inactive-header">🚫 Not Playing This Week ({len(inactive_players)} players)</div>
"""
            for player in inactive_players:
                html_content += f'        <span class="inactive-player">{player.name}</span>\n'
            html_content += "    </div>\n"
        
        html_content += """</body>
</html>"""
        
        # Write to file
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(html_content)
    
    def _get_timestamp(self) -> str:
        """Get current timestamp for display."""
        from datetime import datetime
        return datetime.now().strftime("%B %d, %Y at %I:%M %p")


def main():
    """Main function to run the group generator."""
    parser = argparse.ArgumentParser(description='Generate random groups from player CSV data')
    parser.add_argument('csv_file', help='Path to the CSV file containing player data')
    parser.add_argument('-o', '--output', default='groups.html', 
                       help='Output HTML file name (default: groups.html)')
    parser.add_argument('--seed', type=int, help='Random seed for reproducible results')
    
    args = parser.parse_args()
    
    # Set random seed if provided
    if args.seed:
        random.seed(args.seed)
        print(f"Using random seed: {args.seed}")
    
    try:
        # Create generator and process data
        generator = GroupGenerator(args.csv_file)
        print(f"Reading CSV file: {args.csv_file}")
        generator.read_csv()
        
        print(f"Creating random groups...")
        generator.create_groups()
        
        # Generate HTML output
        html_gen = HTMLGenerator(generator)
        html_gen.generate_html(args.output)
        
        # Print summary
        stats = generator.get_statistics()
        print(f"\n✅ Groups generated successfully!")
        print(f"📊 Summary:")
        print(f"   • Total players: {stats['total_players']}")
        print(f"   • Active players: {stats['active_players']}")
        print(f"   • Groups created: {stats['total_groups']}")
        print(f"   • Group sizes: {', '.join(map(str, stats['group_sizes']))}")
        print(f"   • Ranking distribution: Rank 1: {stats['ranking_counts'][1]}, Rank 2: {stats['ranking_counts'][2]}, Rank 3: {stats['ranking_counts'][3]}, Rank 4: {stats['ranking_counts'][4]}")
        print(f"📄 Output saved to: {args.output}")
        
    except Exception as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
