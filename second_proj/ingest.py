"""
Automated Ingestion & ETL Pipeline for Smart Logistics CO2 Calculator.
Deliverable 1: Structured database (city, fleet, order, tracking tables).

Loads staged raw data and reference catalogs into SQLite database (smart_logistics.db)
with strict type casting, referential integrity verification, and boundary validation.
"""

import csv
import os
import sqlite3
import sys

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
REF_DIR = os.path.join(BASE_DIR, "reference")
DB_PATH = os.path.join(DATA_DIR, "smart_logistics.db")
SCHEMA_PATH = os.path.join(BASE_DIR, "schema.sql")

def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON;")
    conn.row_factory = sqlite3.Row
    return conn

def init_database(conn):
    print("Initializing database schema from schema.sql...")
    with open(SCHEMA_PATH, "r", encoding="utf-8") as f:
        schema_sql = f.read()
    conn.executescript(schema_sql)
    conn.commit()
    print("Schema initialized successfully.")

def ingest_hubs(conn):
    filepath = os.path.join(REF_DIR, "logistics_network_hubs.csv")
    print(f"Ingesting hubs from {filepath}...")
    cursor = conn.cursor()
    count = 0
    with open(filepath, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            cursor.execute("""
                INSERT OR REPLACE INTO dim_city_hubs 
                (hub_id, hub_name, hub_type, city, country_code, latitude, longitude)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                row["hub_id"].strip(),
                row["hub_name"].strip(),
                row["hub_type"].strip(),
                row["city"].strip(),
                row["country_code"].strip(),
                float(row["latitude"]),
                float(row["longitude"])
            ))
            count += 1
    conn.commit()
    print(f"-> Ingested {count} records into dim_city_hubs.")
    return count

def ingest_carriers(conn):
    filepath = os.path.join(DATA_DIR, "raw_tms_carriers.csv")
    print(f"Ingesting TMS fleet carriers from {filepath}...")
    cursor = conn.cursor()
    count = 0
    with open(filepath, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            cursor.execute("""
                INSERT OR REPLACE INTO dim_fleet_carriers 
                (carrier_id, carrier_name, vehicle_type, fuel_type, euro_class, capacity_tons, service_tier)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                row["carrier_id"].strip(),
                row["carrier_name"].strip(),
                row["vehicle_type"].strip(),
                row["fuel_type"].strip(),
                row["euro_class"].strip(),
                float(row["capacity_tons"]),
                row["service_tier"].strip()
            ))
            count += 1
    conn.commit()
    print(f"-> Ingested {count} records into dim_fleet_carriers.")
    return count

def ingest_emission_factors(conn):
    filepath = os.path.join(REF_DIR, "ademe_emission_factors.csv")
    print(f"Ingesting ADEME emission factors from {filepath}...")
    cursor = conn.cursor()
    count = 0
    with open(filepath, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            cursor.execute("""
                INSERT OR REPLACE INTO dim_emission_factors 
                (mode_transport, vehicle_type, unit, emission_factor, ademe_identifier, source_reference, notes)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                row["mode_transport"].strip(),
                row["vehicle_type"].strip(),
                row["unit"].strip(),
                float(row["emission_factor"]),
                row["ademe_identifier"].strip(),
                row["source_reference"].strip(),
                row.get("notes", "").strip()
            ))
            count += 1
    conn.commit()
    print(f"-> Ingested {count} records into dim_emission_factors.")
    return count

def ingest_orders(conn):
    filepath = os.path.join(DATA_DIR, "raw_erp_orders.csv")
    print(f"Ingesting ERP parcel orders from {filepath}...")
    cursor = conn.cursor()
    count = 0
    with open(filepath, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            weight_val = row["weight_kg"].strip()
            weight = float(weight_val) if weight_val else None
            cursor.execute("""
                INSERT OR REPLACE INTO fact_orders 
                (tracking_id, order_date, customer_id, origin_city, origin_country, 
                 destination_city, destination_country, weight_kg, volume_m3, service_tier, declared_value_eur)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                row["tracking_id"].strip(),
                row["order_date"].strip(),
                row["customer_id"].strip(),
                row["origin_city"].strip(),
                row["origin_country"].strip(),
                row["destination_city"].strip(),
                row["destination_country"].strip(),
                weight,
                float(row["volume_m3"]),
                row["service_tier"].strip(),
                float(row["declared_value_eur"])
            ))
            count += 1
    conn.commit()
    print(f"-> Ingested {count} records into fact_orders.")
    return count

def ingest_scans(conn):
    filepath = os.path.join(DATA_DIR, "raw_tracking_scans.csv")
    print(f"Ingesting checkpoint tracking scans from {filepath}...")
    cursor = conn.cursor()
    # Clear existing scans for clean reload
    cursor.execute("DELETE FROM fact_tracking_scans;")
    
    batch = []
    count = 0
    with open(filepath, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            batch.append((
                row["tracking_id"].strip(),
                row["timestamp"].strip(),
                row["hub_id"].strip(),
                row["event_type"].strip(),
                row["scanner_device_id"].strip()
            ))
            if len(batch) >= 1000:
                cursor.executemany("""
                    INSERT INTO fact_tracking_scans 
                    (tracking_id, timestamp, hub_id, event_type, scanner_device_id)
                    VALUES (?, ?, ?, ?, ?)
                """, batch)
                count += len(batch)
                batch = []
        if batch:
            cursor.executemany("""
                INSERT INTO fact_tracking_scans 
                (tracking_id, timestamp, hub_id, event_type, scanner_device_id)
                VALUES (?, ?, ?, ?, ?)
            """, batch)
            count += len(batch)
    conn.commit()
    print(f"-> Ingested {count} records into fact_tracking_scans.")
    return count

def run_data_quality_checks(conn):
    print("\n--- Running Data Quality & Integrity Checks ---")
    cursor = conn.cursor()

    # 1. Referential integrity: Scans with unmapped hubs
    cursor.execute("""
        SELECT COUNT(*) as orphan_hubs 
        FROM fact_tracking_scans s 
        LEFT JOIN dim_city_hubs h ON s.hub_id = h.hub_id 
        WHERE h.hub_id IS NULL;
    """)
    orphan_hubs = cursor.fetchone()["orphan_hubs"]
    assert orphan_hubs == 0, f"Error: Found {orphan_hubs} scans referencing unknown hubs!"
    print("[PASS] Referential integrity: All tracking scan hubs are valid and mapped.")

    # 2. Referential integrity: Scans with unmapped orders
    cursor.execute("""
        SELECT COUNT(*) as orphan_orders 
        FROM fact_tracking_scans s 
        LEFT JOIN fact_orders o ON s.tracking_id = o.tracking_id 
        WHERE o.tracking_id IS NULL;
    """)
    orphan_orders = cursor.fetchone()["orphan_orders"]
    assert orphan_orders == 0, f"Error: Found {orphan_orders} scans referencing unknown orders!"
    print("[PASS] Referential integrity: All tracking scans reference valid orders.")

    # 3. Coordinate bounds verification
    cursor.execute("""
        SELECT COUNT(*) as invalid_coords 
        FROM dim_city_hubs 
        WHERE latitude < -90.0 OR latitude > 90.0 OR longitude < -180.0 OR longitude > 180.0;
    """)
    invalid_coords = cursor.fetchone()["invalid_coords"]
    assert invalid_coords == 0, f"Error: Found {invalid_coords} hubs with invalid GPS coordinates!"
    print("[PASS] Boundary verification: All hub GPS coordinates within valid ranges.")

    # 4. Verify benchmark parcel P001 exists and has correct scan history
    cursor.execute("SELECT * FROM fact_orders WHERE tracking_id = 'P001';")
    p001_order = cursor.fetchone()
    assert p001_order is not None, "Error: Benchmark parcel P001 missing from fact_orders!"
    assert p001_order["weight_kg"] == 8.0, f"Error: P001 weight must be 8.0 kg, got {p001_order['weight_kg']}"

    cursor.execute("""
        SELECT COUNT(*) as p001_scans 
        FROM fact_tracking_scans 
        WHERE tracking_id = 'P001';
    """)
    p001_scans = cursor.fetchone()["p001_scans"]
    assert p001_scans == 8, f"Error: P001 expected 8 scan events, got {p001_scans}"
    print("[PASS] Benchmark verification: Parcel P001 present with 8 scan events.")

    # 5. Table counts report
    tables = ["dim_city_hubs", "dim_fleet_carriers", "dim_emission_factors", "fact_orders", "fact_tracking_scans"]
    print("\nDatabase Table Summary:")
    for t in tables:
        cursor.execute(f"SELECT COUNT(*) as cnt FROM {t};")
        cnt = cursor.fetchone()["cnt"]
        print(f"  - {t}: {cnt} records")

    print("\nAll quality and integrity checks passed successfully!")

def main():
    conn = get_connection()
    try:
        init_database(conn)
        ingest_hubs(conn)
        ingest_carriers(conn)
        ingest_emission_factors(conn)
        ingest_orders(conn)
        ingest_scans(conn)
        run_data_quality_checks(conn)
    finally:
        conn.close()

if __name__ == "__main__":
    main()
