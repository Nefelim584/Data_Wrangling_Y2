"""Build a star schema out of the raw country survey and complaint files.

Every country is read into the same columns, then linked to the master data
in reference/ so that all five branches share one product and country key.
The complaints say why a customer was unhappy, so they carry the same keys as
the surveys plus the parcel they are about.

Outputs in output/:
    dim_country.csv       one row per branch            (from the master data)
    dim_product.csv       one row per global product    (from the master data)
    dim_reason.csv        one row per complaint reason  (from the master data)
    dim_city.csv          one row per city, linked to a country
    fact_survey.csv       one row per survey, linked to the dimensions
    fact_complaint.csv    one row per complaint, linked to the dimensions
                          and to the survey about the same parcel
    surveys_clean.csv     the survey facts already joined to the dimensions
    complaints_clean.csv  the complaint facts already joined to the dimensions

Run: uv run 02.10/transform.py
"""

import json
from pathlib import Path

import pandas as pd

HERE = Path(__file__).parent
DATA = HERE / "data"
REFERENCE = HERE / "reference"
OUTPUT = HERE / "output"

RAW_COLUMNS = [
    "survey_id",
    "country_code",
    "survey_date",
    "source_city",
    "source_product_code",
    "delivery_score",
    "courier_score",
    "condition_score",
    "service_score",
    "overall_score",
    "comment",
]

SCORE_COLUMNS = ["delivery_score", "courier_score", "condition_score", "service_score"]

COMPLAINT_COLUMNS = [
    "complaint_id",
    "country_code",
    "parcel_id",
    "survey_id",
    "complaint_date",
    "source_city",
    "source_product_code",
    "source_reason_code",
    "source_severity",
    "source_status",
    "source_channel",
    "handling_days",
    "refund_amount",
    "description",
]

# Spain answers with words instead of numbers.
SPANISH_SCALE = {"Muy bajo": 1, "Bajo": 2, "Medio": 3, "Alto": 4, "Muy alto": 5}

# Morocco only collects free text, in French, Arabic and Darija.
MOROCCAN_COMMENTS = {
    "Très satisfait, livraison à l'heure": 5,
    "wsel f lwe9t, merci": 5,
    "وصل فالوقت وكلشي مزيان": 5,
    "kolchi mzyan, livreur محترم": 5,
    "الكولي وصل مزيان والخدمة زوينة": 5,
    "RAS, tout s'est bien passé": 4,
    "Livraison en retard mais livreur professionnel": 3,
    "livraison mzyana walakin retard bzaf": 3,
    "التوصيل كان مزيان ولكن وصل متأخر": 3,
    "Service client difficile à joindre": 2,
    "service client ma kayjawbch": 2,
    "خدمة الزبناء ما كيجاوبوش": 2,
    "colis m5ser chwya": 2,
    "الكرتونة مخسرة شوية": 2,
    "Colis arrivé endommagé": 1,
}


def read_reference(name):
    return pd.read_csv(REFERENCE / name, comment="#")


def normalise_code(codes):
    """Trim, uppercase and unify separators so dirty codes still match."""
    return codes.astype("string").str.strip().str.upper().str.replace("-", "_")


def normalise_value(values):
    """Trim and uppercase a written answer so dirty wording still matches."""
    return values.astype("string").str.strip().str.upper()


def to_amount(values):
    """Read a refund, whatever decimal separator the branch typed."""
    text = values.astype("string").str.strip().str.replace(",", ".")
    return pd.to_numeric(text, errors="coerce")


def to_date(values, formats):
    """Parse dates, trying each format the country uses."""
    parsed = pd.to_datetime(values, format=formats[0], errors="coerce")
    for fmt in formats[1:]:
        parsed = parsed.fillna(pd.to_datetime(values, format=fmt, errors="coerce"))
    return parsed


def to_score(values, scale_max=5):
    """Turn a rating into a number out of 5."""
    return pd.to_numeric(values, errors="coerce") * 5 / scale_max


def load_france():
    raw = pd.read_excel(DATA / "france_satisfaction_raw.xlsx")
    return pd.DataFrame({
        "survey_id": raw["id_enquete"],
        "country_code": "FR",
        "survey_date": to_date(raw["date_reponse"], ["%d/%m/%Y", "%Y-%m-%d"]),
        "source_city": raw["ville"],
        "source_product_code": raw["code_produit"],
        "delivery_score": to_score(raw["delai_livraison"]),
        "courier_score": to_score(raw["relation_livreur"]),
        "condition_score": to_score(raw["etat_colis"]),
        "service_score": to_score(raw["service_client"]),
        "overall_score": to_score(raw["satisfaction_globale"]),
        "comment": raw["commentaire"],
    })


def load_spain():
    raw = pd.json_normalize(json.loads((DATA / "spain_satisfaction_raw.json").read_text()))
    words = raw[["satisfaction.entrega", "satisfaction.repartidor", "satisfaction.estado",
                 "satisfaction.soporte", "satisfaction.global"]].map(SPANISH_SCALE.get)
    return pd.DataFrame({
        "survey_id": raw["survey_id"],
        "country_code": "ES",
        "survey_date": to_date(raw["survey_date"], ["%Y-%m-%d", "%d-%m-%Y"]),
        "source_city": raw["parcel.city"],
        "source_product_code": raw["parcel.product_code"],
        "delivery_score": to_score(words["satisfaction.entrega"]),
        "courier_score": to_score(words["satisfaction.repartidor"]),
        "condition_score": to_score(words["satisfaction.estado"]),
        "service_score": to_score(words["satisfaction.soporte"]),
        "overall_score": to_score(words["satisfaction.global"]),
        "comment": raw["comentario"],
    })


def load_germany():
    raw = pd.read_csv(DATA / "germany_satisfaction_raw.csv", sep=";")
    return pd.DataFrame({
        "survey_id": raw["umfrage_id"],
        "country_code": "DE",
        "survey_date": to_date(raw["datum"], ["%d.%m.%Y"]),
        "source_city": raw["stadt"],
        "source_product_code": raw["produkt_code"],
        "delivery_score": to_score(raw["lieferzeit"]),
        "courier_score": to_score(raw["zusteller"]),
        "condition_score": to_score(raw["paketzustand"]),
        "service_score": to_score(raw["kundenservice"]),
        "overall_score": to_score(raw["gesamtzufriedenheit"]),
        "comment": None,
    })


def load_canada():
    raw = pd.read_csv(DATA / "canada_satisfaction_raw.csv")
    return pd.DataFrame({
        "survey_id": raw["survey_id"],
        "country_code": "CA",
        "survey_date": to_date(raw["survey_date"], ["%Y-%m-%d", "%m/%d/%Y"]),
        "source_city": raw["city"],
        "source_product_code": raw["product_code"],
        "delivery_score": to_score(raw["delivery_time_score"], scale_max=10),
        "courier_score": to_score(raw["courier_score"], scale_max=10),
        "condition_score": to_score(raw["parcel_condition_score"], scale_max=10),
        "service_score": to_score(raw["customer_service_score"], scale_max=10),
        "overall_score": to_score(raw["overall_score"], scale_max=10),
        "comment": raw["comment"],
    })


def load_morocco():
    raw = pd.read_csv(DATA / "morocco_satisfaction_raw.txt", sep="|")
    comments = raw["commentaire_client"].str.strip()
    return pd.DataFrame({
        "survey_id": raw["id_enquete"],
        "country_code": "MA",
        "survey_date": to_date(raw["date_reponse"], ["%d/%m/%Y"]),
        "source_city": raw["ville"],
        "source_product_code": raw["code_produit"],
        "delivery_score": None,
        "courier_score": None,
        "condition_score": None,
        "service_score": None,
        "overall_score": to_score(comments.map(MOROCCAN_COMMENTS)),
        "comment": comments,
    })


def load_complaints_france():
    raw = pd.read_excel(DATA / "france_complaints_raw.xlsx")
    return pd.DataFrame({
        "complaint_id": raw["id_reclamation"],
        "country_code": "FR",
        "parcel_id": raw["numero_colis"],
        "survey_id": raw["id_enquete"],
        "complaint_date": to_date(raw["date_reclamation"], ["%d/%m/%Y", "%Y-%m-%d"]),
        "source_city": raw["ville"],
        "source_product_code": raw["code_produit"],
        "source_reason_code": raw["motif_code"],
        "source_severity": raw["gravite"],
        "source_status": raw["statut"],
        "source_channel": raw["canal"],
        "handling_days": raw["delai_traitement_jours"],
        "refund_amount": to_amount(raw["montant_remboursement"]),
        "description": raw["description"],
    })


def load_complaints_spain():
    raw = pd.json_normalize(json.loads((DATA / "spain_complaints_raw.json").read_text()))
    return pd.DataFrame({
        "complaint_id": raw["reclamacion_id"],
        "country_code": "ES",
        "parcel_id": raw["envio.id"],
        "survey_id": raw["envio.encuesta_id"],
        "complaint_date": to_date(raw["fecha"], ["%Y-%m-%d", "%d-%m-%Y"]),
        "source_city": raw["envio.ciudad"],
        "source_product_code": raw["envio.codigo_producto"],
        "source_reason_code": raw["motivo.codigo"],
        "source_severity": raw["gravedad"],
        "source_status": raw["estado"],
        "source_channel": raw["canal"],
        "handling_days": raw["dias_gestion"],
        "refund_amount": to_amount(raw["importe_reembolso"]),
        "description": raw["motivo.descripcion"],
    })


def load_complaints_germany():
    raw = pd.read_csv(DATA / "germany_complaints_raw.csv", sep=";")
    return pd.DataFrame({
        "complaint_id": raw["beschwerde_id"],
        "country_code": "DE",
        "parcel_id": raw["paket_nr"],
        "survey_id": raw["umfrage_id"],
        "complaint_date": to_date(raw["datum"], ["%d.%m.%Y"]),
        "source_city": raw["stadt"],
        "source_product_code": raw["produkt_code"],
        "source_reason_code": raw["grund_code"],
        "source_severity": raw["schweregrad"],
        "source_status": raw["status"],
        "source_channel": raw["kanal"],
        "handling_days": raw["bearbeitungstage"],
        "refund_amount": to_amount(raw["erstattung_eur"]),
        "description": raw["beschreibung"],
    })


def load_complaints_canada():
    # One ticket per line, so the file is read line by line.
    lines = (DATA / "canada_complaints_raw.jsonl").read_text().splitlines()
    raw = pd.DataFrame([json.loads(line) for line in lines if line.strip()])
    return pd.DataFrame({
        "complaint_id": raw["complaint_id"],
        "country_code": "CA",
        "parcel_id": raw["parcel_id"],
        "survey_id": raw["survey_id"],
        "complaint_date": to_date(raw["created_at"], ["%Y-%m-%d", "%m/%d/%Y"]),
        "source_city": raw["city"],
        "source_product_code": raw["product_code"],
        "source_reason_code": raw["reason_code"],
        "source_severity": raw["severity"],
        "source_status": raw["status"],
        "source_channel": raw["channel"],
        "handling_days": raw["handling_days"],
        "refund_amount": to_amount(raw["refund_cad"]),
        "description": raw["description"],
    })


def load_complaints_morocco():
    raw = pd.read_csv(DATA / "morocco_complaints_raw.txt", sep="|")
    return pd.DataFrame({
        "complaint_id": raw["id_reclamation"],
        "country_code": "MA",
        "parcel_id": raw["numero_colis"],
        "survey_id": raw["id_enquete"],
        "complaint_date": to_date(raw["date_reclamation"], ["%d/%m/%Y"]),
        "source_city": raw["ville"],
        "source_product_code": raw["code_produit"],
        "source_reason_code": raw["motif_saisi"],
        # The branch grades nothing: severity stays empty for Morocco.
        "source_severity": None,
        "source_status": raw["statut"],
        "source_channel": raw["canal"],
        "handling_days": None,
        "refund_amount": to_amount(raw["montant_mad"]),
        "description": raw["description"],
    })


def add_product_key(surveys):
    """Link every survey to the global product reference."""
    mapping = read_reference("product_code_mapping.csv")
    surveys["source_product_code"] = normalise_code(surveys["source_product_code"])
    surveys = surveys.merge(
        mapping.rename(columns={"source_code": "source_product_code"}),
        on=["country_code", "source_product_code"],
        how="left",
    )
    surveys["product_key"] = surveys["product_key"].fillna("PRD_UNK")
    return surveys


def add_city_key(surveys):
    """Clean city names and give each one a key inside its country."""
    aliases = read_reference("city_aliases.csv")
    surveys["city_name"] = surveys["source_city"].astype("string").str.strip().str.title()
    surveys = surveys.merge(
        aliases.rename(columns={"source_city": "city_name", "city_name": "alias_target"}),
        on=["country_code", "city_name"],
        how="left",
    )
    surveys["city_name"] = surveys["alias_target"].fillna(surveys["city_name"]).fillna("Unknown")
    surveys["city_key"] = surveys["country_code"] + "_" + surveys["city_name"].str.upper()
    return surveys.drop(columns="alias_target")


def add_reason_key(complaints):
    """Link every local complaint code to the global reason reference."""
    mapping = read_reference("complaint_reason_mapping.csv")
    complaints["source_reason_code"] = normalise_code(complaints["source_reason_code"])
    complaints = complaints.merge(
        mapping.rename(columns={"source_code": "source_reason_code"}),
        on=["country_code", "source_reason_code"],
        how="left",
    )
    complaints["reason_key"] = complaints["reason_key"].fillna("RSN_UNK")
    return complaints


def add_mapped_values(complaints):
    """Replace the local wording of severity, status and channel by ours."""
    mapping = read_reference("complaint_value_mapping.csv")
    mapping["source_value"] = normalise_value(mapping["source_value"])
    for field, source, target in [
        ("severity", "source_severity", "severity_level"),
        ("status", "source_status", "status"),
        ("channel", "source_channel", "channel"),
    ]:
        column = mapping.loc[mapping["field"] == field, ["country_code", "source_value", "target_value"]]
        complaints[target] = complaints.merge(
            column.rename(columns={"source_value": source, "target_value": target}),
            on=["country_code", source],
            how="left",
        )[target].values
    complaints["severity_level"] = pd.to_numeric(complaints["severity_level"], errors="coerce")
    return complaints


def build_surveys():
    """Every survey file in one frame, with scores on the same 1-5 scale."""
    surveys = pd.concat(
        [load_france(), load_spain(), load_germany(), load_canada(), load_morocco()],
        ignore_index=True,
    )[RAW_COLUMNS]

    surveys["survey_id"] = surveys["survey_id"].astype("string").str.strip()
    surveys["comment"] = surveys["comment"].astype("string").str.strip().replace("", None)

    # Where a country did not give an overall score, average the four detail scores.
    surveys["overall_score"] = surveys["overall_score"].fillna(
        surveys[SCORE_COLUMNS].mean(axis=1)
    )
    rated = SCORE_COLUMNS + ["overall_score"]
    surveys[rated] = surveys[rated].clip(1, 5).round(2)

    surveys = add_product_key(surveys)
    surveys = add_city_key(surveys)
    return surveys.drop_duplicates(subset="survey_id").sort_values("survey_date")


def build_complaints():
    """Every complaint file in one frame, with the same keys as the surveys."""
    complaints = pd.concat(
        [
            load_complaints_france(),
            load_complaints_spain(),
            load_complaints_germany(),
            load_complaints_canada(),
            load_complaints_morocco(),
        ],
        ignore_index=True,
    )[COMPLAINT_COLUMNS]

    for column in ["complaint_id", "parcel_id", "survey_id", "description"]:
        complaints[column] = complaints[column].astype("string").str.strip()
    complaints["source_severity"] = normalise_value(complaints["source_severity"])
    complaints["source_status"] = normalise_value(complaints["source_status"])
    complaints["source_channel"] = normalise_value(complaints["source_channel"])

    complaints = add_reason_key(complaints)
    complaints = add_mapped_values(complaints)
    complaints = add_product_key(complaints)
    complaints = add_city_key(complaints)

    # Refunds are paid in the local currency, so convert them for comparison.
    rates = read_reference("country_master.csv")[["country_code", "currency", "eur_rate"]]
    complaints = complaints.merge(rates, on="country_code", how="left")
    complaints["refund_eur"] = (complaints["refund_amount"] * complaints["eur_rate"]).round(2)

    complaints = complaints.drop_duplicates(subset="complaint_id")
    return complaints.sort_values("complaint_date")


def main():
    surveys = build_surveys()
    complaints = build_complaints()
    rated = SCORE_COLUMNS + ["overall_score"]

    dim_country = read_reference("country_master.csv")
    dim_product = read_reference("product_master.csv")
    dim_reason = read_reference("complaint_reason_master.csv")
    dim_city = (
        pd.concat([
            surveys[["city_key", "country_code", "city_name"]],
            complaints[["city_key", "country_code", "city_name"]],
        ])
        .dropna()
        .drop_duplicates()
        .sort_values("city_key")
    )
    fact_survey = surveys[
        ["survey_id", "country_code", "city_key", "product_key", "survey_date"]
        + rated
        + ["comment"]
    ]
    fact_complaint = complaints[
        ["complaint_id", "country_code", "city_key", "product_key", "reason_key",
         "survey_id", "parcel_id", "complaint_date", "severity_level", "status",
         "channel", "handling_days", "refund_amount", "currency", "refund_eur",
         "description"]
    ]

    OUTPUT.mkdir(exist_ok=True)
    dim_country.to_csv(OUTPUT / "dim_country.csv", index=False)
    dim_product.to_csv(OUTPUT / "dim_product.csv", index=False)
    dim_reason.to_csv(OUTPUT / "dim_reason.csv", index=False)
    dim_city.to_csv(OUTPUT / "dim_city.csv", index=False)
    fact_survey.to_csv(OUTPUT / "fact_survey.csv", index=False)
    fact_complaint.to_csv(OUTPUT / "fact_complaint.csv", index=False)

    joined = (
        fact_survey
        .merge(dim_country[["country_code", "country_name", "region"]], on="country_code")
        .merge(dim_product[["product_key", "product_name"]], on="product_key")
        .merge(dim_city[["city_key", "city_name"]], on="city_key", how="left")
    )
    joined.to_csv(OUTPUT / "surveys_clean.csv", index=False)

    # The complaint view also carries the score the customer gave for the
    # aspect it is about, so the reason can be read next to its effect.
    complaints_joined = (
        fact_complaint
        .merge(dim_country[["country_code", "country_name", "region"]], on="country_code")
        .merge(dim_product[["product_key", "product_name"]], on="product_key")
        .merge(dim_reason[["reason_key", "reason_name", "aspect"]], on="reason_key")
        .merge(dim_city[["city_key", "city_name"]], on="city_key", how="left")
        .merge(fact_survey[["survey_id"] + rated], on="survey_id", how="left")
    )
    complaints_joined["aspect_score"] = [
        getattr(row, row.aspect) if isinstance(row.aspect, str) else None
        for row in complaints_joined.itertuples()
    ]
    complaints_joined.to_csv(OUTPUT / "complaints_clean.csv", index=False)

    print(f"{len(fact_survey)} surveys, {len(fact_complaint)} complaints -> {OUTPUT}")
    print(f"unmapped products: {(fact_survey['product_key'] == 'PRD_UNK').sum()}, "
          f"unmapped reasons: {(fact_complaint['reason_key'] == 'RSN_UNK').sum()}, "
          f"complaints without a survey: {fact_complaint['survey_id'].isna().sum()}")
    print(joined.groupby("country_name")["overall_score"].agg(["count", "mean"]).round(2))
    print(complaints_joined.groupby("reason_name")
          .agg(complaints=("complaint_id", "count"),
               aspect_score=("aspect_score", "mean"),
               refund_eur=("refund_eur", "sum"))
          .sort_values("complaints", ascending=False).round(2))


if __name__ == "__main__":
    main()
