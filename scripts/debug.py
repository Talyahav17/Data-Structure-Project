
import pandas as pd
import numpy as np
import sys
import os

# Add parent directory to path to import main
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

import main


def run_stage6_sanity_checks():
    """Run comprehensive sanity checks for Stage 6 analysis."""
    print("=== Stage 6 Sanity Checks ===")
    
    try:
        # Load Stage 6 data
        merged_df, features_df, labels_df = main.load_stage6_data()
        print(f"✓ Loaded {len(merged_df)} team-season records")
        
        # 1. Counts validation
        print("\n1. Counts validation:")
        print(f"  Features records: {len(features_df)}")
        print(f"  Merged records: {len(merged_df)}")
        print(f"  Unique teams: {merged_df['team'].nunique()}")
        print(f"  Unique seasons: {merged_df['season'].nunique()}")
        print(f"  Unique clusters: {merged_df['cluster'].nunique()}")
        
        # 2. Range checks for key metrics
        print("\n2. Range checks:")
        metrics = ["TS_pct", "eFG_pct", "pace_proxy", "REB_per_game", "OREB_per_game", 
                   "AST_to_TOV", "STL_per_game", "BLK_per_game"]
        available_metrics = [m for m in metrics if m in merged_df.columns]
        
        for metric in available_metrics:
            values = merged_df[metric].dropna()
            if len(values) > 0:
                min_val, max_val = values.min(), values.max()
                print(f"  {metric}: [{min_val:.3f}, {max_val:.3f}]")
                
                # Check for reasonable ranges
                if metric in ["TS_pct", "eFG_pct"]:
                    if min_val < 0 or max_val > 1:
                        print(f"    ⚠️  WARNING: {metric} outside [0,1] range")
                elif metric == "AST_to_TOV":
                    if min_val < 0:
                        print(f"    ⚠️  WARNING: {metric} has negative values")
        
        # 3. Cluster validation
        print("\n3. Cluster validation:")
        cluster_counts = merged_df["cluster"].value_counts().sort_index()
        print("  Cluster distribution:")
        for cluster_id, count in cluster_counts.items():
            style_name = merged_df[merged_df["cluster"] == cluster_id]["style_name"].iloc[0]
            print(f"    Cluster {cluster_id} ({style_name}): {count} records")
        
        # Check for missing cluster assignments
        missing_clusters = merged_df["cluster"].isna().sum()
        if missing_clusters > 0:
            print(f"    ⚠️  WARNING: {missing_clusters} records without cluster assignment")
        
        # 4. Trends computation test
        print("\n4. Trends computation test:")
        trends_df = main.compute_trends(merged_df)
        print(f"  Computed trends for {len(trends_df)} team-metric combinations")
        
        # Check for NaN slopes
        nan_slopes = trends_df["slope"].isna().sum()
        print(f"  NaN slopes: {nan_slopes} (expected for teams with <2 seasons)")
        
        # 5. Outliers detection test
        print("\n5. Outliers detection test:")
        outliers_df = main.find_outliers(merged_df)
        print(f"  Found {len(outliers_df)} outliers")
        
        if len(outliers_df) > 0:
            outlier_metrics = outliers_df["metric"].value_counts()
            print("  Outliers by metric:")
            for metric, count in outlier_metrics.items():
                print(f"    {metric}: {count} outliers")
        
        # 6. Sample insights
        print("\n6. Sample insights:")
        
        # Top 5 TS% improvements
        ts_trends = trends_df[trends_df["metric"] == "TS_pct"].dropna(subset=["yoy_delta"])
        if len(ts_trends) > 0:
            top_improvers = ts_trends.nlargest(5, "yoy_delta")
            print("  Top 5 TS% improvements:")
            for _, row in top_improvers.iterrows():
                print(f"    {row['team']}: +{row['yoy_delta']:.3f} ({row['seasons_count']} seasons)")
        
        # Cluster performance ranking
        clusters_df = main.analyze_clusters(merged_df)
        if "TS_pct_mean" in clusters_df.columns:
            cluster_ranking = clusters_df.sort_values("TS_pct_mean", ascending=False)
            print("  Cluster TS% ranking:")
            for _, row in cluster_ranking.iterrows():
                print(f"    {row['style_name']}: {row['TS_pct_mean']:.3f}")
        
        # 7. Data quality summary
        print("\n7. Data quality summary:")
        total_records = len(merged_df)
        complete_records = merged_df.dropna(subset=available_metrics).shape[0]
        completeness = (complete_records / total_records) * 100
        print(f"  Data completeness: {completeness:.1f}% ({complete_records}/{total_records})")
        
        print("\n✓ Stage 6 sanity checks completed successfully!")
        
    except Exception as e:
        print(f"❌ Stage 6 sanity checks failed: {e}")
        raise


if __name__ == "__main__":
    run_stage6_sanity_checks()
