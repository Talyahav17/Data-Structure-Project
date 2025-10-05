# main.py — Fixed version (unified team mappings + Cache for clean file)
import os
import warnings
import pandas as pd
import numpy as np
from pandas.errors import DtypeWarning

# ====== General Settings / Warnings ======
warnings.filterwarnings("ignore", category=FutureWarning)
warnings.filterwarnings("ignore", category=UserWarning)
warnings.filterwarnings("ignore", category=DtypeWarning)
pd.options.mode.chained_assignment = None

# ====== Paths ======
RAW_CSV_PATH = os.path.join("data", "raw", "NBA Team Statistics.xlsx")  # New default location
CLEAN_DIR = "data_clean"
CLEAN_PARQUET = os.path.join(CLEAN_DIR, "PlayerStatistics_clean.parquet")
CLEAN_CSV = os.path.join(CLEAN_DIR, "PlayerStatistics_clean.csv")

# ====== Team Mappings — Single Source of Truth (Global) ======
# Note: The maps below are basic. Recommended to expand them based on TOP unknowns you'll see in Debug.py
TEAM_MAP_FULL = {
    # Examples ("city team" -> "ABR")
    "los angeles lakers": "LAL",
    "los angeles clippers": "LAC",
    "golden state warriors": "GSW",
    "new york knicks": "NYK",
    "brooklyn nets": "BKN",
    "boston celtics": "BOS",
    "chicago bulls": "CHI",
    "miami heat": "MIA",
    "dallas mavericks": "DAL",
    "phoenix suns": "PHX",
    "san antonio spurs": "SAS",
    "oklahoma city thunder": "OKC",
    "new orleans pelicans": "NOP",
    "minnesota timberwolves": "MIN",
    "cleveland cavaliers": "CLE",
    "denver nuggets": "DEN",
    "philadelphia 76ers": "PHI",
    "toronto raptors": "TOR",
    "sacramento kings": "SAC",
    "washington wizards": "WAS",
    "atlanta hawks": "ATL",
    "detroit pistons": "DET",
    "indiana pacers": "IND",
    "orlando magic": "ORL",
    "charlotte hornets": "CHA",
    "memphis grizzlies": "MEM",
    "milwaukee bucks": "MIL",
    "portland trail blazers": "POR",
    "utah jazz": "UTA",
    "houston rockets": "HOU",
    "new orleans hornets": "NOH",  # Historical
    "new jersey nets": "NJN",       # Historical
    "seattle supersonics": "SEA",   # Historical
    "washington bullets": "WSB",    # Historical
    "kansas city kings": "KCK",     # Historical (example)
}

TEAM_MAP_NAME = {
    # Team name only -> abbreviation
    "lakers": "LAL", "clippers": "LAC", "warriors": "GSW", "knicks": "NYK",
    "nets": "BKN", "celtics": "BOS", "bulls": "CHI", "heat": "MIA",
    "mavericks": "DAL", "suns": "PHX", "spurs": "SAS", "thunder": "OKC",
    "pelicans": "NOP", "timberwolves": "MIN", "cavaliers": "CLE", "nuggets": "DEN",
    "76ers": "PHI", "raptors": "TOR", "kings": "SAC", "wizards": "WAS",
    "hawks": "ATL", "pistons": "DET", "pacers": "IND", "magic": "ORL",
    "hornets": "CHA", "grizzlies": "MEM", "bucks": "MIL", "blazers": "POR",
    "jazz": "UTA", "rockets": "HOU",
    # Historical
    "supersonics": "SEA", "sonics": "SEA", "bullets": "WSB",
    # Non-NBA teams (keep as UNKNOWN)
    "braves": "UNKNOWN", "royals": "UNKNOWN", "nationals": "UNKNOWN", 
    "blackhawks": "UNKNOWN", "zephyrs": "UNKNOWN", "packers": "UNKNOWN"
}

TEAM_MAP_CITY = {
    # City only -> abbreviation (prefer less usage, but useful when no full name)
    "los angeles": None,  # Ambiguous (LAL/LAC) — use only if no better option
    "new york": "NYK",  # Historical
    "brooklyn": "BKN",
    "boston": "BOS", "chicago": "CHI", "miami": "MIA", "dallas": "DAL",
    "phoenix": "PHX", "san antonio": "SAS", "oklahoma city": "OKC",
    "new orleans": "NOP", "minnesota": "MIN", "cleveland": "CLE",
    "denver": "DEN", "philadelphia": "PHI", "toronto": "TOR",
    "sacramento": "SAC", "washington": "WAS", "atlanta": "ATL",
    "detroit": "DET", "indiana": "IND", "orlando": "ORL",
    "charlotte": "CHA", "memphis": "MEM", "milwaukee": "MIL",
    "portland": "POR", "utah": "UTA", "houston": "HOU",
    "seattle": "SEA"
}

TEAM_ALIASES = {
    # Patterns/nicknames containing — will be activated in substring search
    "trail blazers": "POR", "blazers": "POR",
    "phila": "PHI", "sixers": "PHI",
    "pels": "NOP", "wolves": "MIN",
    "wiz": "WAS", "celts": "BOS",
}

# ====== Utilities ======

def _to_snake(c: str) -> str:
    c = c.strip()
    c = c.replace("%", "_pct").replace("/", "_").replace("-", "_")
    c = (c
         .replace("FG%", "fg_pct").replace("3P%", "fg3_pct").replace("FT%", "ft_pct")
         .replace("3PM", "fg3m").replace("3PA", "fg3a"))
    c = re_snake.sub(r"_\1", c)
    return c.lower()

import re
re_snake = re.compile(r"(?<!^)([A-Z])")


def _normalize_columns(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df.columns = [_to_snake(x) for x in df.columns]
    return df


def _safe_to_datetime(s: pd.Series) -> pd.Series:
    return pd.to_datetime(s, errors="coerce")


def _safe_to_numeric(s: pd.Series) -> pd.Series:
    return pd.to_numeric(s, errors="coerce")


def _season_from_date(dt: pd.Series) -> pd.Series:
    y = dt.dt.year
    m = dt.dt.month
    start_year = np.where(m >= 8, y, y - 1)
    end_year = start_year + 1
    return pd.Series([f"{sy}-{ey}" for sy, ey in zip(start_year, end_year)], index=dt.index)


def _team_abbr_from_parts(full: str, name: str, city: str) -> str:
    """Try FULL -> NAME -> CITY -> ALIASES. Returns "UNKNOWN" if not found."""
    def norm(x):
        if pd.isna(x) or x is None:
            return ""
        return str(x).strip().lower()
    f, n, ci = norm(full), norm(name), norm(city)

    if f in TEAM_MAP_FULL:
        return TEAM_MAP_FULL[f]
    if n in TEAM_MAP_NAME:
        return TEAM_MAP_NAME[n]
    if ci in TEAM_MAP_CITY and TEAM_MAP_CITY[ci]:
        return TEAM_MAP_CITY[ci]
    # aliases (substring)
    for k, v in TEAM_ALIASES.items():
        if k in f or k in n or k in ci:
            return v
    return "UNKNOWN"


def _map_abbr(uniq_df: pd.DataFrame) -> pd.Series:
    """Expects columns: full, name, city (text)."""
    out = []
    for _, r in uniq_df.iterrows():
        out.append(_team_abbr_from_parts(r.get("full"), r.get("name"), r.get("city")))
    return pd.Series(out, index=uniq_df.index, name="abbr")


def _compute_advanced(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    
    # מיפוי שמות עמודות לנתונים הנוכחיים
    fgm = "field_goals_made" if "field_goals_made" in df.columns else None
    fga = "field_goals_attempted" if "field_goals_attempted" in df.columns else None
    fg3m = "three_pointers_made" if "three_pointers_made" in df.columns else None
    fg3a = "three_pointers_attempted" if "three_pointers_attempted" in df.columns else None
    ftm = "free_throws_made" if "free_throws_made" in df.columns else None
    fta = "free_throws_attempted" if "free_throws_attempted" in df.columns else None
    pts = "team_score" if "team_score" in df.columns else None
    
    # Calculate percentages by made/attempted if available
    if fgm and fga:
        df["fg_pct"] = np.where(df[fga] > 0, df[fgm] / df[fga], 0.0)
    if fg3m and fg3a:
        df["fg3_pct"] = np.where(df[fg3a] > 0, df[fg3m] / df[fg3a], 0.0)
    if ftm and fta:
        df["ft_pct"] = np.where(df[fta] > 0, df[ftm] / df[fta], 0.0)

    # eFG%
    if fgm and fg3m and fga:
        df["efg_pct"] = np.where(df[fga] > 0, (df[fgm] + 0.5 * df[fg3m]) / df[fga], 0.0)

    # TS%
    if pts and fga and fta:
        denom = (2 * (df[fga] + 0.44 * df[fta]))
        df["ts_pct"] = np.where(denom > 0, df[pts] / denom, 0.0)

    # per36 (if minutes column exists)
    minutes_col = "num_minutes" if "num_minutes" in df.columns else None
    if minutes_col:
        minutes = df[minutes_col].replace(0, np.nan)
        stats_cols = [fgm, fga, fg3m, fg3a, ftm, fta, pts]
        stats_cols = [c for c in stats_cols if c is not None]
        for col in stats_cols:
            if col in df.columns:
                df[f"{col}_per36"] = (df[col] * 36) / minutes
        df = df.fillna({c: 0 for c in df.columns if c.endswith("_per36")})
    
    return df


def _create_ids(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    # player_id (deterministic based on name + birth if available)
    base = (df.get("player_name") or df.get("player") or pd.Series([None]*len(df)))
    pid = base.fillna("").astype(str).str.strip().str.lower()
    df["player_id"] = pid.apply(lambda s: pd.util.hash_pandas_object(pd.Series([s]), index=[0],
                                                                    hash_key=None).iloc[0])
    # game_id (if not in source)
    if "game_id" not in df.columns:
        parts = []
        for key in ["game_date", "player_team_abbr", "opponent_team_abbr"]:
            parts.append(df.get(key, pd.Series([""]*len(df))).astype(str))
        combo = parts[0].str.cat(parts[1:], sep="|")
        df["game_id"] = pd.util.hash_pandas_object(combo, index=False)
    return df


def _ensure_team_abbrs(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    
    # מיפוי ישיר ללא יצירת DataFrame ייחודי
    abbr_player = df.apply(lambda r: _team_abbr_from_parts(
        None, r.get("team_name", r.get("teamName", "")), r.get("team_city", r.get("teamCity", ""))
    ), axis=1)
    
    abbr_opp = df.apply(lambda r: _team_abbr_from_parts(
        None, r.get("opponent_team_name", r.get("opponentTeamName", "")), r.get("opponent_team_city", r.get("opponentTeamCity", ""))
    ), axis=1)
    
    df["player_team_abbr"] = abbr_player.values
    df["opponent_team_abbr"] = abbr_opp.values
    return df


# ====== 5 — Export to SQLite ======

def _create_dim_players(df: pd.DataFrame) -> pd.DataFrame:
    """Create dim_players table"""
    # For team data, create unique player_id for each team (not for each game)
    # Use team_name to create unique identifier for each team
    
    # Get unique list of teams
    teams_df = df[["team_name", "player_team_abbr"]].drop_duplicates().copy()
    
    # Create unique player_id for each team
    teams_df["player_id"] = pd.util.hash_pandas_object(
        teams_df["team_name"].astype(str), 
        index=False
    )
    
    # Use team_name as player_name (because this is team data)
    teams_df["player_name"] = teams_df["team_name"] + " (" + teams_df["player_team_abbr"] + ")"
    
    # Return only required columns
    result = teams_df[["player_id", "player_name"]].copy()
    
    return result


def _create_dim_teams(df: pd.DataFrame) -> pd.DataFrame:
    """Create dim_teams table"""
    teams_data = []
    
    # Collect all teams from player_team_abbr
    player_teams = df[["player_team_abbr", "team_name", "team_city"]].drop_duplicates()
    player_teams.columns = ["team_abbr", "team_name", "team_city"]
    teams_data.append(player_teams)
    
    # Collect all teams from opponent_team_abbr
    opp_teams = df[["opponent_team_abbr", "opponent_team_name", "opponent_team_city"]].drop_duplicates()
    opp_teams.columns = ["team_abbr", "team_name", "team_city"]
    teams_data.append(opp_teams)
    
    # Union and remove duplicates
    teams_df = pd.concat(teams_data, ignore_index=True).drop_duplicates(subset=["team_abbr"])
    
    return teams_df[["team_abbr", "team_name", "team_city"]]


def _create_dim_games(df: pd.DataFrame) -> pd.DataFrame:
    """Create dim_games table"""
    # Get unique list of games
    games_df = df[["game_id", "game_date", "season", "player_team_abbr", "opponent_team_abbr"]].drop_duplicates(subset=["game_id"]).copy()
    
    # If there's an original game identifier, add it
    original_game_cols = [c for c in df.columns if "game" in c.lower() and c not in ["game_id", "game_date"]]
    if original_game_cols:
        original_games = df[["game_id"] + original_game_cols].drop_duplicates(subset=["game_id"])
        games_df = games_df.merge(original_games, on="game_id", how="left")
    
    return games_df


def _create_fact_boxscores(df: pd.DataFrame) -> pd.DataFrame:
    """Create fact_boxscores table"""
    fact_df = df.copy()
    
    # Create new player_id for each row (matches dim_players)
    # Use only team_name to create unique player_id for each team
    fact_df["player_id"] = pd.util.hash_pandas_object(
        fact_df["team_name"].astype(str), 
        index=False
    )
    
    # Select all relevant columns
    fact_cols = ["game_id", "player_id", "player_team_abbr", "opponent_team_abbr"]
    
    # Add all numeric and percentage measures (without duplicates)
    numeric_cols = [c for c in fact_df.columns if fact_df[c].dtype in ['int64', 'float64'] and c not in fact_cols]
    fact_cols.extend(numeric_cols)
    
    # Add advanced statistics (without duplicates)
    advanced_cols = [c for c in fact_df.columns if any(x in c.lower() for x in ['pct', 'per36', 'efg', 'ts']) and c not in fact_cols]
    fact_cols.extend(advanced_cols)
    
    # Remove duplicates and maintain order
    fact_cols = list(dict.fromkeys(fact_cols))
    
    # Ensure all columns exist
    available_cols = [c for c in fact_cols if c in fact_df.columns]
    
    return fact_df[available_cols].copy()


def export_to_sqlite(df: pd.DataFrame, db_path: str = None) -> None:
    """Export data to SQLite"""
    if db_path is None:
        db_path = os.path.join(CLEAN_DIR, "nba_clean.sqlite")
    
    # Create directory if it doesn't exist
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    
    # Build tables
    print("Building dimension tables...")
    dim_players = _create_dim_players(df)
    dim_teams = _create_dim_teams(df)
    dim_games = _create_dim_games(df)
    fact_boxscores = _create_fact_boxscores(df)
    
    # Convert player_id to string to avoid SQLite issues
    dim_players["player_id"] = dim_players["player_id"].astype(str)
    fact_boxscores["player_id"] = fact_boxscores["player_id"].astype(str)
    
    # Write to SQLite
    print(f"Writing to {db_path}...")
    import sqlite3
    
    with sqlite3.connect(db_path) as conn:
        # Write tables with data type definitions
        dim_players.to_sql("dim_players", conn, if_exists="replace", index=False, dtype={'player_id': 'TEXT'})
        dim_teams.to_sql("dim_teams", conn, if_exists="replace", index=False)
        dim_games.to_sql("dim_games", conn, if_exists="replace", index=False)
        fact_boxscores.to_sql("fact_boxscores", conn, if_exists="replace", index=False, dtype={'player_id': 'TEXT'})
        
        # Create indexes
        print("Creating indexes...")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_fact_game_player ON fact_boxscores(game_id, player_id)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_fact_player_team ON fact_boxscores(player_team_abbr)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_fact_opponent_team ON fact_boxscores(opponent_team_abbr)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_games_date ON dim_games(game_date)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_players_name ON dim_players(player_name)")
    
    print("SQLite export completed!")


# ====== Pipeline ======

def _run_cleaning_pipeline(raw_csv_path: str) -> pd.DataFrame:
    # Read with convenient types for problematic columns (if they exist)
    if raw_csv_path.endswith('.xlsx'):
        df = pd.read_excel(raw_csv_path)
    else:
        read_kwargs = {
            "low_memory": False,
            "dtype": {
                "gameLabel": "string",
                "gameSubLabel": "string",
            }
        }
        df = pd.read_csv(raw_csv_path, **read_kwargs)

    # 4.B — Normalize column names
    df = _normalize_columns(df)

    # 4.C — Type conversions
    if "game_date" in df.columns:
        df["game_date"] = _safe_to_datetime(df["game_date"])
    # Example of common numeric conversions
    text_columns = ["player_name", "team", "team_name", "opponent", "game_label", "game_sublabel", 
                   "team_city", "opponent_team_city", "opponent_team_name", "team_city", "team_name"]
    numeric_like = [c for c in df.columns if c not in text_columns]
    for c in numeric_like:
        if df[c].dtype == object:
            df[c] = _safe_to_numeric(df[c])

    # 4.D — Basic missing value handling (cautious example)
    if "min" in df.columns:
        zero_mask = (df["min"].fillna(0) == 0)
        zero_cols = [c for c in ["pts","reb","ast","stl","blk","tov","fgm","fga","fg3m","fg3a","ftm","fta"] if c in df.columns]
        df.loc[zero_mask, zero_cols] = df.loc[zero_mask, zero_cols].fillna(0)

    # 4.E — Duplicates
    keys = [k for k in ("person_id", "game_id") if k in df.columns]
    if keys:
        df = df.drop_duplicates(subset=keys, keep="first")
    
    # Remove non-NBA teams (before team mapping)
    non_nba_teams = ["braves", "royals", "nationals", "blackhawks", "zephyrs", "packers"]
    if "team_name" in df.columns:
        df = df[~df["team_name"].str.lower().isin(non_nba_teams)]
    if "teamName" in df.columns:
        df = df[~df["teamName"].str.lower().isin(non_nba_teams)]
    if "opponent_team_name" in df.columns:
        df = df[~df["opponent_team_name"].str.lower().isin(non_nba_teams)]
    if "opponentTeamName" in df.columns:
        df = df[~df["opponentTeamName"].str.lower().isin(non_nba_teams)]

    # 4.F — season
    if "game_date" in df.columns:
        df["season"] = _season_from_date(df["game_date"])

    # 4.G — Team normalization
    df = _ensure_team_abbrs(df)

    # 4.H — Advanced statistics
    df = _compute_advanced(df)

    # 4.I — Identifiers
    df = _create_ids(df)
    
    return df


def load_and_clean(lite: bool = True, force_rebuild: bool = False, raw_csv_path: str = RAW_CSV_PATH) -> pd.DataFrame:
    """
    Load clean data quickly if up-to-date Parquet exists; otherwise run full cleaning and save.
    lite: for quick debugging (not used here for truncation but to maintain existing API).
    force_rebuild: force cleaning run even if clean file is up-to-date.
    """
    os.makedirs(CLEAN_DIR, exist_ok=True)

    need_rebuild = force_rebuild
    if not need_rebuild and os.path.exists(CLEAN_PARQUET):
        try:
            ts_clean = os.path.getmtime(CLEAN_PARQUET)
            ts_raw = os.path.getmtime(raw_csv_path)
            if ts_clean >= ts_raw:
                # Up-to-date — return clean file quickly
                return pd.read_parquet(CLEAN_PARQUET)
        except Exception:
            need_rebuild = True

    # Need to clean again
    df_clean = _run_cleaning_pipeline(raw_csv_path)

    # 4.J — Short validation (can be expanded as needed)
    assert len(df_clean) > 0, "Empty cleaned DataFrame"

    # Quick save to Parquet + CSV
    try:
        df_clean.to_parquet(CLEAN_PARQUET, index=False)
    except Exception:
        pass
    try:
        df_clean.to_csv(CLEAN_CSV, index=False)
    except Exception:
        pass
    
    # Export to SQLite
    try:
        export_to_sqlite(df_clean)
    except Exception as e:
        print(f"Warning: SQLite export failed: {e}")

    return df_clean


# ====== 6 — Team-Season Feature Builder ======

def build_team_season_features(df: pd.DataFrame) -> pd.DataFrame:
    """Aggregate game-level team data into Team-Season features for clustering.

    Expected minimal columns in df:
      - season, game_id, player_team_abbr
      - scoring/attempts: team_score, field_goals_made, field_goals_attempted,
        three_pointers_made, three_pointers_attempted, free_throws_made, free_throws_attempted
      - box stats: reb, oreb, dreb, ast, tov, stl, blk
      - optional: plus_minus

    Returns a DataFrame with one row per (season, team_abbr) and the features listed in the spec.
    """
    required_keys = ["season", "game_id", "player_team_abbr"]
    for c in required_keys:
        if c not in df.columns:
            raise ValueError(f"Missing required column '{c}' in input DataFrame")

    # Helper to safely get a column or zeros if missing
    def col(name: str) -> pd.Series:
        return df[name] if name in df.columns else pd.Series([0] * len(df), index=df.index)

    # Prepare working columns (use zeros if missing)
    pts = col("team_score")
    fgm = col("field_goals_made")
    fga = col("field_goals_attempted")
    fg3m = col("three_pointers_made")
    fg3a = col("three_pointers_attempted")
    ftm = col("free_throws_made")
    fta = col("free_throws_attempted")
    reb = col("reb")
    oreb = col("oreb")
    dreb = col("dreb")
    ast = col("ast")
    tov = col("tov")
    stl = col("stl")
    blk = col("blk")
    plus_minus = df["plus_minus"] if "plus_minus" in df.columns else None

    # Build an aggregation frame first to avoid re-summing multiple times
    work = pd.DataFrame({
        "season": df["season"],
        "team": df["player_team_abbr"],
        "game_id": df["game_id"],
        "PTS": pts,
        "FGM": fgm,
        "FGA": fga,
        "FG3M": fg3m,
        "FG3A": fg3a,
        "FTM": ftm,
        "FTA": fta,
        "REB": reb,
        "OREB": oreb,
        "DREB": dreb,
        "AST": ast,
        "TOV": tov,
        "STL": stl,
        "BLK": blk,
    })
    if plus_minus is not None:
        work["PLUS_MINUS"] = plus_minus

    grp = work.groupby(["season", "team"], as_index=False)

    summed = grp[[
        "PTS", "FGM", "FGA", "FG3M", "FG3A", "FTM", "FTA",
        "REB", "OREB", "DREB", "AST", "TOV", "STL", "BLK"
    ]].sum()

    games = grp["game_id"].nunique().rename(columns={"game_id": "Games"})

    if plus_minus is not None:
        pm = grp["PLUS_MINUS"].mean().rename(columns={"PLUS_MINUS": "+/-_avg"})
        base = summed.merge(games, on=["season", "team"], how="left").merge(pm, on=["season", "team"], how="left")
    else:
        base = summed.merge(games, on=["season", "team"], how="left")

    # Feature calculations
    eps = 1e-9
    G = base["Games"].clip(lower=1)

    # 1. Basic
    base["PTS_per_game"] = base["PTS"] / G

    # 2. Shot profile
    base["FGA_per_game"] = base["FGA"] / G
    base["FG3A_per_game"] = base["FG3A"] / G
    base["pct_3PA"] = base["FG3A"] / (base["FGA"].replace(0, pd.NA))
    base["FTA_per_game"] = base["FTA"] / G
    base["pct_FTA"] = base["FTA"] / (base["FGA"].replace(0, pd.NA))

    # 3. Offensive efficiency
    base["FG_pct"] = base["FGM"] / (base["FGA"].replace(0, pd.NA))
    base["FG3_pct"] = base["FG3M"] / (base["FG3A"].replace(0, pd.NA))
    base["FT_pct"] = base["FTM"] / (base["FTA"].replace(0, pd.NA))
    base["eFG_pct"] = (base["FGM"] + 0.5 * base["FG3M"]) / (base["FGA"].replace(0, pd.NA))
    base["TS_pct"] = base["PTS"] / (2 * (base["FGA"] + 0.44 * base["FTA"]).replace(0, pd.NA))

    # 4. Rebounds
    base["REB_per_game"] = base["REB"] / G
    base["OREB_per_game"] = base["OREB"] / G
    base["DREB_per_game"] = base["DREB"] / G

    # 5. Assists and turnovers
    base["AST_per_game"] = base["AST"] / G
    base["TOV_per_game"] = base["TOV"] / G
    base["AST_to_TOV"] = base["AST"] / (base["TOV"].replace(0, pd.NA))

    # 6. Defense
    base["STL_per_game"] = base["STL"] / G
    base["BLK_per_game"] = base["BLK"] / G

    # 7. Control / Pace proxy
    base["pace_proxy"] = base["FGA"] / G
    if plus_minus is not None:
        base["plus_minus_avg"] = base["+/-_avg"]

    # Clean up infs/nans from zero-denominator divisions
    base = base.replace([pd.NA, np.inf, -np.inf], 0)

    # Reorder/select columns
    out_cols = [
        "season", "team", "Games",
        "PTS_per_game",
        "FGA_per_game", "FG3A_per_game", "pct_3PA",
        "FTA_per_game", "pct_FTA",
        "FG_pct", "FG3_pct", "FT_pct", "eFG_pct", "TS_pct",
        "REB_per_game", "OREB_per_game", "DREB_per_game",
        "AST_per_game", "TOV_per_game", "AST_to_TOV",
        "STL_per_game", "BLK_per_game",
        "pace_proxy",
    ]
    if plus_minus is not None:
        out_cols.append("plus_minus_avg")

    return base[out_cols].copy()

