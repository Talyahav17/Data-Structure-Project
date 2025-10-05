import os
import sqlite3
import pandas as pd
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SRC = os.path.join(ROOT, "src")
if SRC not in sys.path:
    sys.path.insert(0, SRC)

from ds_project.io.load import load_and_clean
from ds_project.features.team_season import build_team_season_features


def main() -> int:
    df = load_and_clean(lite=True)
    tdf = build_team_season_features(df)

    os.makedirs("data_clean", exist_ok=True)
    csv_path = os.path.join("data_clean", "team_season_features.csv")
    tdf.to_csv(csv_path, index=False)

    db_path = os.path.join("data_clean", "nba_clean.sqlite")
    try:
        with sqlite3.connect(db_path) as conn:
            tdf.to_sql("team_season_features", conn, if_exists="replace", index=False)
    except Exception as e:
        print("Warning: SQLite save failed:", e)

    print("Team-Season features saved to:", csv_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
