# Par Buddy - Random Group Generator

Par Buddy is a Python application that creates randomized groups from a list of players with rankings and playing status. Perfect for organizing golf groups, sports teams, or any activity requiring balanced random grouping.

Available in both **GUI** and **command-line** versions for maximum flexibility.

## Features

- **Random Group Generation**: Creates truly randomized groups with mixed rankings
- **Gender Balancing**: Automatically distributes male and female players evenly across groups
- **Playing Status Filter**: Only groups players marked as "playing this week"
- **Smart Group Balancing**: Prefers groups of 4, but creates groups of 3 when needed for balance
- **Beautiful HTML Output**: Generates a styled HTML report with group assignments
- **Comprehensive Validation**: Validates CSV data and provides clear error messages
- **Ranking Display**: Color-coded ranking badges for captains (Rank 1 players)
- **Flexible Input**: Case-insensitive column headers and optional gender column

## Requirements

- Python 3.6 or higher
- No additional packages required (uses only standard library)
- For GUI version: tkinter (included with most Python installations)

## Quick Start

### GUI Version (Recommended for most users)
```bash
python3 par_buddy_gui.py
```

The GUI provides an intuitive interface where you can:
- Browse and select your CSV file
- Preview player data with validation
- Choose output location for HTML report
- Set optional random seed for reproducible results
- View generation statistics and open results directly

### Command Line Version
```bash
python3 par_buddy.py your_players.csv
```

## CSV File Format

Your CSV file must have these required columns with an optional gender column:

```csv
name,ranking,gender,playing
John Smith,1,Male,yes
Sarah Johnson,2,Female,no
Mike Davis,3,Male,yes
```

### Column Requirements:
- **name**: Player name (cannot be empty)
- **ranking**: Must be 1, 2, 3, or 4
- **gender**: Optional - Male/Female (used for gender balancing)
- **playing**: Must be "yes" or "no" (case-insensitive)

### Column Name Flexibility:
- Column names are case-insensitive (e.g., "Name" or "name" both work)
- Supports both "ranking" and "Ranking" column headers
- Gender column is optional - works with or without it

## Usage

### GUI Version

1. **Launch the application:**
   ```bash
   python3 par_buddy_gui.py
   ```

2. **Select your CSV file** using the "Browse CSV File" button
3. **Preview your data** - the application will validate and display your player data
4. **Choose output location** for the HTML report (or use the default)
5. **Optional:** Set a random seed for reproducible results
6. **Click "Generate Random Groups"** to create your groups
7. **View results** and click "Open HTML Report" to see the formatted output

### Command Line Version

#### Basic Usage
```bash
python3 par_buddy.py your_players.csv
```

#### Custom Output File
```bash
python3 par_buddy.py your_players.csv -o my_groups.html
```

#### Reproducible Results (for testing)
```bash
python3 par_buddy.py your_players.csv --seed 42
```

#### Help
```bash
python3 par_buddy.py --help
```

## Command Line Options

- `csv_file`: Path to your CSV file (required)
- `-o, --output`: Output HTML filename (default: groups.html)
- `--seed`: Random seed for reproducible results (optional)

## How It Works

1. **Data Loading**: Reads and validates your CSV file with flexible column name support
2. **Filtering**: Selects only players with playing="yes"
3. **Gender-Aware Distribution**: Separates players by gender and ranking for balanced assignment
4. **Captain Assignment**: Distributes rank 1 players (captains) evenly across groups with gender balance
5. **Group Filling**: Fills remaining slots with rank 2-4 players, alternating genders for balance
6. **Smart Balancing**: Creates groups of 3-4 players as needed for optimal distribution
7. **HTML Generation**: Creates a beautiful report with gender indicators and group assignments

## Group Balancing Logic

- **Perfect division by 4**: All groups have 4 players
- **1 remainder**: Creates 2 groups of 3 players
- **2 remainder**: Creates 2 groups of 3 players  
- **3 remainder**: Creates 1 group of 3 players

## Example Output

The HTML report includes:
- Summary statistics (total players, active players, groups formed)
- Individual group assignments with player names, gender indicators (♀/♂), and captain badges
- Clean, focused display without cluttered statistics
- List of players not playing this week

## Sample Data

A sample CSV file (`sample_players.csv`) is included for testing:

**GUI Version:**
```bash
python3 par_buddy_gui.py
# Then select sample_players.csv using the Browse button
```

**Command Line Version:**
```bash
python3 par_buddy.py sample_players.csv
```

## Error Handling

The script provides clear error messages for:
- Missing or invalid CSV files
- Incorrect column headers
- Invalid ranking values (not 1, 2, 3, or 4)
- Invalid playing status (not yes/no)
- Empty player names
- Insufficient players (need at least 3 active players)
- Missing required columns (flexible column name matching)

## GUI Features

The graphical interface includes:
- **File Browser Integration:** Easy CSV file selection and HTML output location
- **Data Preview:** Live preview of CSV data with validation
- **Visual Feedback:** Color-coded player status (active/inactive)
- **Progress Indication:** Progress bar during group generation
- **Results Summary:** Detailed statistics and generation summary
- **Direct File Access:** One-click opening of CSV and HTML files
- **Error Handling:** User-friendly error messages and validation

## Output

The generated HTML file features:
- Responsive design that works on desktop and mobile
- Color-coded ranking badges
- Clean, professional styling
- Statistics dashboard
- Separate section for inactive players

## License

This project is open source and available under the MIT License.
