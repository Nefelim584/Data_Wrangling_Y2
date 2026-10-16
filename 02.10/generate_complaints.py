"""Generate the five raw complaint files that sit behind the survey scores.

Each branch runs its own ticketing tool, so the files are as mixed as the survey
files: Excel in France, JSON in Spain, semicolon CSV in Germany, JSON Lines in
Canada and pipe text in Morocco, each with its own language, codes and dirt.

Every complaint is built from an existing survey, so it stays inside the master
data: the reason codes come from reference/complaint_reason_mapping.csv, the
wording of severity, status and channel from reference/complaint_value_mapping.csv,
and the parcel, city and product code are the ones the survey already carries.
A complaint is drawn for a survey with a probability that grows as the score
drops, and its reason is taken from the comment, or from the aspect the customer
rated worst. That is what makes the complaints explain the dissatisfaction.

Run: uv run 02.10/generate_complaints.py
"""

import json
import random
from pathlib import Path

import pandas as pd

import transform

HERE = Path(__file__).parent
DATA = HERE / "data"
REFERENCE = HERE / "reference"

SEED = 20251002

# A survey only turns into a complaint when the customer was unhappy.
COMPLAINT_RATE = {1.0: 0.80, 2.0: 0.46, 3.0: 0.20, 4.0: 0.07, 5.0: 0.02}

# Which reasons live under which aspect, and how often they occur there.
REASON_WEIGHTS = {
    "delivery_score": {"RSN_LATE": 0.60, "RSN_MISSED": 0.28, "RSN_LOST": 0.12},
    "courier_score": {"RSN_RUDE": 0.40, "RSN_NOCALL": 0.38, "RSN_WRONGADDR": 0.22},
    "condition_score": {"RSN_DAMAGE": 0.58, "RSN_MISSING": 0.27, "RSN_COLDCHAIN": 0.15},
    "service_score": {"RSN_NOREPLY": 0.50, "RSN_REFUND": 0.30, "RSN_WRONGINFO": 0.20},
}

# The product explains part of the reason: fragile parcels break, cold chain
# only fails on refrigerated ones, valuables get lost and claimed.
PRODUCT_BIAS = {
    "PRD_FRG": {"RSN_DAMAGE": 2.5, "RSN_MISSING": 1.3},
    "PRD_CLD": {"RSN_COLDCHAIN": 9.0, "RSN_DAMAGE": 0.6},
    "PRD_VAL": {"RSN_LOST": 3.0, "RSN_REFUND": 1.8, "RSN_MISSING": 1.5},
    "PRD_LRG": {"RSN_MISSED": 1.8, "RSN_DAMAGE": 1.4},
    "PRD_EXP": {"RSN_LATE": 1.8},
}

# Refrigerated parcels never fail cold chain when they are not refrigerated.
COLD_ONLY = "RSN_COLDCHAIN"

# When the customer already said why in the survey, the complaint says the same.
COMMENT_REASONS = [
    ("endommag", "RSN_DAMAGE"),
    ("dañado", "RSN_DAMAGE"),
    ("damaged", "RSN_DAMAGE"),
    ("m5ser", "RSN_DAMAGE"),
    ("مخسرة", "RSN_DAMAGE"),
    ("retard", "RSN_LATE"),
    ("tardía", "RSN_LATE"),
    ("late", "RSN_LATE"),
    ("متأخر", "RSN_LATE"),
    ("service client", "RSN_NOREPLY"),
    ("kayjawbch", "RSN_NOREPLY"),
    ("كيجاوبوش", "RSN_NOREPLY"),
]

TEXTS = {
    "en": {
        "RSN_LATE": "Parcel arrived three days after the promised date",
        "RSN_MISSED": "Courier never showed up during the booked time slot",
        "RSN_LOST": "Parcel never arrived and tracking stopped updating",
        "RSN_RUDE": "The courier was rude at the door",
        "RSN_NOCALL": "Courier left without ringing the bell",
        "RSN_WRONGADDR": "Parcel was dropped at the wrong address",
        "RSN_DAMAGE": "Box arrived crushed and the contents were broken",
        "RSN_COLDCHAIN": "Refrigerated parcel arrived warm",
        "RSN_MISSING": "Two items were missing from the parcel",
        "RSN_NOREPLY": "Nobody answers the customer service line",
        "RSN_REFUND": "My claim has been open for weeks without a refund",
        "RSN_WRONGINFO": "Support gave me a delivery date that was wrong",
        "RSN_FEES": "I was charged extra fees nobody announced",
        "RSN_UNK": "Complaint recorded without a reason",
    },
    "fr": {
        "RSN_LATE": "Colis livré avec trois jours de retard",
        "RSN_MISSED": "Le livreur n'est jamais passé sur le créneau réservé",
        "RSN_LOST": "Colis jamais arrivé, le suivi est bloqué",
        "RSN_RUDE": "Livreur désagréable au moment de la remise",
        "RSN_NOCALL": "Le livreur est reparti sans sonner",
        "RSN_WRONGADDR": "Colis déposé à la mauvaise adresse",
        "RSN_DAMAGE": "Carton écrasé, contenu cassé",
        "RSN_COLDCHAIN": "Colis réfrigéré livré tiède",
        "RSN_MISSING": "Deux articles manquent dans le colis",
        "RSN_NOREPLY": "Impossible de joindre le service client",
        "RSN_REFUND": "Dossier de remboursement sans réponse depuis des semaines",
        "RSN_WRONGINFO": "Le service client m'a donné une mauvaise date",
        "RSN_FEES": "Des frais supplémentaires qui n'étaient pas annoncés",
        "RSN_UNK": "Réclamation enregistrée sans motif",
    },
    "es": {
        "RSN_LATE": "El paquete llegó con tres días de retraso",
        "RSN_MISSED": "El repartidor no vino en la franja acordada",
        "RSN_LOST": "El paquete nunca llegó y el seguimiento no avanza",
        "RSN_RUDE": "El repartidor fue muy maleducado en la entrega",
        "RSN_NOCALL": "El repartidor se fue sin llamar al timbre",
        "RSN_WRONGADDR": "Entregaron el paquete en una dirección equivocada",
        "RSN_DAMAGE": "La caja llegó aplastada y el contenido roto",
        "RSN_COLDCHAIN": "El envío refrigerado llegó caliente",
        "RSN_MISSING": "Faltan dos artículos dentro del paquete",
        "RSN_NOREPLY": "Nadie contesta en atención al cliente",
        "RSN_REFUND": "Llevo semanas esperando el reembolso",
        "RSN_WRONGINFO": "Me dieron una fecha de entrega incorrecta",
        "RSN_FEES": "Me cobraron gastos que nadie me avisó",
        "RSN_UNK": "Reclamación sin motivo indicado",
    },
    "de": {
        "RSN_LATE": "Paket kam drei Tage zu spät",
        "RSN_MISSED": "Zusteller ist im gebuchten Zeitfenster nicht erschienen",
        "RSN_LOST": "Paket nie angekommen, Sendungsverfolgung steht still",
        "RSN_RUDE": "Der Zusteller war an der Tür unhöflich",
        "RSN_NOCALL": "Zusteller ist ohne zu klingeln wieder weggefahren",
        "RSN_WRONGADDR": "Paket wurde an der falschen Adresse abgegeben",
        "RSN_DAMAGE": "Karton eingedrückt, Inhalt beschädigt",
        "RSN_COLDCHAIN": "Kühlsendung kam warm an",
        "RSN_MISSING": "Zwei Artikel fehlen im Paket",
        "RSN_NOREPLY": "Der Kundenservice ist nicht erreichbar",
        "RSN_REFUND": "Erstattung wird seit Wochen nicht bearbeitet",
        "RSN_WRONGINFO": "Falsche Auskunft zum Liefertermin erhalten",
        "RSN_FEES": "Unangekündigte Zusatzkosten berechnet",
        "RSN_UNK": "Beschwerde ohne Grund erfasst",
    },
    "darija": {
        "RSN_LATE": "lkolis wsel m3attel b 3 iyam",
        "RSN_MISSED": "livreur ma jach f lwe9t li tfa9na 3lih",
        "RSN_LOST": "lkolis day3, tracking ma kaytbedelch",
        "RSN_RUDE": "livreur hder m3aya b tari9a khayba",
        "RSN_NOCALL": "livreur ma3ayetch 3liya o mcha",
        "RSN_WRONGADDR": "khellaw lkolis f 3nwan akhor",
        "RSN_DAMAGE": "lkarton m5ser o li dakhel therres",
        "RSN_COLDCHAIN": "lkolis dyal lbred wsel skhoun",
        "RSN_MISSING": "na9ss jouj dyal lhwayj mn lkolis",
        "RSN_NOREPLY": "service client ma kayjawbch f telephone",
        "RSN_REFUND": "3andi chi chhar katsenna flousi o walo",
        "RSN_WRONGINFO": "3tawni date dyal livraison ghalta",
        "RSN_FEES": "khellsouni frais zayda bla ma y3elmoni",
        "RSN_UNK": "chikaya msejla bla sbab",
    },
    "ar": {
        "RSN_LATE": "الطرد وصل متأخر بثلاثة أيام",
        "RSN_MISSED": "موزع الطرود لم يأت في الموعد المتفق عليه",
        "RSN_LOST": "الطرد لم يصل أبدا والتتبع متوقف",
        "RSN_RUDE": "موزع الطرود تعامل معي بطريقة غير لائقة",
        "RSN_NOCALL": "الموزع غادر دون أن يتصل بي",
        "RSN_WRONGADDR": "تم تسليم الطرد في عنوان خاطئ",
        "RSN_DAMAGE": "الكرتونة مخسرة والمحتوى مكسور",
        "RSN_COLDCHAIN": "الطرد المبرد وصل ساخنا",
        "RSN_MISSING": "ناقص منتجان داخل الطرد",
        "RSN_NOREPLY": "خدمة الزبناء ما كيجاوبوش في الهاتف",
        "RSN_REFUND": "طلب الاسترجاع لم يعالج منذ أسابيع",
        "RSN_WRONGINFO": "أعطوني تاريخ تسليم خاطئ",
        "RSN_FEES": "تم احتساب رسوم إضافية دون إخبارنا",
        "RSN_UNK": "شكاية مسجلة بدون سبب",
    },
}

# Severity level 1-4 written the way each branch writes it.
LOCAL_SEVERITY = {
    "FR": {1: "Mineur", 2: "Moyen", 3: "Majeur", 4: "Critique"},
    "ES": {1: "Baja", 2: "Media", 3: "Alta", 4: "Crítica"},
    "DE": {1: "1", 2: "2", 3: "2", 4: "3"},
    "CA": {1: "1", 2: "2", 3: "3", 4: "5"},
}

LOCAL_STATUS = {
    "FR": {"OPEN": "Ouvert", "IN_PROGRESS": "En cours", "RESOLVED": "Résolu",
           "ESCALATED": "Escaladé", "CLOSED": "Clos"},
    "ES": {"OPEN": "Pendiente", "IN_PROGRESS": "En curso", "RESOLVED": "Resuelto",
           "ESCALATED": "Escalado", "CLOSED": "Cerrado"},
    "DE": {"OPEN": "offen", "IN_PROGRESS": "in Bearbeitung", "RESOLVED": "gelöst",
           "ESCALATED": "eskaliert", "CLOSED": "geschlossen"},
    "CA": {"OPEN": "open", "IN_PROGRESS": "in_progress", "RESOLVED": "resolved",
           "ESCALATED": "escalated", "CLOSED": "closed"},
    "MA": {"OPEN": "Ouvert", "IN_PROGRESS": "En cours", "RESOLVED": "Résolu",
           "CLOSED": "Clos"},
}

CHANNELS = {
    "FR": ["Web", "Téléphone", "Email", "Agence"],
    "ES": ["Web", "Teléfono", "Email", "App"],
    "DE": ["Web", "Telefon", "E-Mail", "Filiale"],
    "CA": ["Web", "Phone", "Email", "Chat"],
    "MA": ["Web", "Téléphone", "Agence", "WhatsApp"],
}

# Refund in euro before the branch currency is applied.
REFUND_BASE = {1: 5.0, 2: 12.0, 3: 30.0, 4: 70.0}
CURRENCY_FACTOR = {"FR": 1.0, "ES": 1.0, "DE": 1.0, "CA": 1.5, "MA": 11.0}

# Codes nobody maintains: they must end up as RSN_UNK after the mapping.
BROKEN_CODES = ["", "N/A", "???", "A_CLASSER"]


def read_reference(name):
    return pd.read_csv(REFERENCE / name, comment="#", dtype="string")


def parcel_id(survey_id):
    """FR-S-00861 -> FC-FR-100860, the same rule the survey files follow."""
    country, _, number = survey_id.split("-")
    return f"FC-{country}-{100000 + int(number) - 1}"


def load_surveys():
    """Replay the survey loaders, keeping the raw city and product code."""
    surveys = pd.concat(
        [
            transform.load_france(),
            transform.load_spain(),
            transform.load_germany(),
            transform.load_canada(),
            transform.load_morocco(),
        ],
        ignore_index=True,
    )[transform.RAW_COLUMNS]

    surveys["survey_id"] = surveys["survey_id"].astype("string").str.strip()
    surveys["overall_score"] = surveys["overall_score"].fillna(
        surveys[transform.SCORE_COLUMNS].mean(axis=1)
    )
    surveys = surveys.dropna(subset=["survey_id"]).drop_duplicates(subset="survey_id")
    surveys["raw_city"] = surveys["source_city"]
    surveys["raw_product_code"] = surveys["source_product_code"]
    surveys = transform.add_product_key(surveys)
    surveys["parcel_id"] = surveys["survey_id"].map(parcel_id)
    return surveys


def complaint_probability(row):
    """Unhappy customers complain, happy ones almost never do."""
    score = row.overall_score
    if pd.isna(score):
        score = 3.0
    score = min(max(score, 1.0), 5.0)
    low = int(score)
    high = min(low + 1, 5)
    base = COMPLAINT_RATE[float(low)]
    if high > low:
        base += (COMPLAINT_RATE[float(high)] - base) * (score - low)
    aspects = [row.delivery_score, row.courier_score, row.condition_score, row.service_score]
    if any(not pd.isna(value) and value <= 2 for value in aspects):
        base += 0.12
    return min(base, 0.9)


def weakest_aspects(row):
    """The aspects the customer rated worst, worst first."""
    scored = [
        (value, aspect)
        for aspect, value in zip(transform.SCORE_COLUMNS, [
            row.delivery_score, row.courier_score, row.condition_score, row.service_score
        ])
        if not pd.isna(value)
    ]
    return [aspect for _, aspect in sorted(scored)]


def reason_from_comment(comment):
    if not isinstance(comment, str):
        return None
    text = comment.lower()
    for needle, reason_key in COMMENT_REASONS:
        if needle in text:
            return reason_key
    return None


def pick_reason(rng, aspect, product_key):
    weights = dict(REASON_WEIGHTS[aspect])
    if product_key != "PRD_CLD":
        weights.pop(COLD_ONLY, None)
    for reason_key, factor in PRODUCT_BIAS.get(product_key, {}).items():
        if reason_key in weights:
            weights[reason_key] *= factor
    return rng.choices(list(weights), weights=list(weights.values()))[0]


def pick_severity(rng, score, reason_key):
    """Critical for a lost or ruined parcel, minor for a small annoyance."""
    if pd.isna(score):
        score = 2.5
    level = 4 if score <= 1.5 else 3 if score <= 2.5 else 2 if score <= 3.5 else 1
    if reason_key in ("RSN_LOST", "RSN_COLDCHAIN"):
        level = min(level + 1, 4)
    if reason_key in ("RSN_WRONGINFO", "RSN_FEES", "RSN_UNK"):
        level = max(level - 1, 1)
    if rng.random() < 0.15:
        level = min(max(level + rng.choice([-1, 1]), 1), 4)
    return level


def pick_status(rng, level, reason_key):
    """Service failures are the ones that stay open."""
    settled = 0.80 - 0.10 * level
    if reason_key in ("RSN_NOREPLY", "RSN_REFUND"):
        settled -= 0.25
    if rng.random() < settled:
        return rng.choices(["RESOLVED", "CLOSED"], weights=[0.75, 0.25])[0]
    return rng.choices(["OPEN", "IN_PROGRESS", "ESCALATED"], weights=[0.35, 0.45, 0.20])[0]


def build_complaints(surveys, reasons, rng):
    """One row per complaint, still in platform wording."""
    compensable = set(reasons.loc[reasons["is_compensable"] == "true", "reason_key"])
    aspect_of = dict(zip(reasons["reason_key"], reasons["aspect"]))
    records = []

    for row in surveys.itertuples():
        if rng.random() > complaint_probability(row):
            continue

        aspects = weakest_aspects(row)
        from_comment = reason_from_comment(row.comment)
        picked = []
        if from_comment:
            picked.append(from_comment)
        elif aspects:
            picked.append(pick_reason(rng, aspects[0], row.product_key))
        else:
            picked.append(pick_reason(rng, rng.choice(list(REASON_WEIGHTS)), row.product_key))

        # A second reason only when another aspect was rated badly too.
        for aspect in aspects:
            if aspect == aspect_of.get(picked[0]):
                continue
            if getattr(row, aspect) <= 2 and rng.random() < 0.35:
                picked.append(pick_reason(rng, aspect, row.product_key))
            break

        for order, reason_key in enumerate(picked):
            if rng.random() < 0.04:
                reason_key = "RSN_FEES"
            level = pick_severity(rng, row.overall_score, reason_key)
            status = pick_status(rng, level, reason_key)
            refund = 0.0
            if reason_key in compensable and status in ("RESOLVED", "CLOSED"):
                refund = REFUND_BASE[level] * rng.uniform(0.6, 1.6)

            # The complaint is filed in the days around the survey answer.
            date = row.survey_date
            if not pd.isna(date):
                date = date - pd.Timedelta(days=rng.randint(0, 12) + 3 * order)
                date = max(date, pd.Timestamp("2025-01-01"))

            records.append({
                "country_code": row.country_code,
                "parcel_id": row.parcel_id,
                "survey_id": row.survey_id,
                "complaint_date": date,
                "raw_city": row.raw_city,
                "raw_product_code": row.raw_product_code,
                "reason_key": reason_key,
                "severity_level": level,
                "status": status,
                "refund_eur": refund,
                "handling_days": rng.randint(1, 6) if status in ("RESOLVED", "CLOSED")
                else rng.randint(7, 45),
            })

    return pd.DataFrame(records)


def add_orphans(complaints, surveys, rng):
    """Customers who complained but never answered a survey."""
    extra = []
    for country_code, group in complaints.groupby("country_code"):
        highest = surveys.loc[surveys["country_code"] == country_code, "parcel_id"]
        highest = highest.str.split("-").str[-1].astype(int).max()
        for _ in range(max(1, round(len(group) * 0.03))):
            sample = group.sample(1, random_state=rng.randint(0, 10**6)).iloc[0].to_dict()
            sample["parcel_id"] = f"FC-{country_code}-{highest + rng.randint(1, 400)}"
            sample["survey_id"] = None
            extra.append(sample)
    return pd.concat([complaints, pd.DataFrame(extra)], ignore_index=True)


def add_ids(complaints, rng):
    """Shuffle, then number per country the way the survey ids are numbered."""
    complaints = complaints.sample(frac=1, random_state=rng.randint(0, 10**6))
    complaints = complaints.reset_index(drop=True)
    numbers = complaints.groupby("country_code").cumcount() + 1
    complaints["complaint_id"] = (
        complaints["country_code"] + "-C-" + numbers.astype(str).str.zfill(5)
    )
    return complaints


def local_code(rng, country_code, reason_key, mapping):
    """Pick one of the local spellings, then rough it up a little."""
    options = mapping[
        (mapping["country_code"] == country_code) & (mapping["reason_key"] == reason_key)
    ]["source_code"].tolist()
    code = rng.choice(options) if options else "RSN_UNK"
    if country_code == "DE":
        code = code.replace("_", "-")
    roll = rng.random()
    if roll < 0.02:
        return rng.choice(BROKEN_CODES)
    if roll < 0.06:
        return code.lower()
    if roll < 0.09:
        return f" {code} "
    return code


def local_date(rng, date, formats):
    if pd.isna(date) or rng.random() < 0.01:
        return None
    fmt = formats[0] if rng.random() > 0.05 else formats[-1]
    return date.strftime(fmt)


def local_city(rng, city):
    if not isinstance(city, str):
        return None
    if rng.random() < 0.04:
        return city.upper()
    if rng.random() < 0.04:
        return f" {city}"
    return city


def amount(value, factor, decimals=2, decimal_comma=False):
    if not value:
        return None
    scaled = round(value * factor, decimals)
    if decimals == 0:
        return str(int(scaled))
    text = f"{scaled:.2f}"
    return text.replace(".", ",") if decimal_comma else scaled


def duplicate_some(frame, rng, share=0.01):
    """Ticket exports that ran twice leave the same row behind."""
    extra = frame.sample(frac=share, random_state=rng.randint(0, 10**6))
    return pd.concat([frame, extra], ignore_index=True).sample(
        frac=1, random_state=rng.randint(0, 10**6)
    )


def write_france(rows, rng, mapping):
    frame = pd.DataFrame({
        "id_reclamation": rows["complaint_id"],
        "numero_colis": rows["parcel_id"],
        "id_enquete": rows["survey_id"],
        "date_reclamation": [local_date(rng, d, ["%d/%m/%Y", "%Y-%m-%d"])
                             for d in rows["complaint_date"]],
        "ville": [local_city(rng, c) for c in rows["raw_city"]],
        "code_produit": rows["raw_product_code"],
        "canal": [rng.choice(CHANNELS["FR"]) for _ in range(len(rows))],
        "motif_code": [local_code(rng, "FR", key, mapping) for key in rows["reason_key"]],
        "description": [TEXTS["fr"][key] for key in rows["reason_key"]],
        "gravite": [LOCAL_SEVERITY["FR"][level] for level in rows["severity_level"]],
        "statut": [LOCAL_STATUS["FR"][status] for status in rows["status"]],
        "delai_traitement_jours": rows["handling_days"],
        "montant_remboursement": [amount(v, 1.0, decimal_comma=True)
                                  for v in rows["refund_eur"]],
    })
    duplicate_some(frame, rng).to_excel(DATA / "france_complaints_raw.xlsx", index=False)


def write_spain(rows, rng, mapping):
    records = []
    for row in rows.itertuples():
        records.append({
            "reclamacion_id": row.complaint_id,
            "envio": {
                "id": row.parcel_id,
                "encuesta_id": row.survey_id,
                "ciudad": local_city(rng, row.raw_city),
                "codigo_producto": row.raw_product_code,
            },
            "fecha": local_date(rng, row.complaint_date, ["%Y-%m-%d", "%d-%m-%Y"]),
            "canal": rng.choice(CHANNELS["ES"]),
            "motivo": {
                "codigo": local_code(rng, "ES", row.reason_key, mapping),
                "descripcion": TEXTS["es"][row.reason_key],
            },
            "gravedad": LOCAL_SEVERITY["ES"][row.severity_level],
            "estado": LOCAL_STATUS["ES"][row.status],
            "dias_gestion": row.handling_days,
            "importe_reembolso": amount(row.refund_eur, 1.0),
        })
    # Spain exports a few tickets twice and leaves a blank grade behind.
    for record in rng.sample(records, k=max(1, len(records) // 40)):
        record["gravedad"] = None
    records += [dict(record) for record in rng.sample(records, k=max(1, len(records) // 100))]
    rng.shuffle(records)
    (DATA / "spain_complaints_raw.json").write_text(
        json.dumps(records, ensure_ascii=False, indent=2), encoding="utf-8"
    )


def write_germany(rows, rng, mapping):
    frame = pd.DataFrame({
        "beschwerde_id": rows["complaint_id"],
        "paket_nr": rows["parcel_id"],
        "umfrage_id": rows["survey_id"],
        "datum": [local_date(rng, d, ["%d.%m.%Y"]) for d in rows["complaint_date"]],
        "stadt": [local_city(rng, c) for c in rows["raw_city"]],
        "produkt_code": rows["raw_product_code"],
        "kanal": [rng.choice(CHANNELS["DE"]) for _ in range(len(rows))],
        "grund_code": [local_code(rng, "DE", key, mapping) for key in rows["reason_key"]],
        "beschreibung": [TEXTS["de"][key] for key in rows["reason_key"]],
        "schweregrad": [LOCAL_SEVERITY["DE"][level] for level in rows["severity_level"]],
        "status": [LOCAL_STATUS["DE"][status] for status in rows["status"]],
        "bearbeitungstage": rows["handling_days"],
        "erstattung_eur": [amount(v, 1.0, decimal_comma=True) for v in rows["refund_eur"]],
    })
    duplicate_some(frame, rng).to_csv(
        DATA / "germany_complaints_raw.csv", sep=";", index=False, encoding="utf-8-sig"
    )


def write_canada(rows, rng, mapping):
    lines = []
    for row in rows.itertuples():
        french = isinstance(row.raw_city, str) and row.raw_city in ("Montréal", "Québec")
        language = "FR" if rng.random() < (0.7 if french else 0.15) else "EN"
        lines.append({
            "complaint_id": row.complaint_id,
            "parcel_id": row.parcel_id,
            "survey_id": row.survey_id,
            "created_at": local_date(rng, row.complaint_date, ["%Y-%m-%d", "%m/%d/%Y"]),
            "city": local_city(rng, row.raw_city),
            "product_code": row.raw_product_code,
            "channel": rng.choice(CHANNELS["CA"]),
            "reason_code": local_code(rng, "CA", row.reason_key, mapping),
            "description": TEXTS["fr" if language == "FR" else "en"][row.reason_key],
            "severity": int(LOCAL_SEVERITY["CA"][row.severity_level]),
            "status": LOCAL_STATUS["CA"][row.status],
            "handling_days": row.handling_days,
            "refund_cad": amount(row.refund_eur, CURRENCY_FACTOR["CA"]),
            "language": language,
        })
    lines += [dict(line) for line in rng.sample(lines, k=max(1, len(lines) // 100))]
    rng.shuffle(lines)
    (DATA / "canada_complaints_raw.jsonl").write_text(
        "\n".join(json.dumps(line, ensure_ascii=False) for line in lines) + "\n",
        encoding="utf-8",
    )


def write_morocco(rows, rng, mapping):
    languages = [rng.choices(["FR", "Darija", "AR"], weights=[0.4, 0.4, 0.2])[0]
                 for _ in range(len(rows))]
    frame = pd.DataFrame({
        "id_reclamation": rows["complaint_id"],
        "numero_colis": rows["parcel_id"],
        "id_enquete": rows["survey_id"],
        "date_reclamation": [local_date(rng, d, ["%d/%m/%Y"]) for d in rows["complaint_date"]],
        "ville": [local_city(rng, c) for c in rows["raw_city"]],
        "code_produit": rows["raw_product_code"],
        "canal": [rng.choice(CHANNELS["MA"]) for _ in range(len(rows))],
        "motif_saisi": [local_code(rng, "MA", key, mapping) for key in rows["reason_key"]],
        "description": [
            TEXTS[{"FR": "fr", "Darija": "darija", "AR": "ar"}[language]][key]
            for language, key in zip(languages, rows["reason_key"])
        ],
        "langue_saisie": languages,
        # The branch has no severity field and settles everything in cash.
        "statut": [LOCAL_STATUS["MA"].get(status, "En cours") for status in rows["status"]],
        "montant_mad": [amount(v, CURRENCY_FACTOR["MA"], decimals=0)
                        for v in rows["refund_eur"]],
    })
    duplicate_some(frame, rng).to_csv(
        DATA / "morocco_complaints_raw.txt", sep="|", index=False, encoding="utf-8"
    )


WRITERS = {
    "FR": write_france,
    "ES": write_spain,
    "DE": write_germany,
    "CA": write_canada,
    "MA": write_morocco,
}


def main():
    rng = random.Random(SEED)
    mapping = read_reference("complaint_reason_mapping.csv")
    reasons = read_reference("complaint_reason_master.csv")

    surveys = load_surveys()
    complaints = build_complaints(surveys, reasons, rng)
    complaints = add_orphans(complaints, surveys, rng)
    complaints = add_ids(complaints, rng)

    for country_code, write in WRITERS.items():
        rows = complaints[complaints["country_code"] == country_code].reset_index(drop=True)
        write(rows, rng, mapping)
        print(f"{country_code}: {len(rows)} complaints")

    print(f"{len(complaints)} complaints for {len(surveys)} surveys -> {DATA}")
    share = complaints.groupby("country_code")["reason_key"].value_counts(normalize=True)
    print(share.groupby(level=0).head(3).round(2))


if __name__ == "__main__":
    main()
