"""
Build an interactive HTML dashboard from the Global Video Game Sales dataset.
Fulfills Phase 15 Deliverable: Interactive HTML dashboard modeled after 02.10/output and second_proj/output.

Reads the cleaned dataset, computes executive KPIs, Market Power Indices (MPI),
genre-region affinities, cultural outliers, and embeds them into a single,
self-contained, compact HTML page: Fin_project/output/dashboard.html.
No web server or internet connection needed.

Run: uv run python Fin_project/dashboard.py
"""

import json
from pathlib import Path
import numpy as np
import pandas as pd

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
OUTPUT_DIR = BASE_DIR / "output"
TEMPLATE_PATH = BASE_DIR / "dashboard_template.html"
HTML_OUTPUT_PATH = OUTPUT_DIR / "dashboard.html"


def build_payload():
    csv_path = DATA_DIR / "vgsales.csv"
    df = pd.read_csv(csv_path)

    # Clean
    df = df.dropna(subset=["Year"]).reset_index(drop=True)
    df["Publisher"] = df["Publisher"].fillna("Unknown")
    df["Year"] = df["Year"].astype(int)

    region_cols = ["NA_Sales", "EU_Sales", "JP_Sales", "Other_Sales"]
    for c in region_cols + ["Global_Sales"]:
        df[c] = pd.to_numeric(df[c], errors="coerce").fillna(0.0)

    # 1. Global baseline Q
    total_reg = df[region_cols].sum()
    Q = (total_reg / total_reg.sum()).values

    # 2. Game-level Proportions and Divergence
    sales_mat = df[region_cols].values
    row_sums = sales_mat.sum(axis=1, keepdims=True)
    P = np.divide(sales_mat, row_sums, out=np.zeros_like(sales_mat), where=row_sums > 0)

    M = 0.5 * (P + Q)
    with np.errstate(divide="ignore", invalid="ignore"):
        kl_p_m = np.where(P > 0, P * np.log2(P / M), 0.0).sum(axis=1)
        kl_q_m = np.where(Q > 0, Q * np.log2(Q / M), 0.0).sum(axis=1)

    jsd = 0.5 * kl_p_m + 0.5 * kl_q_m
    df["RDS"] = np.sqrt(np.clip(jsd, 0, 1)) * 100

    # Cultural Specificity Score (CSS) & Outlier
    max_p = np.max(P, axis=1)
    df["CSS"] = np.clip((max_p - 0.25) / 0.75 * 100, 0, 100)

    is_outlier = []
    dom_territory = []
    dom_share = []
    reg_names = ["North America", "Europe", "Japan", "Other"]

    for p in P:
        max_idx = np.argmax(p)
        max_val = p[max_idx]
        other_vals = np.delete(p, max_idx)
        if max_val > 0.50 and (other_vals < 0.10).all():
            is_outlier.append(True)
            dom_territory.append(reg_names[max_idx])
            dom_share.append(round(max_val * 100, 1))
        else:
            is_outlier.append(False)
            dom_territory.append("None")
            dom_share.append(0.0)

    df["Is_Outlier"] = is_outlier
    df["Dominant_Territory"] = dom_territory
    df["Dominant_Share"] = dom_share

    # 3. Genres Payload
    genre_totals = df.groupby("Genre")["Global_Sales"].sum()
    genre_counts = df.groupby("Genre")["Name"].count()
    genres_payload = []
    for g, sales in genre_totals.sort_values(ascending=False).items():
        genres_payload.append({
            "name": g,
            "sales": round(float(sales), 2),
            "games": int(genre_counts[g]),
            "avg_sales": round(float(sales / genre_counts[g]), 2)
        })

    # 4. Platforms Payload
    plat_totals = df.groupby("Platform")["Global_Sales"].sum()
    plat_counts = df.groupby("Platform")["Name"].count()
    platforms_payload = []
    for p, sales in plat_totals.sort_values(ascending=False).items():
        platforms_payload.append({
            "name": p,
            "sales": round(float(sales), 2),
            "games": int(plat_counts[p])
        })

    # 5. Top 10 Best-Selling Games
    top10_df = df.nlargest(10, "Global_Sales")
    top10_payload = []
    for _, r in top10_df.iterrows():
        top10_payload.append({
            "name": r["Name"],
            "platform": r["Platform"],
            "year": int(r["Year"]),
            "genre": r["Genre"],
            "publisher": r["Publisher"],
            "na": round(float(r["NA_Sales"]), 2),
            "eu": round(float(r["EU_Sales"]), 2),
            "jp": round(float(r["JP_Sales"]), 2),
            "other": round(float(r["Other_Sales"]), 2),
            "global": round(float(r["Global_Sales"]), 2),
        })

    # 6. Publishers, MPI & Archetypes
    genre_medians = df.groupby("Genre")["Global_Sales"].median()
    df["Above_Genre_Median"] = df["Global_Sales"] > df["Genre"].map(genre_medians)

    pub_records = []
    for pub, group in df.groupby("Publisher"):
        tot_sales = group["Global_Sales"].sum()
        count = len(group)
        div = group["Genre"].nunique()
        
        reg_sales = group[region_cols].sum()
        reg_tot = reg_sales.sum()
        c_val = (reg_sales / reg_tot).std(ddof=1) if reg_tot > 0 else 0.5
        
        hit_rate = (group["Above_Genre_Median"].sum() / count) * 100
        
        g_sales = group.groupby("Genre")["Global_Sales"].sum()
        top_g = g_sales.idxmax()
        top_g_share = (g_sales.max() / tot_sales * 100) if tot_sales > 0 else 0
        
        pub_records.append({
            "name": pub,
            "sales": tot_sales,
            "games": count,
            "diversity": div,
            "consistency": c_val,
            "hit_rate": hit_rate,
            "top_genre": top_g,
            "top_genre_share": top_g_share
        })

    pdf = pd.DataFrame(pub_records)
    max_log_sales = np.log1p(pdf["sales"].max())
    pdf["S_norm"] = np.log1p(pdf["sales"]) / max_log_sales
    pdf["H_norm"] = pdf["hit_rate"] / 100.0
    pdf["D_norm"] = pdf["diversity"] / 12.0
    pdf["C_score"] = np.clip(1.0 - (pdf["consistency"] / 0.5), 0, 1)

    pdf["MPI"] = (0.35 * pdf["S_norm"] + 0.25 * pdf["H_norm"] + 0.20 * pdf["D_norm"] + 0.20 * pdf["C_score"]) * 100

    def classify_arch(row):
        if row["sales"] >= 200 and row["diversity"] >= 10 and row["top_genre_share"] < 50:
            return "Diversified Giant"
        elif (row["top_genre_share"] >= 60.0 or row["diversity"] <= 4) and (row["sales"] >= 8.0 or row["hit_rate"] >= 60.0):
            return "Genre Specialist"
        elif row["sales"] >= 40 and row["C_score"] < 0.55:
            return "Regional Powerhouse"
        elif row["sales"] >= 15.0 and row["diversity"] >= 5:
            return "Mainstream Mid-Tier"
        else:
            return "Long-Tail / Niche"

    pdf["Archetype"] = pdf.apply(classify_arch, axis=1)
    pdf = pdf.sort_values("MPI", ascending=False).reset_index(drop=True)
    pdf["Rank"] = pdf.index + 1

    publishers_payload = []
    for _, r in pdf.head(50).iterrows():
        publishers_payload.append({
            "rank": int(r["Rank"]),
            "name": r["name"],
            "sales": round(float(r["sales"]), 2),
            "games": int(r["games"]),
            "diversity": int(r["diversity"]),
            "hit_rate": round(float(r["hit_rate"]), 1),
            "mpi": round(float(r["MPI"]), 1),
            "archetype": r["Archetype"],
            "top_genre": r["top_genre"]
        })

    # 7. Official Genre Leaders (>30%)
    pub_genre_sales = df.groupby(["Publisher", "Genre"])["Global_Sales"].sum().reset_index()
    pub_genre_sales["Genre_Total"] = pub_genre_sales["Genre"].map(genre_totals)
    pub_genre_sales["Share"] = (pub_genre_sales["Global_Sales"] / pub_genre_sales["Genre_Total"]) * 100
    leaders = pub_genre_sales[pub_genre_sales["Share"] > 30.0].sort_values("Share", ascending=False)
    leaders_payload = []
    for _, r in leaders.iterrows():
        leaders_payload.append({
            "genre": r["Genre"],
            "publisher": r["Publisher"],
            "sales": round(float(r["Global_Sales"]), 2),
            "share": round(float(r["Share"]), 1)
        })

    # 8. Genre-Region Affinity Matrix
    genre_reg = df.groupby("Genre")[region_cols].sum()
    genre_dist = genre_reg.div(genre_reg.sum(axis=1), axis=0)
    affinity_mat = (genre_dist / Q) * 100
    affinity_payload = []
    for g, row in affinity_mat.iterrows():
        affinity_payload.append({
            "genre": g,
            "na": round(float(row["NA_Sales"]), 1),
            "eu": round(float(row["EU_Sales"]), 1),
            "jp": round(float(row["JP_Sales"]), 1),
            "other": round(float(row["Other_Sales"]), 1)
        })

    # 9. Low Divergence / Universal Hits
    low_div_df = df[df["Global_Sales"] >= 2.0].sort_values("RDS", ascending=True).head(15)
    low_div_payload = []
    for _, r in low_div_df.iterrows():
        low_div_payload.append({
            "name": r["Name"],
            "platform": r["Platform"],
            "genre": r["Genre"],
            "sales": round(float(r["Global_Sales"]), 2),
            "rds": round(float(r["RDS"]), 1)
        })

    # 10. Cultural Outliers (Major >= $1.0M)
    outliers_df = df[(df["Is_Outlier"]) & (df["Global_Sales"] >= 1.0)].sort_values("Global_Sales", ascending=False).head(40)
    outliers_payload = []
    for _, r in outliers_df.iterrows():
        outliers_payload.append({
            "name": r["Name"],
            "platform": r["Platform"],
            "genre": r["Genre"],
            "publisher": r["Publisher"],
            "territory": r["Dominant_Territory"],
            "territory_share": round(float(r["Dominant_Share"]), 1),
            "sales": round(float(r["Global_Sales"]), 2),
            "css": round(float(r["CSS"]), 1)
        })

    # 11. All Major Games for Explorer (Sales >= $1.0M, ~2,000 titles)
    major_games = df[df["Global_Sales"] >= 1.0].sort_values("Global_Sales", ascending=False)
    major_games_payload = []
    for _, r in major_games.iterrows():
        major_games_payload.append({
            "name": r["Name"],
            "platform": r["Platform"],
            "year": int(r["Year"]),
            "genre": r["Genre"],
            "publisher": r["Publisher"],
            "na": round(float(r["NA_Sales"]), 2),
            "eu": round(float(r["EU_Sales"]), 2),
            "jp": round(float(r["JP_Sales"]), 2),
            "global": round(float(r["Global_Sales"]), 2),
            "rds": round(float(r["RDS"]), 1)
        })

    return {
        "genres": genres_payload,
        "platforms": platforms_payload,
        "top10_games": top10_payload,
        "publishers": publishers_payload,
        "genre_leaders": leaders_payload,
        "affinity_matrix": affinity_payload,
        "low_divergence_games": low_div_payload,
        "cultural_outliers": outliers_payload,
        "all_major_games": major_games_payload
    }


def main():
    print("Building analytical dashboard payload...")
    payload = build_payload()

    print(f"Reading template from {TEMPLATE_PATH}...")
    with open(TEMPLATE_PATH, "r", encoding="utf-8") as f:
        template = f.read()

    payload_json = json.dumps(payload, separators=(",", ":"))
    script_injection = f"const PAYLOAD = {payload_json};"

    html = template.replace("/* __PAYLOAD_PLACEHOLDER__ */", script_injection)

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    with open(HTML_OUTPUT_PATH, "w", encoding="utf-8") as f:
        f.write(html)

    print(f"✅ Dashboard written to {HTML_OUTPUT_PATH} ({len(html):,} bytes)")


if __name__ == "__main__":
    main()
