import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns


def save_pca_scatter(df: pd.DataFrame, x_col: str, y_col: str, hue_col: str, out_path: str) -> str:
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    plt.figure(figsize=(9, 7))
    palette = sns.color_palette("tab10", n_colors=len(np.unique(df[hue_col])))
    sns.scatterplot(
        x=x_col, y=y_col, hue=hue_col, data=df, palette=palette, s=60, edgecolor="white", linewidth=0.5
    )
    plt.title("Team-Season PCA (colored by cluster)")
    plt.xlabel("PC1")
    plt.ylabel("PC2")
    plt.legend(title="Cluster", loc="best")
    plt.tight_layout()
    plt.savefig(out_path, dpi=150)
    plt.close()
    return out_path


