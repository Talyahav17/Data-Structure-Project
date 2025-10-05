import os
from typing import Optional
import pandas as pd
import sys
from pathlib import Path

# Temporary wrappers that delegate to existing implementation in main.py
# This keeps behavior stable while providing a clean public API.

try:
    import main as _legacy
except Exception:
    # When executed from scripts/, project root might not be on sys.path
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


def load_and_clean(lite: bool = True, force_rebuild: bool = False, raw_csv_path: Optional[str] = None) -> pd.DataFrame:
    if _legacy is None:
        raise RuntimeError("Legacy module 'main.py' not found in project root")
    if raw_csv_path is None:
        raw_csv_path = getattr(_legacy, "RAW_CSV_PATH", "NBA Team Statistics.xlsx")
    return _legacy.load_and_clean(lite=lite, force_rebuild=force_rebuild, raw_csv_path=raw_csv_path)


def export_to_sqlite(df: pd.DataFrame, db_path: Optional[str] = None) -> None:
    if _legacy is None:
        raise RuntimeError("Legacy module 'main.py' not found in project root")
    return _legacy.export_to_sqlite(df, db_path=db_path)

 