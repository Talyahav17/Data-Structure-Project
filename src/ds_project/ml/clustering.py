from typing import Dict, Any, Tuple
import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
from sklearn.decomposition import PCA


def run_kmeans_with_selection(features: pd.DataFrame, feature_cols: list, k_min: int = 3, k_max: int = 6, random_state: int = 42) -> Dict[str, Any]:
    scaler = StandardScaler()
    X = scaler.fit_transform(features[feature_cols])

    results = []
    for k in range(k_min, k_max + 1):
        km = KMeans(n_clusters=k, n_init=10, random_state=random_state)
        labels = km.fit_predict(X)
        sil = silhouette_score(X, labels) if k > 1 else np.nan
        results.append((k, sil, km.inertia_, labels, km))

    best = max(results, key=lambda t: t[1])
    best_k, best_sil, best_inertia, best_labels, best_model = best

    pca = PCA(n_components=2, random_state=random_state)
    coords = pca.fit_transform(X)

    return {
        "X": X,
        "scaler": scaler,
        "results": [(k, sil, inertia) for (k, sil, inertia, _, _) in results],
        "best_k": best_k,
        "labels": best_labels,
        "model": best_model,
        "pca_coords": coords,
    }


def derive_cluster_style_labels(team_season: pd.DataFrame, feature_cols: list, z_threshold: float = 0.6) -> pd.DataFrame:
    """Return a DataFrame mapping cluster -> suggested style name and key traits.

    Uses simple Z-score thresholds on interpretable features to assign a name.
    """
    df = team_season.copy()
    # Compute Z-scores per feature over all rows
    z = (df[feature_cols] - df[feature_cols].mean()) / df[feature_cols].std(ddof=0)
    z.columns = [f"z_{c}" for c in z.columns]
    df = pd.concat([df[["cluster"]], z], axis=1)

    rows = []
    for cl, g in df.groupby("cluster"):
        # aggregate mean Z per cluster
        zmean = g.mean(numeric_only=True)
        traits = []
        name = "Balanced"

        # Heuristics
        if zmean.get("z_pace_proxy", 0) > z_threshold and zmean.get("z_pct_3PA", 0) > z_threshold and zmean.get("z_TS_pct", 0) > 0:
            name = "Run & Gun"
            traits.extend(["High pace", "High 3PA%", "Good TS%"])
        elif zmean.get("z_pace_proxy", 0) < -z_threshold and (zmean.get("z_REB_per_game", 0) > z_threshold or zmean.get("z_OREB_per_game", 0) > z_threshold) and zmean.get("z_pct_3PA", 0) < 0:
            name = "Inside Focused"
            traits.extend(["Low pace", "High REB/OREB", "Low 3PA%"])
        elif zmean.get("z_AST_to_TOV", 0) > z_threshold and zmean.get("z_TS_pct", 0) > 0:
            name = "Efficient Ball Movement"
            traits.extend(["High AST/TOV", "Good TS%"])
        elif zmean.get("z_pace_proxy", 0) > z_threshold and zmean.get("z_TS_pct", 0) < 0 and zmean.get("z_TOV_per_game", 0) > 0:
            name = "Chaotic Offense"
            traits.extend(["High pace", "Low TS%", "High TOV"])
        elif zmean.get("z_STL_per_game", 0) > z_threshold and zmean.get("z_BLK_per_game", 0) > z_threshold:
            name = "Defensive Identity"
            traits.extend(["High steals", "High blocks"])
        else:
            # pick top-3 absolute traits for description
            top = zmean.abs().sort_values(ascending=False).head(3)
            traits = [f"{k.replace('z_','')}: {'high' if zmean[k]>0 else 'low'}" for k in top.index]

        rows.append({"cluster": int(cl), "style_name": name, "key_traits": ", ".join(traits)})

    return pd.DataFrame(rows).sort_values("cluster").reset_index(drop=True)


