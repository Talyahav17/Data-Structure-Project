import pandas as pd
import sys
from pathlib import Path

try:
    import main as _legacy
except Exception:
    root = Path(__file__).resolve().parents[3]
    if str(root) not in sys.path:
        sys.path.insert(0, str(root))
    try:
        import importlib.util
        spec = importlib.util.spec_from_file_location('main', str(root / 'main.py'))
        if spec and spec.loader:
            _legacy = importlib.util.module_from_spec(spec)  # type: ignore
            spec.loader.exec_module(_legacy)  # type: ignore
        else:  # pragma: no cover
            _legacy = None
    except Exception:  # pragma: no cover
        _legacy = None


def build_team_season_features(df: pd.DataFrame) -> pd.DataFrame:
    if _legacy is None:
        raise RuntimeError("Legacy 'main.py' not found for delegation")
    return _legacy.build_team_season_features(df)


