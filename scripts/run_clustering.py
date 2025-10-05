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
from ds_project.ml.clustering import run_kmeans_with_selection, derive_cluster_style_labels
from ds_project.viz.plots import save_pca_scatter


def main() -> int:
    df = load_and_clean(lite=True)
    team_season = build_team_season_features(df)

    id_cols = ["season", "team"]
    feature_cols = [c for c in team_season.columns if c not in id_cols]

    res = run_kmeans_with_selection(team_season, feature_cols, k_min=3, k_max=6)

    print("Silhouette scores (higher is better):")
    for k, sil, inertia in res["results"]:
        print(f"  k={k}: silhouette={sil:.3f}, inertia={inertia:.1f}")

    print(f"\nSelected k={res['best_k']}")
    team_season["cluster"] = res["labels"]
    team_season["pc1"] = res["pca_coords"][:, 0]
    team_season["pc2"] = res["pca_coords"][:, 1]

    # Save artifacts
    os.makedirs("data_clean", exist_ok=True)
    csv_path = os.path.join("data_clean", "team_season_clusters.csv")
    team_season.to_csv(csv_path, index=False)

    db_path = os.path.join("data_clean", "nba_clean.sqlite")
    try:
        with sqlite3.connect(db_path) as conn:
            team_season.to_sql("team_season_clusters", conn, if_exists="replace", index=False)
    except Exception as e:
        print("Warning: SQLite save failed:", e)

    plot_path = os.path.join("data_clean", "team_season_pca_clusters.png")
    save_pca_scatter(team_season, "pc1", "pc2", "cluster", plot_path)

    # Derive style labels per cluster and save CSV
    style_cols = [c for c in feature_cols if c in [
        'TS_pct','eFG_pct','pace_proxy','pct_3PA','REB_per_game','OREB_per_game','AST_to_TOV','TOV_per_game','STL_per_game','BLK_per_game'
    ]] or feature_cols
    labels_df = derive_cluster_style_labels(team_season, style_cols, z_threshold=0.6)
    labels_path = os.path.join("data_clean", "cluster_style_labels.csv")
    labels_df.to_csv(labels_path, index=False)

    print("Saved:")
    print("  ", csv_path)
    print("  ", db_path, "[table team_season_clusters]")
    print("  ", plot_path)
    print("  ", labels_path)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
