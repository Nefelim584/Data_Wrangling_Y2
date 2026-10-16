"""
Unit Test Suite for Smart Logistics CO2 Calculator.
Validates Deliverable 2 and the Walkthrough Calculation (Parcel P001 = 15.81 kgCO2e).
"""

import os
import sqlite3
import unittest

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
OUTPUT_DIR = os.path.join(BASE_DIR, "output")
DB_PATH = os.path.join(DATA_DIR, "smart_logistics.db")
MASTER_CSV_PATH = os.path.join(OUTPUT_DIR, "master_parcel_emissions.csv")

class TestCO2Emissions(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.conn = sqlite3.connect(DB_PATH)
        cls.conn.row_factory = sqlite3.Row

    @classmethod
    def tearDownClass(cls):
        cls.conn.close()

    def test_01_p001_walkthrough_segments(self):
        """Verify Parcel P001 has exactly 4 segments with walkthrough parameters."""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT segment_order, mode_transport, distance_km, weight_kg, segment_emissions
            FROM fact_journey_segments
            WHERE tracking_id = 'P001'
            ORDER BY segment_order ASC;
        """)
        segments = cursor.fetchall()
        self.assertEqual(len(segments), 4, "Parcel P001 must have exactly 4 segments.")

        # Segment 1: LCV 35 km -> 10.89 kgCO2e
        seg1 = segments[0]
        self.assertEqual(seg1["mode_transport"], "LCV")
        self.assertAlmostEqual(seg1["distance_km"], 35.0, places=1)
        self.assertAlmostEqual(seg1["segment_emissions"], 10.89, places=2)

        # Segment 2: Air freight 1200 km, 8 kg -> 4.80 kgCO2e
        seg2 = segments[1]
        self.assertEqual(seg2["mode_transport"], "AIR_FREIGHT")
        self.assertAlmostEqual(seg2["distance_km"], 1200.0, places=1)
        self.assertAlmostEqual(seg2["segment_emissions"], 4.80, places=2)

        # Segment 3: Heavy truck 180 km, 8 kg -> 0.12 kgCO2e
        seg3 = segments[2]
        self.assertEqual(seg3["mode_transport"], "HEAVY_TRUCK")
        self.assertAlmostEqual(seg3["distance_km"], 180.0, places=1)
        self.assertAlmostEqual(seg3["segment_emissions"], 0.12, places=2)

        # Segment 4: Bicycle 8 km, 8 kg -> 0.00 kgCO2e
        seg4 = segments[3]
        self.assertEqual(seg4["mode_transport"], "BICYCLE")
        self.assertAlmostEqual(seg4["distance_km"], 8.0, places=1)
        self.assertAlmostEqual(seg4["segment_emissions"], 0.00, places=2)

    def test_02_p001_total_emissions(self):
        """Verify total estimated CO2 emissions for P001 equals ~15.81 kgCO2e."""
        cursor = self.conn.cursor()
        cursor.execute("SELECT estimated_emissions FROM master_parcel_emissions WHERE tracking_id = 'P001';")
        row = cursor.fetchone()
        self.assertIsNotNone(row, "P001 missing from master_parcel_emissions table")
        total_co2 = row["estimated_emissions"]
        self.assertAlmostEqual(total_co2, 15.81, delta=0.05, msg="P001 total CO2 should equal 15.81 kgCO2e")

    def test_03_non_negative_emissions(self):
        """Verify no negative emissions exist in segments or master table."""
        cursor = self.conn.cursor()
        cursor.execute("SELECT COUNT(*) as neg_segs FROM fact_journey_segments WHERE segment_emissions < 0;")
        self.assertEqual(cursor.fetchone()["neg_segs"], 0, "Found negative segment emissions!")

        cursor.execute("SELECT COUNT(*) as neg_parcels FROM master_parcel_emissions WHERE estimated_emissions < 0;")
        self.assertEqual(cursor.fetchone()["neg_parcels"], 0, "Found negative parcel emissions!")

    def test_04_bicycle_zero_emissions(self):
        """Verify active mobility (Bicycle) segments produce zero carbon emissions."""
        cursor = self.conn.cursor()
        cursor.execute("SELECT COUNT(*) as non_zero_bike FROM fact_journey_segments WHERE mode_transport = 'BICYCLE' AND segment_emissions != 0.0;")
        self.assertEqual(cursor.fetchone()["non_zero_bike"], 0, "Bicycle legs must have 0.0 emissions.")

    def test_05_master_schema_compliance(self):
        """Verify master dataset table contains all required columns."""
        cursor = self.conn.cursor()
        cursor.execute("PRAGMA table_info(master_parcel_emissions);")
        columns = [r["name"] for r in cursor.fetchall()]
        expected_cols = [
            "tracking_id", "date_premier_flashage", "origin_country", "destination_country",
            "weight_kg", "volume_m3", "number_of_hubs", "distance_estimee_km",
            "mode_transport", "facteur_emission", "estimated_emissions", "ml_emissions"
        ]
        for col in expected_cols:
            self.assertIn(col, columns, f"Expected column {col} missing from master table!")

    def test_06_csv_export_exists(self):
        """Verify master dataset CSV file exists and has rows."""
        self.assertTrue(os.path.exists(MASTER_CSV_PATH), "master_parcel_emissions.csv not found")
        with open(MASTER_CSV_PATH, "r", encoding="utf-8") as f:
            lines = f.readlines()
        self.assertEqual(len(lines), 1501, "Expected header + 1500 records in master CSV")

if __name__ == "__main__":
    unittest.main()
