## Phase 0 - Description of the project 

### PROJECT EXAMPLE: Smart Logistics $\text{CO}_2$ Calculator

## Overview
**Goal:** Transform scattered logistics data into a reliable estimate of the carbon footprint per parcel.

**Core Project Challenge:** Reconstruct the parcel's actual journey before calculating its $\text{CO}_2$ emissions.

---

## 1. High-Level Architecture & Workflow

### Processing Pipeline
$$\text{DATA} \longrightarrow \text{PREPARATION} \longrightarrow \text{CO}_2 \text{ CALCULATION} \longrightarrow \text{DELIVERABLES}$$

* **Data:** ERP • scans • carriers
* **Preparation:** clean • link • enrich
* **$\text{CO}_2$ Calculation:** segment $\rightarrow$ parcel
* **Deliverables:** dataset • analysis • tool

### End-to-End Progression
$$\text{Data} \longrightarrow \text{Preparation} \longrightarrow \text{Calculation} \longrightarrow \text{Analysis} \longrightarrow \text{Prediction} \longrightarrow \text{Business tool}$$

---

## 2. Logistics Journey (Multi-Modal Reconstruction)

A parcel may use several modes of transport. The final footprint depends on each segment of the journey. Transport mode is therefore not a single simple column: the journey segments must first be reconstructed.

```
[ Warehouse ] 
      │ 
      ▼  Truck (35 km)
[  Airport  ] 
      │ 
      ▼  Air freight (1 200 km)
[ Regional hub ] 
      │ 
      ▼  Truck (180 km)
[ Local depot ] 
      │ 
      ▼  Bicycle / LCV (8 km)
[  Customer ]
```

* **For each segment:** $\text{Origin} \bullet \text{destination} \bullet \text{mode} \bullet \text{distance} \bullet \text{weight} \bullet \text{emission factor}$
* **Aggregation rule:** $\text{Parcel emissions} = \sum(\text{emissions calculated across all segments})$

---

## 3. Data Sources: Internal + External Reference Data

A business project combines several systems, formats, and levels of data quality.

$$\text{Internal data} + \text{external data} \longrightarrow \text{enriched, calculable journey}$$

### Internal Systems
* **ERP / SAP:** parcel • customer • weight • dimensions
* **Scans:** dates • times • hubs • location
* **TMS / carriers:** routes • services • modes

### External Reference Data
* **ADEME – Base Empreinte®:** official emission factors
* **Geographic data:** GPS coordinates • hubs
* **Distance API:** estimated / actual road distance

*Real examples from report:*
* **LCV:** $0.311\text{ kgCO}_2\text{e/km}$
* **Articulated heavy truck:** $0.0823\text{ kgCO}_2\text{e/t.km}$

---

## 4. Final Dataset Schema

The final dataset is built progressively: $\text{raw data} \rightarrow \text{enriched data} \rightarrow \text{calculated variables}$.

| Column | Description | Source / Calculation |
| :--- | :--- | :--- |
| `tracking_id` | Unique parcel identifier | ERP / internal system |
| `date_premier_flashage` | First scan event / timestamp | Logistics events |
| `origin_country / destination` | Standardized country codes | ERP + country reference data |
| `weight_kg / volume_m3` | Parcel characteristics | ERP + calculation |
| `number_of_hubs` | Number of hubs crossed | Scans |
| `distance_estimee_km` | Distance per segment / journey | GPS / API de distance |
| `mode_transport` | Mode used on each segment | TMS / carriers |
| `facteur_emission` | Factor adapted to transport mode / vehicle | ADEME – Base Empreinte® |
| `estimated_emissions` | $\text{CO}_2$ calculated then aggregated by parcel | Derived calculation |
| `ml_emissions` | $\text{CO}_2$ predicted when data is incomplete | Predictive model |

---

## 5. Calculation Walkthrough Example (Parcel P001)

> **Important:** Emission-factor units vary by mode (per km, t.km, passenger.km, etc.). Data wrangling must harmonize the calculation logic.

| Segment | Mode | Distance | Weight | Factor Used | Emissions |
| :---: | :--- | :---: | :---: | :--- | :--- |
| **1** | Light Commercial Vehicle (LCV) | $35\text{ km}$ | $8\text{ kg}$ | $0.311\text{ kgCO}_2\text{e/km}$ | $10.89\text{ kgCO}_2\text{e}$ |
| **2** | Air freight | $1\,200\text{ km}$ | $8\text{ kg}$ | $0.50\text{ kgCO}_2\text{e/t.km}$ | $4.80\text{ kgCO}_2\text{e}$ |
| **3** | Heavy truck | $180\text{ km}$ | $8\text{ kg}$ | $0.0823\text{ kgCO}_2\text{e/t.km}$ | $0.12\text{ kgCO}_2\text{e}$ |
| **4** | Bicycle | $8\text{ km}$ | $8\text{ kg}$ | $0.00$ | $0.00\text{ kgCO}_2\text{e}$ |

$$\mathbf{Parcel\ P001 \longrightarrow 4\ segments \longrightarrow estimated\ total\ CO_2 \approx 15.81\ kgCO_2e}$$

---

## 6. Project Deliverables

Outputs produced at the end of the Data Wrangling project:

1. **Structured database:** city • fleet • order • tracking tables
2. **Unified and clean dataset:** weight • distance • mode • factors • emissions
3. **$\text{CO}_2$ analysis:** emissions by parcel, journey, mode, or flow
4. **Predictive model:** estimate $\text{CO}_2$ when some data is missing
5. **Simulator / dashboard:** compare scenarios and present results



# Phase 1 - preparation 

- Generate csv table with such fuilds:
  - EPIC (List of EPICS for the project, not more than 7)
  - User story (list of user stories in format US_1.1.1)
  - Features (list of features)
  -Dev tasks (list of Dev tasks)
Rules:
- Each EPIC has:
  - Name (E.g - EPIC 1: International Survey Data Ingestion)
  - List of connected Features (not more than 5)
- Each User story has:
  - Name (E.g - US 1.1.1)
  - Description (E.g - As a Data Engineer, I want to automatically ingest the French Excel survey files so that French satisfaction data is available on the centralized platform.)
  - Connection to the correct EPIC (E.g - User stories from 1.1.1 to 1.5.1 are connected to the EPIC 1)
- Each Feature has:
  - Name (E.g - FEAT 1.1: France Excel Ingestion)
  - Connection to the selected User story (E.g - FEAT 1.1 connects to the US_1.1.1, FEAT 1.2 connects to the US_1.2.1 and etc.)
  - List of Dev tasks associated with this feature (not more than 4)
- Each Dev task has:
  - Name (E.g - Create sample France Excel survey file and identify source columns (survey_id, date, product, service, rating).)
  - Corresponding Feature 


## Phase 2 
- To be done

