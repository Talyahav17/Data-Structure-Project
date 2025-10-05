import pandas as pd
import sys, os
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SRC = os.path.join(ROOT, "src")
if SRC not in sys.path:
    sys.path.insert(0, SRC)
from ds_project.features.team_season import build_team_season_features


def test_build_team_season_features_basic():
    df = pd.DataFrame({
        'season': ['2023-2024', '2023-2024'],
        'game_id': [1, 2],
        'player_team_abbr': ['ABC', 'ABC'],
        'team_score': [100, 110],
        'field_goals_made': [40, 42],
        'field_goals_attempted': [80, 84],
        'three_pointers_made': [10, 12],
        'three_pointers_attempted': [30, 36],
        'free_throws_made': [10, 14],
        'free_throws_attempted': [12, 16],
        'reb': [40, 44],
        'oreb': [10, 12],
        'dreb': [30, 32],
        'ast': [25, 28],
        'tov': [12, 10],
        'stl': [7, 6],
        'blk': [5, 4],
        'plus_minus': [5, -3]
    })

    out = build_team_season_features(df)
    assert len(out) == 1
    row = out.iloc[0]
    assert row['season'] == '2023-2024'
    assert row['team'] == 'ABC'
    # Average points per game should be 105
    assert abs(row['PTS_per_game'] - 105) < 1e-6
    # eFG% reasonable between 0 and 1
    assert 0 <= row['eFG_pct'] <= 1
