# Smart Logistics CO2 Calculator - Phase 1 Backlog

## Overview
This document outlines the Phase 1 preparation backlog for the **Smart Logistics CO2 Calculator** study project.

The backlog is saved as a structured CSV in:
- [`second_proj/backlog.csv`](file:///Users/nefelim584/PycharmProjects/Data_Wrangling/second_proj/backlog.csv)
- [`second_proj/phase1_backlog.csv`](file:///Users/nefelim584/PycharmProjects/Data_Wrangling/second_proj/phase1_backlog.csv)
- [`phase1_backlog.csv`](file:///Users/nefelim584/PycharmProjects/Data_Wrangling/phase1_backlog.csv)

Generated using automated validation script: [`second_proj/generate_backlog.py`](file:///Users/nefelim584/PycharmProjects/Data_Wrangling/second_proj/generate_backlog.py).

---

## Compliance with Phase 1 Rules

| Rule | Requirement | Actual Value | Status |
| :--- | :--- | :--- | :---: |
| **EPIC Count** | Not more than 7 EPICS | **6 EPICS** | ✅ Pass |
| **Connected Features per EPIC** | Not more than 5 Features per EPIC | **3 to 5 Features per EPIC** (Total: 22) | ✅ Pass |
| **User Story Format** | Format `US_X.Y.Z` with Role, Want, So That | **22 User Stories** (`US_1.1.1` to `US_6.3.1`) | ✅ Pass |
| **User Story - EPIC Connection** | Connect to correct EPIC | All stories linked (`US_1.x` to EPIC 1, etc.) | ✅ Pass |
| **Feature - User Story Connection** | 1-to-1 linkage (`FEAT X.Y` to `US_X.Y.1`) | Fully mapped across all 22 features | ✅ Pass |
| **Dev Tasks per Feature** | Not more than 4 Dev Tasks per Feature | **3 Dev Tasks per Feature** (Total: 66) | ✅ Pass |
| **Dev Task - Feature Connection** | Explicit naming and link to feature | Fully linked in CSV columns | ✅ Pass |

---

## EPICS & Features Summary

### EPIC 1: Multi-Source Logistics Data Ingestion & Storage
1. **FEAT 1.1: ERP & SAP Parcel Order Ingestion** (Linked: `US_1.1.1`)
   - `TASK 1.1.1`: Define ERP parcel schema and generate synthetic multi-country order records.
   - `TASK 1.1.2`: Implement data ingestion pipeline with strict type and boundary validation for ERP orders.
   - `TASK 1.1.3`: Store validated order records into structured relational database table 'orders'.
2. **FEAT 1.2: Logistics Checkpoint Scan Events Ingestion** (Linked: `US_1.2.1`)
   - `TASK 1.2.1`: Define scan event schema (tracking_id, timestamp, hub_id, scan_type).
   - `TASK 1.2.2`: Build parsing script for chronological scan logs with ISO-8601 timestamp normalization.
   - `TASK 1.2.3`: Ingest scan records into structured relational database table 'tracking_events'.
3. **FEAT 1.3: TMS Carrier & Dispatch Manifest Ingestion** (Linked: `US_1.3.1`)
   - `TASK 1.3.1`: Define TMS transit specifications mapping route legs, carrier IDs, and vehicle types.
   - `TASK 1.3.2`: Implement ingestion workflow parsing carrier dispatch manifests and service tiers.
   - `TASK 1.3.3`: Load vehicle fleet and carrier metadata into relational database tables 'fleet' and 'carriers'.
4. **FEAT 1.4: Geographic Hub & GPS Coordinates Ingestion** (Linked: `US_1.4.1`)
   - `TASK 1.4.1`: Curate reference dataset of logistics hubs, regional airports, and local depots with GPS coordinates.
   - `TASK 1.4.2`: Build validation rules for ISO country codes, postal codes, and coordinate boundaries.
   - `TASK 1.4.3`: Populate geographic reference data into structured database table 'dim_hubs_cities'.
5. **FEAT 1.5: Relational Database Architecture & Integrity Setup** (Linked: `US_1.5.1`)
   - `TASK 1.5.1`: Write DDL schema defining tables, primary keys, foreign keys, and indexes.
   - `TASK 1.5.2`: Create automated integrity check script detecting orphaned scan events or unmapped hubs.
   - `TASK 1.5.3`: Build database bootstrap and automated migration runner.

---

### EPIC 2: Multi-Modal Journey Reconstruction & Enrichment
1. **FEAT 2.1: Scan Event Sequencing & Segment Splitting** (Linked: `US_2.1.1`)
   - `TASK 2.1.1`: Develop scan event sorting and deduplication logic per tracking_id.
   - `TASK 2.1.2`: Implement journey segment boundary detector between origin, intermediate hubs, and delivery.
   - `TASK 2.1.3`: Construct raw journey segment pairs (origin_node, destination_node, departure_time, arrival_time).
2. **FEAT 2.2: Transport Mode Classification & Inference** (Linked: `US_2.2.1`)
   - `TASK 2.2.1`: Map carrier route codes and hub types to standard transport modes.
   - `TASK 2.2.2`: Build rule-based fallback mode classifier for unlabelled legs based on hub categories and distance.
   - `TASK 2.2.3`: Validate transport mode assignments against shipment service levels.
3. **FEAT 2.3: Segment Distance Calculation & Detour Modeling** (Linked: `US_2.3.1`)
   - `TASK 2.3.1`: Implement Haversine geodesic distance calculation between segment origin and destination coordinates.
   - `TASK 2.3.2`: Apply modal detour routing factors (1.25 road detour factor, 1.05 air routing).
   - `TASK 2.3.3`: Cache and store calculated segment distances in 'distance_estimee_km'.
4. **FEAT 2.4: Journey Quality & Anomaly Detection** (Linked: `US_2.4.1`)
   - `TASK 2.4.1`: Implement transit velocity checks identifying unrealistic speeds or negative transit times.
   - `TASK 2.4.2`: Build reconciliation rule engine to impute missing intermediate transit hubs for standard corridors.
   - `TASK 2.4.3`: Generate automated journey reconstruction quality report with error flagging.

---

### EPIC 3: CO2 Emission Factors Harmonization & Calculation Engine
1. **FEAT 3.1: ADEME Base Empreinte Factor Harmonization** (Linked: `US_3.1.1`)
   - `TASK 3.1.1`: Extract and curate official ADEME carbon factors for LCV, heavy truck, air freight, and electric cargo bike.
   - `TASK 3.1.2`: Normalize factor unit metrics (kgCO2e/km vs kgCO2e/t.km vs zero baseline).
   - `TASK 3.1.3`: Store factor reference data in table 'dim_emission_factors' with version and validity metadata.
2. **FEAT 3.2: Segment-Level CO2 Calculation Engine** (Linked: `US_3.2.1`)
   - `TASK 3.2.1`: Implement ton-kilometer emissions formula (distance_km * weight_t * factor) for heavy truck and air freight.
   - `TASK 3.2.2`: Implement vehicle-kilometer formula (distance_km * factor) with parcel allocation for LCV delivery legs.
   - `TASK 3.2.3`: Implement zero-carbon calculation logic for active transport modes (Bicycle / Walking).
3. **FEAT 3.3: Parcel-Level Emissions Aggregation** (Linked: `US_3.3.1`)
   - `TASK 3.3.1`: Build aggregation pipeline computing estimated_emissions = sum(segment_emissions).
   - `TASK 3.3.2`: Calculate parcel journey summary metrics including total distance and hub count (number_of_hubs).
   - `TASK 3.3.3`: Join parcel-level aggregated carbon metrics into the master tracking table.
4. **FEAT 3.4: Calculation Verification & Reference Walkthrough Tests** (Linked: `US_3.4.1`)
   - `TASK 3.4.1`: Write unit test verifying exact walkthrough calculation for Parcel P001 across its 4 segments.
   - `TASK 3.4.2`: Add edge-case test cases for high-weight parcels, zero-emission legs, and extreme distances.
   - `TASK 3.4.3`: Implement automated threshold assertions alerting on abnormal carbon outliers.

---

### EPIC 4: Unified Logistics & Carbon Dataset Construction
1. **FEAT 4.1: Target Schema Harmonization & Formatting** (Linked: `US_4.1.1`)
   - `TASK 4.1.1`: Build dataset assembler mapping tracking_id, date_premier_flashage, countries, weights, hubs, distance, mode, and emissions.
   - `TASK 4.1.2`: Standardize country identifiers into ISO 3166-1 alpha-2 format and normalize dates to ISO-8601.
   - `TASK 4.1.3`: Enforce strict data type casting and null representation rules across all fields.
2. **FEAT 4.2: Missing Data Treatment & Imputation** (Linked: `US_4.2.1`)
   - `TASK 4.2.1`: Profile missingness rates across weight, volume, and scan attributes.
   - `TASK 4.2.2`: Implement volumetric ratio and median imputation for missing parcel weights.
   - `TASK 4.2.3`: Quarantine unrecoverable records with detailed audit logging.
3. **FEAT 4.3: Analytical Export & Performance Optimization** (Linked: `US_4.3.1`)
   - `TASK 4.3.1`: Implement partitioned Parquet export by date and destination country.
   - `TASK 4.3.2`: Implement structured CSV export with comprehensive metadata header.
   - `TASK 4.3.3`: Generate automated data dictionary and summary profile report.

---

### EPIC 5: Machine Learning CO2 Prediction Model
1. **FEAT 5.1: Feature Engineering for Incomplete Journey Estimation** (Linked: `US_5.1.1`)
   - `TASK 5.1.1`: Engineer direct origin-destination geodesic distance, corridor flags, and parcel density features.
   - `TASK 5.1.2`: Encode categorical features including origin country, destination country, and service tier.
   - `TASK 5.1.3`: Construct verified training, validation, and test datasets from complete reconstructed journeys.
2. **FEAT 5.2: Model Training, Evaluation & Cross-Validation** (Linked: `US_5.2.1`)
   - `TASK 5.2.1`: Train baseline linear regression and tree-based ensemble models (Random Forest / LightGBM).
   - `TASK 5.2.2`: Perform hyperparameter tuning and 5-fold cross-validation on emissions regression.
   - `TASK 5.2.3`: Evaluate error metrics (RMSE, MAE, R2) and calculate feature importance.
3. **FEAT 5.3: Batch Prediction & ml_emissions Integration** (Linked: `US_5.3.1`)
   - `TASK 5.3.1`: Build batch inference pipeline loading the trained regression model artifact.
   - `TASK 5.3.2`: Populate ml_emissions column for parcels missing detailed scan journeys.
   - `TASK 5.3.3`: Compute prediction uncertainty intervals and confidence scores for each estimated value.

---

### EPIC 6: Carbon Footprint Analytics, Reporting & Interactive Simulator
1. **FEAT 6.1: Carbon Footprint Analytics & KPI Generation** (Linked: `US_6.1.1`)
   - `TASK 6.1.1`: Aggregate total and average carbon emissions grouped by transport mode and carrier.
   - `TASK 6.1.2`: Compute carbon intensity KPIs (gCO2e per ton-km and average kgCO2e per parcel) per lane.
   - `TASK 6.1.3`: Identify top 10 carbon-emitting logistics corridors and modal bottlenecks.
2. **FEAT 6.2: Modal Shift & Eco-Routing Scenario Simulator** (Linked: `US_6.2.1`)
   - `TASK 6.2.1`: Build simulation function allowing substitution of segment transport modes.
   - `TASK 6.2.2`: Compute delta CO2 savings and percentage reductions for simulated scenarios.
   - `TASK 6.2.3`: Generate scenario comparison summary tables for operational decision-making.
3. **FEAT 6.3: Interactive Sustainability Dashboard** (Linked: `US_6.3.1`)
   - `TASK 6.3.1`: Develop interactive dashboard web interface with KPI summary cards and modal charts.
   - `TASK 6.3.2`: Add interactive scenario simulator controls allowing users to test modal shift parameters.
   - `TASK 6.3.3`: Implement automated export of carbon reports and visualization charts.

---

## Project Execution Roadmap (Phases 2 – 8)

| Phase | Focus | Core Deliverable Produced | Key Artifacts |
| :--- | :--- | :--- | :--- |
| **Phase 2** | Synthetic Data & Reference Setup | Internal ERP/Scans/TMS feeds & ADEME reference | `generate_raw_data.py`, raw CSVs in `data/` & `reference/` |
| **Phase 3** | Relational Database & Ingestion | **Deliverable 1:** Structured database (`city`, `fleet`, `order`, `tracking`) | `schema.sql`, `ingest.py`, `smart_logistics.db` |
| **Phase 4** | Multi-Modal Journey Reconstruction | **Core Challenge:** Multi-segment journey linking & mode inference | `reconstruct_journey.py`, `journey_segments.csv` |
| **Phase 5** | $\text{CO}_2$ Calculation & Master Dataset | **Deliverable 2:** Unified & clean 10-column dataset | `calculate_emissions.py`, `test_emissions.py`, `master_parcel_emissions.csv` |
| **Phase 6** | ML Predictive Modeling | **Deliverable 4:** Predictive model for incomplete data (`ml_emissions`) | `train_model.py`, `predict_emissions.py`, evaluation report |
| **Phase 7** | Carbon Analytics & Flow Insights | **Deliverable 3:** Emissions analysis by mode, flow, and corridor | `analytics.py`, KPI reports, modal summaries |
| **Phase 8** | Scenario Simulator & Dashboard | **Deliverable 5:** Interactive Simulator & Visual Dashboard | `dashboard.py`, `dashboard_template.html`, `output/dashboard.html` |

---

## Deliverables Quick Reference

1. **Deliverable 1: Structured Database**
   - SQLite DB: [`second_proj/data/smart_logistics.db`](file:///Users/nefelim584/PycharmProjects/Data_Wrangling/second_proj/data/smart_logistics.db)
   - Schema: [`second_proj/schema.sql`](file:///Users/nefelim584/PycharmProjects/Data_Wrangling/second_proj/schema.sql)
   - ETL Pipeline: `python3 second_proj/ingest.py`
2. **Deliverable 2: Unified and Clean Master Dataset**
   - Master CSV: [`second_proj/output/master_parcel_emissions.csv`](file:///Users/nefelim584/PycharmProjects/Data_Wrangling/second_proj/output/master_parcel_emissions.csv)
   - Calculation Engine: `python3 second_proj/calculate_emissions.py`
   - Unit Tests: `python3 -m unittest second_proj/test_emissions.py`
3. **Deliverable 3: $\text{CO}_2$ Analysis by Mode, Flow & Corridor**
   - Carbon Report: [`second_proj/output/carbon_kpis_report.md`](file:///Users/nefelim584/PycharmProjects/Data_Wrangling/second_proj/output/carbon_kpis_report.md)
   - Modal Summary: [`second_proj/output/emissions_by_mode.csv`](file:///Users/nefelim584/PycharmProjects/Data_Wrangling/second_proj/output/emissions_by_mode.csv)
   - Corridor Flows: [`second_proj/output/emissions_by_corridor.csv`](file:///Users/nefelim584/PycharmProjects/Data_Wrangling/second_proj/output/emissions_by_corridor.csv)
   - Analytics Pipeline: `python3 second_proj/analytics.py`
4. **Deliverable 4: Predictive Machine Learning Model**
   - Model Evaluation Report: [`second_proj/output/model_evaluation_report.md`](file:///Users/nefelim584/PycharmProjects/Data_Wrangling/second_proj/output/model_evaluation_report.md)
   - Trained Model Artifact: [`second_proj/output/model_artifact.json`](file:///Users/nefelim584/PycharmProjects/Data_Wrangling/second_proj/output/model_artifact.json)
   - Train / Inference Pipelines: `python3 second_proj/train_model.py` / `python3 second_proj/predict_emissions.py`
5. **Deliverable 5: Interactive Simulator & Dashboard**
   - Standalone Application: [`second_proj/output/dashboard.html`](file:///Users/nefelim584/PycharmProjects/Data_Wrangling/second_proj/output/dashboard.html)
   - Dashboard Compiler: `python3 second_proj/dashboard.py`

