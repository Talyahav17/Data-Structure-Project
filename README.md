# NBA Data Processing Pipeline

A comprehensive data processing pipeline for NBA team statistics that cleans, transforms, and exports data to multiple formats including SQLite with a star schema.

## Features

- **Data Cleaning Pipeline**: Comprehensive cleaning of NBA team statistics data
- **Team Mapping**: Advanced team name normalization and abbreviation mapping
- **Advanced Statistics**: Automatic calculation of eFG%, TS%, and per-36 stats
- **Multiple Export Formats**: CSV, Parquet, and SQLite database
- **Star Schema Database**: Properly normalized dim/fact table structure
- **Performance Optimization**: Parquet caching for fast subsequent loads
- **Data Validation**: Comprehensive checks for data integrity and orphans

## Project Structure

```
├── main.py              # Core data processing pipeline
├── Debug.py             # Data validation and verification
├── data_clean/          # Generated clean data files
│   ├── nba_clean.sqlite # SQLite database with star schema
│   ├── *.parquet        # Fast-loading Parquet files
│   └── *.csv           # Human-readable CSV files
└── README.md           # This file
```

## Database Schema

The pipeline creates a star schema with the following tables:

### Dimension Tables
- **`dim_players`**: Team information (32 NBA teams)
- **`dim_teams`**: Team details with city and abbreviation
- **`dim_games`**: Game metadata (date, season, teams)

### Fact Table
- **`fact_boxscores`**: Team performance statistics per game

## Usage

### Basic Usage
```python
import main

# Load and clean data (uses Parquet cache if available)
df = main.load_and_clean()

# Force rebuild from source
df = main.load_and_clean(force_rebuild=True)
```

### Data Validation
```python
# Run comprehensive validation checks
python Debug.py
```

## Data Processing Steps

1. **Data Loading**: Supports both CSV and Excel files
2. **Column Normalization**: Converts column names to snake_case
3. **Team Mapping**: Maps team names to standardized abbreviations
4. **Advanced Statistics**: Calculates eFG%, TS%, and per-36 metrics
5. **Data Validation**: Checks for unknowns, outliers, and data integrity
6. **Export**: Saves to multiple formats with proper indexing

## Configuration

Update the `RAW_CSV_PATH` in `main.py` to point to your data file:

```python
RAW_CSV_PATH = "NBA Team Statistics.xlsx"  # Update path as needed
```

## Team Mapping

The pipeline includes comprehensive team mapping for:
- Historical team names and relocations
- Common team nicknames and abbreviations
- Non-NBA teams filtering

## Performance

- **First Run**: Full data processing (may take time)
- **Subsequent Runs**: Fast loading from Parquet cache
- **Database Queries**: Optimized with proper indexing

## Requirements

- Python 3.7+
- pandas
- numpy
- pyarrow (for Parquet support)
- openpyxl (for Excel support)

## Installation

```bash
pip install pandas numpy pyarrow openpyxl
```

## Data Validation

The Debug.py script provides comprehensive validation:

- **Unknown Team Checks**: Identifies unmapped team names
- **Advanced Statistics Validation**: Verifies calculated metrics
- **Database Integrity**: Checks for orphan records and referential integrity
- **Sample Queries**: Demonstrates data quality and accessibility

## License

This project is for educational and research purposes.
# Data-Structure-Project
