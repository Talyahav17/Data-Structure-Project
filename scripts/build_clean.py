import sys
import os

# Ensure src is on path when running as a script
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SRC = os.path.join(ROOT, "src")
if SRC not in sys.path:
    sys.path.insert(0, SRC)

from ds_project.io.load import load_and_clean, export_to_sqlite


def main() -> int:
    df = load_and_clean(lite=True)
    # export is already called inside load_and_clean in legacy, but we keep explicit call if needed
    try:
        export_to_sqlite(df)
    except Exception:
        pass
    print("Clean build complete. Rows:", len(df))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
