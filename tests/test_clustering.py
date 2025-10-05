import pandas as pd
import numpy as np
import sys, os
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SRC = os.path.join(ROOT, "src")
if SRC not in sys.path:
    sys.path.insert(0, SRC)
from ds_project.ml.clustering import run_kmeans_with_selection


def test_run_kmeans_with_selection_shapes():
    # Create small synthetic dataset with 2 teams over 3 seasons (6 rows)
    rng = np.random.default_rng(0)
    df = pd.DataFrame({
        'season': ['A','A','B','B','C','C'],
        'team': ['T1','T2','T1','T2','T1','T2'],
        'PTS_per_game': rng.normal(100, 10, 6),
        'FGA_per_game': rng.normal(85, 5, 6),
        'FG3A_per_game': rng.normal(35, 5, 6),
        'pct_3PA': rng.uniform(0.3, 0.5, 6),
        'FTA_per_game': rng.normal(20, 3, 6),
        'pct_FTA': rng.uniform(0.1, 0.3, 6),
        'FG_pct': rng.uniform(0.45, 0.55, 6),
        'FG3_pct': rng.uniform(0.33, 0.4, 6),
        'FT_pct': rng.uniform(0.7, 0.85, 6),
        'eFG_pct': rng.uniform(0.5, 0.6, 6),
        'TS_pct': rng.uniform(0.55, 0.62, 6),
        'REB_per_game': rng.normal(44, 4, 6),
        'OREB_per_game': rng.normal(10, 2, 6),
        'DREB_per_game': rng.normal(34, 3, 6),
        'AST_per_game': rng.normal(25, 3, 6),
        'TOV_per_game': rng.normal(13, 2, 6),
        'AST_to_TOV': rng.normal(2.0, 0.2, 6),
        'STL_per_game': rng.normal(7, 1, 6),
        'BLK_per_game': rng.normal(4, 0.5, 6),
        'pace_proxy': rng.normal(90, 5, 6)
    })

    feature_cols = [c for c in df.columns if c not in ['season','team']]
    res = run_kmeans_with_selection(df, feature_cols, k_min=2, k_max=3, random_state=0)
    assert 'labels' in res and len(res['labels']) == len(df)
    assert res['pca_coords'].shape == (len(df), 2)
