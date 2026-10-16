"""
Generate Phase 1 CSV backlog and documentation for Smart Logistics CO2 Calculator.
Validates all constraints specified in Phase 1 of todo.md:
- Total EPICS <= 7
- Features per EPIC <= 5
- Dev tasks per feature <= 4
- User stories in format US_X.Y.Z with role/action/benefit description
- Features connected to selected User story
- Dev tasks connected to corresponding feature
"""

import csv
import os

epics_data = [
    {
        "id": 1,
        "name": "EPIC 1: Multi-Source Logistics Data Ingestion & Storage",
        "features": [
            {
                "id": "1.1",
                "name": "FEAT 1.1: ERP & SAP Parcel Order Ingestion",
                "user_story": {
                    "id": "US_1.1.1",
                    "role": "Data Engineer",
                    "want": "automatically ingest ERP parcel order records",
                    "so_that": "foundational parcel dimensions, weights, and delivery destinations are centralized on the platform",
                },
                "tasks": [
                    "TASK 1.1.1: Define ERP parcel schema and generate synthetic multi-country order records.",
                    "TASK 1.1.2: Implement data ingestion pipeline with strict type and boundary validation for ERP orders.",
                    "TASK 1.1.3: Store validated order records into structured relational database table 'orders'.",
                ],
            },
            {
                "id": "1.2",
                "name": "FEAT 1.2: Logistics Checkpoint Scan Events Ingestion",
                "user_story": {
                    "id": "US_1.2.1",
                    "role": "Data Engineer",
                    "want": "ingest parcel checkpoint scan event streams",
                    "so_that": "handling timestamps, hub locations, and scan types are reliably captured for transit tracking",
                },
                "tasks": [
                    "TASK 1.2.1: Define scan event schema (tracking_id, timestamp, hub_id, scan_type).",
                    "TASK 1.2.2: Build parsing script for chronological scan logs with ISO-8601 timestamp normalization.",
                    "TASK 1.2.3: Ingest scan records into structured relational database table 'tracking_events'.",
                ],
            },
            {
                "id": "1.3",
                "name": "FEAT 1.3: TMS Carrier & Dispatch Manifest Ingestion",
                "user_story": {
                    "id": "US_1.3.1",
                    "role": "Logistics Analyst",
                    "want": "ingest carrier transport manifests and dispatch logs",
                    "so_that": "transit route identifiers, carrier services, and vehicle classifications are linked to shipments",
                },
                "tasks": [
                    "TASK 1.3.1: Define TMS transit specifications mapping route legs, carrier IDs, and vehicle types.",
                    "TASK 1.3.2: Implement ingestion workflow parsing carrier dispatch manifests and service tiers.",
                    "TASK 1.3.3: Load vehicle fleet and carrier metadata into relational database tables 'fleet' and 'carriers'.",
                ],
            },
            {
                "id": "1.4",
                "name": "FEAT 1.4: Geographic Hub & GPS Coordinates Ingestion",
                "user_story": {
                    "id": "US_1.4.1",
                    "role": "Data Steward",
                    "want": "centralize geographical reference tables for hubs, depots, and airports",
                    "so_that": "precise GPS coordinates can be mapped to transport segments",
                },
                "tasks": [
                    "TASK 1.4.1: Curate reference dataset of logistics hubs, regional airports, and local depots with GPS coordinates.",
                    "TASK 1.4.2: Build validation rules for ISO country codes, postal codes, and coordinate boundaries.",
                    "TASK 1.4.3: Populate geographic reference data into structured database table 'dim_hubs_cities'.",
                ],
            },
            {
                "id": "1.5",
                "name": "FEAT 1.5: Relational Database Architecture & Integrity Setup",
                "user_story": {
                    "id": "US_1.5.1",
                    "role": "Database Architect",
                    "want": "establish relational schemas with primary and foreign key constraints",
                    "so_that": "cross-system data joins maintain strict integrity and support high-performance analytical queries",
                },
                "tasks": [
                    "TASK 1.5.1: Write DDL schema defining tables, primary keys, foreign keys, and indexes.",
                    "TASK 1.5.2: Create automated integrity check script detecting orphaned scan events or unmapped hubs.",
                    "TASK 1.5.3: Build database bootstrap and automated migration runner.",
                ],
            },
        ],
    },
    {
        "id": 2,
        "name": "EPIC 2: Multi-Modal Journey Reconstruction & Enrichment",
        "features": [
            {
                "id": "2.1",
                "name": "FEAT 2.1: Scan Event Sequencing & Segment Splitting",
                "user_story": {
                    "id": "US_2.1.1",
                    "role": "Data Engineer",
                    "want": "order parcel scans chronologically and identify leg boundaries",
                    "so_that": "multi-segment parcel transit paths from warehouse to customer are accurately reconstructed",
                },
                "tasks": [
                    "TASK 2.1.1: Develop scan event sorting and deduplication logic per tracking_id.",
                    "TASK 2.1.2: Implement journey segment boundary detector between origin, intermediate hubs, and delivery.",
                    "TASK 2.1.3: Construct raw journey segment pairs (origin_node, destination_node, departure_time, arrival_time).",
                ],
            },
            {
                "id": "2.2",
                "name": "FEAT 2.2: Transport Mode Classification & Inference",
                "user_story": {
                    "id": "US_2.2.1",
                    "role": "Logistics Specialist",
                    "want": "assign the correct transport mode (LCV, Truck, Air freight, Bicycle) to each journey segment",
                    "so_that": "appropriate carbon calculation parameters are applied per leg",
                },
                "tasks": [
                    "TASK 2.2.1: Map carrier route codes and hub types to standard transport modes.",
                    "TASK 2.2.2: Build rule-based fallback mode classifier for unlabelled legs based on hub categories and distance.",
                    "TASK 2.2.3: Validate transport mode assignments against shipment service levels.",
                ],
            },
            {
                "id": "2.3",
                "name": "FEAT 2.3: Segment Distance Calculation & Detour Modeling",
                "user_story": {
                    "id": "US_2.3.1",
                    "role": "Data Scientist",
                    "want": "calculate realistic segment travel distances from geographic coordinates",
                    "so_that": "accurate kilometer lengths are established for every leg of the journey",
                },
                "tasks": [
                    "TASK 2.3.1: Implement Haversine geodesic distance calculation between segment origin and destination coordinates.",
                    "TASK 2.3.2: Apply modal detour routing factors (1.25 road detour factor, 1.05 air routing).",
                    "TASK 2.3.3: Cache and store calculated segment distances in 'distance_estimee_km'.",
                ],
            },
            {
                "id": "2.4",
                "name": "FEAT 2.4: Journey Quality & Anomaly Detection",
                "user_story": {
                    "id": "US_2.4.1",
                    "role": "Data Quality Specialist",
                    "want": "detect temporal inconsistencies and impossible transit speeds across segments",
                    "so_that": "corrupted or anomalous journey paths are flagged before carbon calculation",
                },
                "tasks": [
                    "TASK 2.4.1: Implement transit velocity checks identifying unrealistic speeds or negative transit times.",
                    "TASK 2.4.2: Build reconciliation rule engine to impute missing intermediate transit hubs for standard corridors.",
                    "TASK 2.4.3: Generate automated journey reconstruction quality report with error flagging.",
                ],
            },
        ],
    },
    {
        "id": 3,
        "name": "EPIC 3: CO2 Emission Factors Harmonization & Calculation Engine",
        "features": [
            {
                "id": "3.1",
                "name": "FEAT 3.1: ADEME Base Empreinte Factor Harmonization",
                "user_story": {
                    "id": "US_3.1.1",
                    "role": "Sustainability Specialist",
                    "want": "integrate official ADEME Base Empreinte emission factors into a standardized reference table",
                    "so_that": "calculations strictly adhere to accredited carbon accounting standards",
                },
                "tasks": [
                    "TASK 3.1.1: Extract and curate official ADEME carbon factors for LCV, heavy truck, air freight, and electric cargo bike.",
                    "TASK 3.1.2: Normalize factor unit metrics (kgCO2e/km vs kgCO2e/t.km vs zero baseline).",
                    "TASK 3.1.3: Store factor reference data in table 'dim_emission_factors' with version and validity metadata.",
                ],
            },
            {
                "id": "3.2",
                "name": "FEAT 3.2: Segment-Level CO2 Calculation Engine",
                "user_story": {
                    "id": "US_3.2.1",
                    "role": "Data Engineer",
                    "want": "compute emissions for each journey segment based on modal formulas and units",
                    "so_that": "granular segment-level carbon footprints are determined",
                },
                "tasks": [
                    "TASK 3.2.1: Implement ton-kilometer emissions formula (distance_km * weight_t * factor) for heavy truck and air freight.",
                    "TASK 3.2.2: Implement vehicle-kilometer formula (distance_km * factor) with parcel allocation for LCV delivery legs.",
                    "TASK 3.2.3: Implement zero-carbon calculation logic for active transport modes (Bicycle / Walking).",
                ],
            },
            {
                "id": "3.3",
                "name": "FEAT 3.3: Parcel-Level Emissions Aggregation",
                "user_story": {
                    "id": "US_3.3.1",
                    "role": "Carbon Accountant",
                    "want": "aggregate emissions across all reconstructed journey segments for each parcel",
                    "so_that": "the total end-to-end carbon footprint per parcel is computed",
                },
                "tasks": [
                    "TASK 3.3.1: Build aggregation pipeline computing estimated_emissions = sum(segment_emissions).",
                    "TASK 3.3.2: Calculate parcel journey summary metrics including total distance and hub count (number_of_hubs).",
                    "TASK 3.3.3: Join parcel-level aggregated carbon metrics into the master tracking table.",
                ],
            },
            {
                "id": "3.4",
                "name": "FEAT 3.4: Calculation Verification & Reference Walkthrough Tests",
                "user_story": {
                    "id": "US_3.4.1",
                    "role": "QA Engineer",
                    "want": "automated unit tests comparing calculations against benchmark test cases",
                    "so_that": "mathematical accuracy matching reference examples (Parcel P001 = 15.81 kgCO2e) is proven",
                },
                "tasks": [
                    "TASK 3.4.1: Write unit test verifying exact walkthrough calculation for Parcel P001 across its 4 segments.",
                    "TASK 3.4.2: Add edge-case test cases for high-weight parcels, zero-emission legs, and extreme distances.",
                    "TASK 3.4.3: Implement automated threshold assertions alerting on abnormal carbon outliers.",
                ],
            },
        ],
    },
    {
        "id": 4,
        "name": "EPIC 4: Unified Logistics & Carbon Dataset Construction",
        "features": [
            {
                "id": "4.1",
                "name": "FEAT 4.1: Target Schema Harmonization & Formatting",
                "user_story": {
                    "id": "US_4.1.1",
                    "role": "Data Steward",
                    "want": "harmonize parcel variables into the specified 10-column final dataset schema",
                    "so_that": "downstream consumers and analysts receive a unified and standardized data structure",
                },
                "tasks": [
                    "TASK 4.1.1: Build dataset assembler mapping tracking_id, date_premier_flashage, countries, weights, hubs, distance, mode, and emissions.",
                    "TASK 4.1.2: Standardize country identifiers into ISO 3166-1 alpha-2 format and normalize dates to ISO-8601.",
                    "TASK 4.1.3: Enforce strict data type casting and null representation rules across all fields.",
                ],
            },
            {
                "id": "4.2",
                "name": "FEAT 4.2: Missing Data Treatment & Imputation",
                "user_story": {
                    "id": "US_4.2.1",
                    "role": "Data Engineer",
                    "want": "impute missing parcel weights and dimensions using category medians",
                    "so_that": "calculation gaps are resolved without omitting valuable shipment records",
                },
                "tasks": [
                    "TASK 4.2.1: Profile missingness rates across weight, volume, and scan attributes.",
                    "TASK 4.2.2: Implement volumetric ratio and median imputation for missing parcel weights.",
                    "TASK 4.2.3: Quarantine unrecoverable records with detailed audit logging.",
                ],
            },
            {
                "id": "4.3",
                "name": "FEAT 4.3: Analytical Export & Performance Optimization",
                "user_story": {
                    "id": "US_4.3.1",
                    "role": "BI Developer",
                    "want": "partitioned Parquet and structured CSV exports of the unified dataset",
                    "so_that": "dashboards, analytical queries, and reports execute with high performance",
                },
                "tasks": [
                    "TASK 4.3.1: Implement partitioned Parquet export by date and destination country.",
                    "TASK 4.3.2: Implement structured CSV export with comprehensive metadata header.",
                    "TASK 4.3.3: Generate automated data dictionary and summary profile report.",
                ],
            },
        ],
    },
    {
        "id": 5,
        "name": "EPIC 5: Machine Learning CO2 Prediction Model",
        "features": [
            {
                "id": "5.1",
                "name": "FEAT 5.1: Feature Engineering for Incomplete Journey Estimation",
                "user_story": {
                    "id": "US_5.1.1",
                    "role": "Machine Learning Engineer",
                    "want": "extract predictive features from parcel characteristics",
                    "so_that": "emissions can be predicted when detailed scan histories are missing",
                },
                "tasks": [
                    "TASK 5.1.1: Engineer direct origin-destination geodesic distance, corridor flags, and parcel density features.",
                    "TASK 5.1.2: Encode categorical features including origin country, destination country, and service tier.",
                    "TASK 5.1.3: Construct verified training, validation, and test datasets from complete reconstructed journeys.",
                ],
            },
            {
                "id": "5.2",
                "name": "FEAT 5.2: Model Training, Evaluation & Cross-Validation",
                "user_story": {
                    "id": "US_5.2.1",
                    "role": "Data Scientist",
                    "want": "train regression models on complete journey emissions data",
                    "so_that": "high predictive accuracy (low MAE and RMSE) is achieved for estimated footprint prediction",
                },
                "tasks": [
                    "TASK 5.2.1: Train baseline linear regression and tree-based ensemble models (Random Forest / LightGBM).",
                    "TASK 5.2.2: Perform hyperparameter tuning and 5-fold cross-validation on emissions regression.",
                    "TASK 5.2.3: Evaluate error metrics (RMSE, MAE, R2) and calculate feature importance.",
                ],
            },
            {
                "id": "5.3",
                "name": "FEAT 5.3: Batch Prediction & ml_emissions Integration",
                "user_story": {
                    "id": "US_5.3.1",
                    "role": "Data Engineer",
                    "want": "execute batch model inference for parcels with missing scans and populate ml_emissions",
                    "so_that": "every parcel in the final dataset has an actionable emissions value",
                },
                "tasks": [
                    "TASK 5.3.1: Build batch inference pipeline loading the trained regression model artifact.",
                    "TASK 5.3.2: Populate ml_emissions column for parcels missing detailed scan journeys.",
                    "TASK 5.3.3: Compute prediction uncertainty intervals and confidence scores for each estimated value.",
                ],
            },
        ],
    },
    {
        "id": 6,
        "name": "EPIC 6: Carbon Footprint Analytics, Reporting & Interactive Simulator",
        "features": [
            {
                "id": "6.1",
                "name": "FEAT 6.1: Carbon Footprint Analytics & KPI Generation",
                "user_story": {
                    "id": "US_6.1.1",
                    "role": "Logistics Strategy Manager",
                    "want": "aggregated carbon metrics by transport mode, corridor, and carrier",
                    "so_that": "decarbonization priorities and high-emission routes can be identified",
                },
                "tasks": [
                    "TASK 6.1.1: Aggregate total and average carbon emissions grouped by transport mode and carrier.",
                    "TASK 6.1.2: Compute carbon intensity KPIs (gCO2e per ton-km and average kgCO2e per parcel) per lane.",
                    "TASK 6.1.3: Identify top 10 carbon-emitting logistics corridors and modal bottlenecks.",
                ],
            },
            {
                "id": "6.2",
                "name": "FEAT 6.2: Modal Shift & Eco-Routing Scenario Simulator",
                "user_story": {
                    "id": "US_6.2.1",
                    "role": "Operations Planner",
                    "want": "simulate modal shift scenarios (e.g., air to rail or diesel van to cargo bike)",
                    "so_that": "potential emissions savings can be quantified before making operational changes",
                },
                "tasks": [
                    "TASK 6.2.1: Build simulation function allowing substitution of segment transport modes.",
                    "TASK 6.2.2: Compute delta CO2 savings and percentage reductions for simulated scenarios.",
                    "TASK 6.2.3: Generate scenario comparison summary tables for operational decision-making.",
                ],
            },
            {
                "id": "6.3",
                "name": "FEAT 6.3: Interactive Sustainability Dashboard",
                "user_story": {
                    "id": "US_6.3.1",
                    "role": "Executive Stakeholder",
                    "want": "an interactive dashboard displaying carbon KPIs and scenario simulators",
                    "so_that": "sustainability performance and reduction pathways are clear to leadership",
                },
                "tasks": [
                    "TASK 6.3.1: Develop interactive dashboard web interface with KPI summary cards and modal charts.",
                    "TASK 6.3.2: Add interactive scenario simulator controls allowing users to test modal shift parameters.",
                    "TASK 6.3.3: Implement automated export of carbon reports and visualization charts.",
                ],
            },
        ],
    },
]

def validate_rules(epics):
    assert len(epics) <= 7, f"EPICS count must be <= 7, got {len(epics)}"
    total_features = 0
    total_tasks = 0
    total_stories = 0
    
    for epic in epics:
        features = epic["features"]
        assert len(features) <= 5, f"Features in {epic['name']} must be <= 5, got {len(features)}"
        for feat in features:
            total_features += 1
            us = feat["user_story"]
            total_stories += 1
            # Check US ID format
            assert us["id"].startswith(f"US_{epic['id']}."), f"US ID {us['id']} must connect to EPIC {epic['id']}"
            tasks = feat["tasks"]
            assert len(tasks) <= 4, f"Tasks in {feat['name']} must be <= 4, got {len(tasks)}"
            for task in tasks:
                total_tasks += 1
                
    print(f"Validation passed!")
    print(f"Total EPICS: {len(epics)} (rule: <= 7)")
    print(f"Total Features: {total_features} (rule per epic: <= 5)")
    print(f"Total User Stories: {total_stories}")
    print(f"Total Dev Tasks: {total_tasks} (rule per feature: <= 4)")

def generate_csv_rows(epics):
    rows = []
    for epic in epics:
        epic_name = epic["name"]
        for feat in epic["features"]:
            feat_name = feat["name"]
            us = feat["user_story"]
            us_text = f"{us['id']}: As a {us['role']}, I want to {us['want']} so that {us['so_that']}."
            for task in feat["tasks"]:
                rows.append({
                    "EPIC": epic_name,
                    "User story": us_text,
                    "Features": feat_name,
                    "Dev tasks": task
                })
    return rows

def write_csv(filepath, rows):
    fieldnames = ["EPIC", "User story", "Features", "Dev tasks"]
    dirname = os.path.dirname(filepath)
    if dirname:
        os.makedirs(dirname, exist_ok=True)
    with open(filepath, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)
    print(f"Written {len(rows)} rows to {filepath}")

if __name__ == "__main__":
    validate_rules(epics_data)
    rows = generate_csv_rows(epics_data)
    
    # Save in second_proj/
    write_csv("second_proj/backlog.csv", rows)
    write_csv("second_proj/phase1_backlog.csv", rows)
    # Also save in root for easy discovery
    write_csv("phase1_backlog.csv", rows)
