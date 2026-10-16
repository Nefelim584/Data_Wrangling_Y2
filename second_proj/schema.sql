-- ====================================================================
-- Smart Logistics CO2 Calculator - Relational Database Schema
-- Deliverable 1: Structured database (city, fleet, order, tracking)
-- Compatible with SQLite and PostgreSQL
-- ====================================================================

-- 1. Dimension: Logistics Network Hubs & Cities
CREATE TABLE IF NOT EXISTS dim_city_hubs (
    hub_id TEXT PRIMARY KEY,
    hub_name TEXT NOT NULL,
    hub_type TEXT NOT NULL CHECK(hub_type IN ('WAREHOUSE', 'AIRPORT', 'REGIONAL_HUB', 'LOCAL_DEPOT')),
    city TEXT NOT NULL,
    country_code TEXT NOT NULL,
    latitude REAL NOT NULL CHECK(latitude BETWEEN -90.0 AND 90.0),
    longitude REAL NOT NULL CHECK(longitude BETWEEN -180.0 AND 180.0)
);

-- 2. Dimension: TMS Carriers & Fleet Specifications
CREATE TABLE IF NOT EXISTS dim_fleet_carriers (
    carrier_id TEXT PRIMARY KEY,
    carrier_name TEXT NOT NULL,
    vehicle_type TEXT NOT NULL,
    fuel_type TEXT NOT NULL,
    euro_class TEXT NOT NULL,
    capacity_tons REAL NOT NULL CHECK(capacity_tons > 0),
    service_tier TEXT NOT NULL
);

-- 3. Dimension: ADEME Base Empreinte Official Emission Factors
CREATE TABLE IF NOT EXISTS dim_emission_factors (
    factor_id INTEGER PRIMARY KEY AUTOINCREMENT,
    mode_transport TEXT NOT NULL,
    vehicle_type TEXT NOT NULL,
    unit TEXT NOT NULL CHECK(unit IN ('kgCO2e/km', 'kgCO2e/t.km')),
    emission_factor REAL NOT NULL CHECK(emission_factor >= 0),
    ademe_identifier TEXT UNIQUE NOT NULL,
    source_reference TEXT NOT NULL,
    notes TEXT
);

-- 4. Fact Table: ERP Parcel Orders
CREATE TABLE IF NOT EXISTS fact_orders (
    tracking_id TEXT PRIMARY KEY,
    order_date DATE NOT NULL,
    customer_id TEXT NOT NULL,
    origin_city TEXT NOT NULL,
    origin_country TEXT NOT NULL,
    destination_city TEXT NOT NULL,
    destination_country TEXT NOT NULL,
    weight_kg REAL CHECK(weight_kg IS NULL OR weight_kg > 0),
    volume_m3 REAL CHECK(volume_m3 > 0),
    service_tier TEXT NOT NULL,
    declared_value_eur REAL CHECK(declared_value_eur >= 0)
);

-- 5. Fact Table: Physical Logistics Checkpoint Scans
CREATE TABLE IF NOT EXISTS fact_tracking_scans (
    scan_id INTEGER PRIMARY KEY AUTOINCREMENT,
    tracking_id TEXT NOT NULL,
    timestamp DATETIME NOT NULL,
    hub_id TEXT NOT NULL,
    event_type TEXT NOT NULL CHECK(event_type IN ('PICKUP', 'ARRIVAL_HUB', 'DEPARTURE_HUB', 'OUT_FOR_DELIVERY', 'DELIVERED')),
    scanner_device_id TEXT NOT NULL,
    FOREIGN KEY (tracking_id) REFERENCES fact_orders (tracking_id) ON DELETE CASCADE,
    FOREIGN KEY (hub_id) REFERENCES dim_city_hubs (hub_id)
);

-- Performance & Analytical Query Indexes
CREATE INDEX IF NOT EXISTS idx_scans_tracking_time ON fact_tracking_scans (tracking_id, timestamp);
CREATE INDEX IF NOT EXISTS idx_scans_hub ON fact_tracking_scans (hub_id);
CREATE INDEX IF NOT EXISTS idx_orders_customer ON fact_orders (customer_id);
CREATE INDEX IF NOT EXISTS idx_orders_corridor ON fact_orders (origin_country, destination_country);
CREATE INDEX IF NOT EXISTS idx_orders_date ON fact_orders (order_date);
