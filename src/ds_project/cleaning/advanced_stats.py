import pandas as pd

try:
    import main as _legacy
except Exception:
    _legacy = None


def compute_advanced(df: pd.DataFrame) -> pd.DataFrame:
    if _legacy is None:
        raise RuntimeError("Legacy 'main.py' not found for delegation")
    return _legacy._compute_advanced(df)


