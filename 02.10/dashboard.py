"""Build an interactive HTML dashboard from the star schema.

Reads the tables written by transform.py, joins the facts to the dimensions,
embeds the result in a single self-contained page and writes
output/dashboard.html. No internet connection or web server needed.

The page has two views: the satisfaction scores, and the complaints that
explain them. Every complaint carries the score the customer gave for the
aspect it is about, so the reason can be read next to its effect.

Run: uv run 02.10/dashboard.py
"""

import json
from pathlib import Path

import pandas as pd

HERE = Path(__file__).parent
OUTPUT = HERE / "output"
TEMPLATE = HERE / "dashboard_template.html"

ASPECTS = ["delivery_score", "courier_score", "condition_score", "service_score"]
ASPECT_LABELS = ["Delivery time", "Courier", "Parcel condition", "Customer service"]


def build_payload():
    fact = pd.read_csv(OUTPUT / "fact_survey.csv", parse_dates=["survey_date"])
    complaints = pd.read_csv(OUTPUT / "fact_complaint.csv", parse_dates=["complaint_date"])
    countries = pd.read_csv(OUTPUT / "dim_country.csv")
    products = pd.read_csv(OUTPUT / "dim_product.csv")
    cities = pd.read_csv(OUTPUT / "dim_city.csv")
    reasons = pd.read_csv(OUTPUT / "dim_reason.csv")

    fact = fact.dropna(subset=["survey_date"])
    complaints = complaints.dropna(subset=["complaint_date"])
    fact["month"] = fact["survey_date"].dt.strftime("%Y-%m")
    complaints["month"] = complaints["complaint_date"].dt.strftime("%Y-%m")
    months = sorted(set(fact["month"]) | set(complaints["month"]))

    # Dimensions become small lookup lists; facts only carry their position.
    country_index = {code: i for i, code in enumerate(countries["country_code"])}
    product_index = {key: i for i, key in enumerate(products["product_key"])}
    city_index = {key: i for i, key in enumerate(cities["city_key"])}
    reason_index = {key: i for i, key in enumerate(reasons["reason_key"])}
    month_index = {month: i for i, month in enumerate(months)}

    comments = sorted(fact["comment"].dropna().unique())
    comment_index = {text: i for i, text in enumerate(comments)}
    statuses = sorted(complaints["status"].dropna().unique())
    status_index = {name: i for i, name in enumerate(statuses)}
    channels = sorted(complaints["channel"].dropna().unique())
    channel_index = {name: i for i, name in enumerate(channels)}

    # A survey knows whether it ended in a complaint, so the page can compare
    # the satisfaction of the customers who complained with the rest.
    complained = fact["survey_id"].isin(complaints["survey_id"])

    def cell(value):
        return None if pd.isna(value) else round(float(value), 2)

    rows = [
        [
            country_index[row.country_code],
            product_index[row.product_key],
            city_index[row.city_key],
            month_index[row.month],
            cell(row.delivery_score),
            cell(row.courier_score),
            cell(row.condition_score),
            cell(row.service_score),
            cell(row.overall_score),
            comment_index.get(row.comment),
            int(row.complained),
        ]
        for row in fact.assign(complained=complained).itertuples()
    ]

    # Each complaint is linked back to the survey about the same parcel.
    linked = complaints.merge(
        fact[["survey_id", "overall_score"] + ASPECTS], on="survey_id", how="left"
    )
    linked["aspect"] = linked["reason_key"].map(dict(zip(reasons["reason_key"], reasons["aspect"])))
    linked["aspect_score"] = [
        getattr(row, row.aspect) if isinstance(row.aspect, str) else None
        for row in linked.itertuples()
    ]

    complaint_rows = [
        [
            country_index[row.country_code],
            product_index[row.product_key],
            city_index[row.city_key],
            month_index[row.month],
            reason_index[row.reason_key],
            cell(row.severity_level),
            status_index[row.status],
            channel_index[row.channel],
            cell(row.refund_eur),
            cell(row.handling_days),
            cell(row.aspect_score),
            cell(row.overall_score),
        ]
        for row in linked.itertuples()
    ]

    reason_list = [
        {
            "reason_key": row.reason_key,
            "reason_name": row.reason_name,
            "aspect": ASPECTS.index(row.aspect) if row.aspect in ASPECTS else None,
        }
        for row in reasons.itertuples()
    ]

    return {
        "countries": countries[["country_code", "country_name", "region"]].to_dict("records"),
        "products": products[["product_key", "product_name"]].to_dict("records"),
        "cities": cities[["city_key", "city_name", "country_code"]].to_dict("records"),
        "reasons": reason_list,
        "months": months,
        "comments": comments,
        "statuses": statuses,
        "channels": channels,
        "aspects": ASPECT_LABELS,
        "rows": rows,
        "complaints": complaint_rows,
    }


def main():
    payload = build_payload()
    html = TEMPLATE.read_text(encoding="utf-8").replace(
        "__DATA__", json.dumps(payload, ensure_ascii=False, separators=(",", ":"))
    )
    target = OUTPUT / "dashboard.html"
    target.write_text(html, encoding="utf-8")
    print(f"{len(payload['rows'])} surveys and {len(payload['complaints'])} complaints -> {target}")


if __name__ == "__main__":
    main()
