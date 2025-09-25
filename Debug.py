# Debug.py — Fixed version (Unknowns check and advanced statistics)

import pandas as pd
from collections import Counter
import main

# Load data (will load quickly if up-to-date Parquet exists)
df = main.load_and_clean(lite=True)

print(f"Rows: {len(df):,}")

# Check for Unknowns
for col in ["player_team_abbr", "opponent_team_abbr"]:
    if col in df.columns:
        unk = (df[col].isna()) | (df[col].astype(str).str.upper().eq("UNKNOWN"))
        cnt = int(unk.sum())
        print(f"Unknowns in {col}: {cnt}")
        if cnt:
            # Show TOP source values (can be refined based on your relevant source columns)
            # Here we assume there's 'team_name' and 'opponent_team' — update according to your data
            source_col = "team_name" if "player" in col else "opponent_team"
            if source_col in df.columns:
                top_vals = Counter(df.loc[unk, source_col].fillna("(NaN)")).most_common(20)
                print(f"Top unknown sources for {col}:")
                for k, v in top_vals:
                    print(f"  {k}: {v}")

# אינדיקציות ל-4.H
for col in ["efg_pct", "ts_pct"]:
    if col in df.columns:
        desc = df[col].describe()
        out_of_range = ((df[col] < 0) | (df[col] > 1.5)).sum()
        print(f"{col}: min={desc['min']:.3f}, max={desc['max']:.3f}, mean={desc['mean']:.3f}, out_of_range={int(out_of_range)}")
    else:
        print(f"{col}: MISSING (check core columns)")

print("\n" + "="*50)
print("5 — DB Checks")
print("="*50)

import sqlite3
import os

db_path = "data_clean/nba_clean.sqlite"
if os.path.exists(db_path):
    print(f"Connecting to {db_path}...")
    
    with sqlite3.connect(db_path) as conn:
        # Count rows in each table
        print("\nTable row counts:")
        tables = ["dim_players", "dim_teams", "dim_games", "fact_boxscores"]
        for table in tables:
            try:
                result = conn.execute(f"SELECT COUNT(*) FROM {table}").fetchone()
                print(f"  {table}: {result[0]:,} rows")
            except sqlite3.Error as e:
                print(f"  {table}: Error - {e}")
        
        # Orphan checks
        print("\nOrphan checks:")
        
        # player_id orphans
        try:
            result = conn.execute("""
                SELECT COUNT(*) FROM fact_boxscores f 
                LEFT JOIN dim_players p ON f.player_id = p.player_id 
                WHERE p.player_id IS NULL
            """).fetchone()
            print(f"  Orphan player_ids in fact_boxscores: {result[0]}")
        except sqlite3.Error as e:
            print(f"  Player orphan check failed: {e}")
        
        # game_id orphans
        try:
            result = conn.execute("""
                SELECT COUNT(*) FROM fact_boxscores f 
                LEFT JOIN dim_games g ON f.game_id = g.game_id 
                WHERE g.game_id IS NULL
            """).fetchone()
            print(f"  Orphan game_ids in fact_boxscores: {result[0]}")
        except sqlite3.Error as e:
            print(f"  Game orphan check failed: {e}")
        
        # team_abbr orphans
        try:
            result = conn.execute("""
                SELECT COUNT(*) FROM fact_boxscores f 
                LEFT JOIN dim_teams t ON f.player_team_abbr = t.team_abbr 
                WHERE f.player_team_abbr IS NOT NULL AND t.team_abbr IS NULL
            """).fetchone()
            print(f"  Orphan team_abbrs in fact_boxscores: {result[0]}")
        except sqlite3.Error as e:
            print(f"  Team orphan check failed: {e}")
        
        # Sanity sample - points check
        print("\nSanity check - sample players with points:")
        try:
            result = conn.execute("""
                SELECT p.player_name, SUM(f.team_score) as total_points
                FROM fact_boxscores f
                JOIN dim_players p ON f.player_id = p.player_id
                WHERE f.team_score > 0
                GROUP BY f.player_id, p.player_name
                ORDER BY total_points DESC
                LIMIT 5
            """).fetchall()
            for player, points in result:
                print(f"  {player}: {points} points")
        except sqlite3.Error as e:
            print(f"  Sanity check failed: {e}")
        
        # Sample queries
        print("\nSample queries:")
        
        # Top 5 teams by average eFG%
        try:
            result = conn.execute("""
                SELECT t.team_name, AVG(f.efg_pct) as avg_efg
                FROM fact_boxscores f
                JOIN dim_teams t ON f.player_team_abbr = t.team_abbr
                WHERE f.efg_pct > 0
                GROUP BY f.player_team_abbr, t.team_name
                ORDER BY avg_efg DESC
                LIMIT 5
            """).fetchall()
            print("  Top 5 teams by eFG%:")
            for team, efg in result:
                print(f"    {team}: {efg:.3f}")
        except sqlite3.Error as e:
            print(f"  eFG% query failed: {e}")
        
        # Games per season
        try:
            result = conn.execute("""
                SELECT season, COUNT(DISTINCT game_id) as games
                FROM dim_games
                GROUP BY season
                ORDER BY season
            """).fetchall()
            print("  Games per season:")
            for season, games in result:
                print(f"    {season}: {games} games")
        except sqlite3.Error as e:
            print(f"  Season query failed: {e}")
    
    print("\n✅ Database checks completed!")
else:
    print(f"❌ Database file not found: {db_path}")