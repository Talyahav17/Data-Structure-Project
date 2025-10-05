# Team Season Insights Summary

## 🏀 1. Introduction
This report summarizes the results of analysis of team insights by seasons and playing styles.
The stage was based on files `team_season_features.csv`, `team_season_clusters.csv`, and `cluster_style_labels.csv`.

---

## 📊 2. General League Trends
- **Overall TS% improvement:** Analysis of 256 team-metric combinations shows varying trends between teams
- **Large gaps in game pace:** Cluster 2 shows average pace_proxy of 83.77 compared to 3.07 in Cluster 0
- **High efficiency variance:** TS% ranges from 0.000 to 60.941, indicating significant gaps between seasons

---

## 🧮 3. Cluster Comparison (Styles)
| Cluster | Style Name | Team Count | Avg TS% | Avg eFG% | Pace Proxy | Key Characteristics |
|---------|------------|------------|---------|----------|------------|---------------------|
| 0 | Balanced | 331 | 5.04 | 0.57 | 3.07 | Slow game, moderate efficiency |
| 1 | Balanced | 22 | 5.16 | 15.20 | 3.21 | Slow game, high efficiency |
| 2 | Balanced | 1174 | 0.54 | 0.50 | 83.77 | Fast game, low efficiency |

---

## 📈 4. Notable Teams for Improvement / Decline
### 📈 Improvements
- **Golden State Warriors** — increase of +0.569 in TS% over 79 seasons
- **Memphis Grizzlies** — improvement of +0.128 in TS% over 29 seasons
- **Minnesota Timberwolves** — improvement of +0.098 in TS% over 36 seasons

### 📉 Declines
- **Boston Celtics** — decline of -31.609 in TS% over 79 seasons
- **Atlanta Hawks** — decline of -8.018 in TS% over 74 seasons
- **Sacramento Kings** — decline of -4.567 in TS% over 53 seasons

---

## ⚠️ 5. Outliers and Deviations
- Found 42 statistical outliers (Z-score > 2.5) across different metrics
- Large gaps in early historical data (seasons 1946-1950) affect the analysis
- Cluster 2 represents 76.9% of the data (1174/1527), indicating dominance of one playing style

---

## 🧭 6. Conclusions and Summary
- **Cluster 2** (Balanced) dominates most data with high pace_proxy (83.77) but low TS% (0.54)
- **Historical gaps** in early data affect trend analysis
- **Golden State Warriors** show the greatest improvement in TS% over time
- **Boston Celtics** show dramatic decline in TS%, likely due to changes in historical data

---

## 📚 7. Output Files
- `insights_trends.csv` — seasonal trends and slope for each team (256 records)
- `insights_clusters.csv` — cluster comparison table (3 clusters)
- `insights_outliers.csv` — outliers (42 outliers)
- `insights_leaders.csv` — top 10 for each metric (80 records)

---

## 🔍 8. Recommendations for Continuation
1. **Historical data cleaning** — check and clean early data (1946-1960)
2. **Periodic analysis** — divide analysis into periods (historical, modern)
3. **Data enrichment** — add win/loss metrics for comprehensive analysis
4. **External validation** — compare results with official NBA sources
