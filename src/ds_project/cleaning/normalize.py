import pandas as pd

try:
    import main as _legacy
except Exception:
    _legacy = None


def normalize_columns(df: pd.DataFrame) -> pd.DataFrame:
    if _legacy is None:
        raise RuntimeError("Legacy 'main.py' not found for delegation")
    return _legacy._normalize_columns(df)


def ensure_team_abbreviations(df: pd.DataFrame) -> pd.DataFrame:
    if _legacy is None:
        raise RuntimeError("Legacy 'main.py' not found for delegation")
    return _legacy._ensure_team_abbrs(df)


