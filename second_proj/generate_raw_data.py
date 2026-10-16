"""
Synthetic Raw Data & Reference Generator for Smart Logistics CO2 Calculator.

Generates:
1. second_proj/reference/ademe_emission_factors.csv
2. second_proj/reference/logistics_network_hubs.csv
3. second_proj/data/raw_tms_carriers.csv
4. second_proj/data/raw_erp_orders.csv
5. second_proj/data/raw_tracking_scans.csv

Includes benchmark Parcel P001 matching the walkthrough:
- Segment 1: LCV (35 km, 8 kg, 0.311 kgCO2e/km -> 10.89 kgCO2e)
- Segment 2: Air freight (1,200 km, 8 kg, 0.50 kgCO2e/t.km -> 4.80 kgCO2e)
- Segment 3: Heavy truck (180 km, 8 kg, 0.0823 kgCO2e/t.km -> 0.12 kgCO2e)
- Segment 4: Bicycle (8 km, 8 kg, 0.00 kgCO2e/km -> 0.00 kgCO2e)
Total: ~15.81 kgCO2e
"""

import csv
import math
import os
import random
from datetime import datetime, timedelta

# Set seed for reproducible synthetic data
random.seed(42)

# Directory paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
REF_DIR = os.path.join(BASE_DIR, "reference")
OUTPUT_DIR = os.path.join(BASE_DIR, "output")

os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(REF_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)

# -------------------------------------------------------------
# 1. ADEME Emission Factors Reference
# -------------------------------------------------------------
def generate_ademe_factors():
    factors = [
        {
            "mode_transport": "LCV",
            "vehicle_type": "LCV_DIESEL",
            "unit": "kgCO2e/km",
            "emission_factor": 0.311,
            "ademe_identifier": "ADEME-FR-LCV-01",
            "source_reference": "ADEME Base Empreinte 2024 - VUL Diesel moyen",
            "notes": "Light commercial vehicle delivery van (<3.5t)"
        },
        {
            "mode_transport": "HEAVY_TRUCK",
            "vehicle_type": "HEAVY_TRUCK_ARTICULATED",
            "unit": "kgCO2e/t.km",
            "emission_factor": 0.0823,
            "ademe_identifier": "ADEME-FR-TRUCK-02",
            "source_reference": "ADEME Base Empreinte 2024 - Poids lourd articule >32t",
            "notes": "Articulated long-haul heavy freight truck"
        },
        {
            "mode_transport": "AIR_FREIGHT",
            "vehicle_type": "AIR_CARGO_FREIGHT",
            "unit": "kgCO2e/t.km",
            "emission_factor": 0.500,
            "ademe_identifier": "ADEME-FR-AIR-03",
            "source_reference": "ADEME Base Empreinte 2024 - Fret aerien moyen courrier",
            "notes": "Medium-haul dedicated cargo air freight"
        },
        {
            "mode_transport": "BICYCLE",
            "vehicle_type": "CARGO_BIKE_ELECTRIC",
            "unit": "kgCO2e/km",
            "emission_factor": 0.000,
            "ademe_identifier": "ADEME-FR-BIKE-04",
            "source_reference": "ADEME Base Empreinte 2024 - Velo cargo mecanique / electrique",
            "notes": "Active zero-carbon last-mile micro-mobility"
        },
        {
            "mode_transport": "ELECTRIC_LCV",
            "vehicle_type": "LCV_ELECTRIC",
            "unit": "kgCO2e/km",
            "emission_factor": 0.065,
            "ademe_identifier": "ADEME-FR-ELCV-05",
            "source_reference": "ADEME Base Empreinte 2024 - VUL 100% electrique",
            "notes": "Used for eco-routing modal shift simulation"
        },
        {
            "mode_transport": "RAIL_FREIGHT",
            "vehicle_type": "FREIGHT_TRAIN_ELECTRIC",
            "unit": "kgCO2e/t.km",
            "emission_factor": 0.018,
            "ademe_identifier": "ADEME-FR-RAIL-06",
            "source_reference": "ADEME Base Empreinte 2024 - Train de fret traction electrique",
            "notes": "Used for air-to-rail modal shift simulation"
        }
    ]

    filepath = os.path.join(REF_DIR, "ademe_emission_factors.csv")
    fieldnames = ["mode_transport", "vehicle_type", "unit", "emission_factor", "ademe_identifier", "source_reference", "notes"]
    with open(filepath, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(factors)
    print(f"Generated {len(factors)} ADEME factors at {filepath}")
    return factors

# -------------------------------------------------------------
# 2. Logistics Network Hubs & Coordinates Reference
# -------------------------------------------------------------
HUBS = [
    # France
    {"hub_id": "WH_CDG_01", "hub_name": "Roissy Central Fulfillment Warehouse", "hub_type": "WAREHOUSE", "city": "Paris", "country_code": "FR", "latitude": 49.0097, "longitude": 2.5479},
    {"hub_id": "APT_CDG", "hub_name": "Paris Charles de Gaulle Cargo Terminal", "hub_type": "AIRPORT", "city": "Paris", "country_code": "FR", "latitude": 49.0080, "longitude": 2.5500},
    {"hub_id": "HUB_PAR_01", "hub_name": "Paris Nord Regional Sorting Hub", "hub_type": "REGIONAL_HUB", "city": "Paris", "country_code": "FR", "latitude": 48.9100, "longitude": 2.3700},
    {"hub_id": "DEP_PAR_01", "hub_name": "Paris Center Urban Depot", "hub_type": "LOCAL_DEPOT", "city": "Paris", "country_code": "FR", "latitude": 48.8600, "longitude": 2.3400},
    
    {"hub_id": "WH_LYN_01", "hub_name": "Lyon Saint-Exupéry Warehouse", "hub_type": "WAREHOUSE", "city": "Lyon", "country_code": "FR", "latitude": 45.7200, "longitude": 5.0800},
    {"hub_id": "APT_LYS", "hub_name": "Lyon Airport Cargo Hub", "hub_type": "AIRPORT", "city": "Lyon", "country_code": "FR", "latitude": 45.7255, "longitude": 5.0811},
    {"hub_id": "HUB_LYN_01", "hub_name": "Lyon Rhône-Alpes Sorting Hub", "hub_type": "REGIONAL_HUB", "city": "Lyon", "country_code": "FR", "latitude": 45.7500, "longitude": 4.8500},
    {"hub_id": "DEP_LYN_01", "hub_name": "Lyon Villeurbanne Local Depot", "hub_type": "LOCAL_DEPOT", "city": "Lyon", "country_code": "FR", "latitude": 45.7700, "longitude": 4.8800},

    # Spain
    {"hub_id": "WH_MAD_01", "hub_name": "Madrid Coslada Logistics Park", "hub_type": "WAREHOUSE", "city": "Madrid", "country_code": "ES", "latitude": 40.4260, "longitude": -3.5600},
    {"hub_id": "APT_MAD", "hub_name": "Adolfo Suárez Madrid-Barajas Cargo Hub", "hub_type": "AIRPORT", "city": "Madrid", "country_code": "ES", "latitude": 40.4839, "longitude": -3.5680},
    {"hub_id": "HUB_MAD_01", "hub_name": "Madrid Central Sortation Hub", "hub_type": "REGIONAL_HUB", "city": "Madrid", "country_code": "ES", "latitude": 40.4168, "longitude": -3.7038},
    {"hub_id": "DEP_MAD_01", "hub_name": "Madrid Chamartín Last-Mile Depot", "hub_type": "LOCAL_DEPOT", "city": "Madrid", "country_code": "ES", "latitude": 40.4600, "longitude": -3.6900},

    {"hub_id": "WH_BCN_01", "hub_name": "Barcelona Port Logistics Platform", "hub_type": "WAREHOUSE", "city": "Barcelona", "country_code": "ES", "latitude": 41.3400, "longitude": 2.1300},
    {"hub_id": "APT_BCN", "hub_name": "Barcelona El Prat Cargo Hub", "hub_type": "AIRPORT", "city": "Barcelona", "country_code": "ES", "latitude": 41.2974, "longitude": 2.0833},
    {"hub_id": "HUB_BCN_01", "hub_name": "Barcelona Catalunya Sorting Hub", "hub_type": "REGIONAL_HUB", "city": "Barcelona", "country_code": "ES", "latitude": 41.3879, "longitude": 2.1699},
    {"hub_id": "DEP_BCN_01", "hub_name": "Barcelona Eixample Local Depot", "hub_type": "LOCAL_DEPOT", "city": "Barcelona", "country_code": "ES", "latitude": 41.3900, "longitude": 2.1600},

    # Germany
    {"hub_id": "WH_FRA_01", "hub_name": "Frankfurt Gateway Gardens Warehouse", "hub_type": "WAREHOUSE", "city": "Frankfurt", "country_code": "DE", "latitude": 50.0500, "longitude": 8.6000},
    {"hub_id": "APT_FRA", "hub_name": "Frankfurt CargoCity Airport", "hub_type": "AIRPORT", "city": "Frankfurt", "country_code": "DE", "latitude": 50.0379, "longitude": 8.5622},
    {"hub_id": "HUB_FRA_01", "hub_name": "Frankfurt Hessen Regional Hub", "hub_type": "REGIONAL_HUB", "city": "Frankfurt", "country_code": "DE", "latitude": 50.1109, "longitude": 8.6821},
    {"hub_id": "DEP_FRA_01", "hub_name": "Frankfurt West Local Depot", "hub_type": "LOCAL_DEPOT", "city": "Frankfurt", "country_code": "DE", "latitude": 50.1000, "longitude": 8.6500},

    {"hub_id": "WH_BER_01", "hub_name": "Berlin Schönefeld Logistics Center", "hub_type": "WAREHOUSE", "city": "Berlin", "country_code": "DE", "latitude": 52.3800, "longitude": 13.5200},
    {"hub_id": "APT_BER", "hub_name": "Berlin Brandenburg Air Cargo", "hub_type": "AIRPORT", "city": "Berlin", "country_code": "DE", "latitude": 52.3667, "longitude": 13.5033},
    {"hub_id": "HUB_BER_01", "hub_name": "Berlin Brandenburg Sorting Hub", "hub_type": "REGIONAL_HUB", "city": "Berlin", "country_code": "DE", "latitude": 52.5200, "longitude": 13.4050},
    {"hub_id": "DEP_BER_01", "hub_name": "Berlin Mitte Urban Depot", "hub_type": "LOCAL_DEPOT", "city": "Berlin", "country_code": "DE", "latitude": 52.5200, "longitude": 13.4100},

    # Morocco
    {"hub_id": "WH_CAS_01", "hub_name": "Casablanca Ain Sebaa Warehouse", "hub_type": "WAREHOUSE", "city": "Casablanca", "country_code": "MA", "latitude": 33.6000, "longitude": -7.5300},
    {"hub_id": "APT_CMN", "hub_name": "Casablanca Mohammed V Cargo Hub", "hub_type": "AIRPORT", "city": "Casablanca", "country_code": "MA", "latitude": 33.3675, "longitude": -7.5899},
    {"hub_id": "HUB_CAS_01", "hub_name": "Casablanca Regional Transit Hub", "hub_type": "REGIONAL_HUB", "city": "Casablanca", "country_code": "MA", "latitude": 33.5731, "longitude": -7.5898},
    {"hub_id": "DEP_CAS_01", "hub_name": "Casablanca Maarif Local Depot", "hub_type": "LOCAL_DEPOT", "city": "Casablanca", "country_code": "MA", "latitude": 33.5800, "longitude": -7.6300},

    # Canada
    {"hub_id": "WH_TOR_01", "hub_name": "Toronto Mississauga Logistics Center", "hub_type": "WAREHOUSE", "city": "Toronto", "country_code": "CA", "latitude": 43.6000, "longitude": -79.6500},
    {"hub_id": "APT_YYZ", "hub_name": "Toronto Pearson Cargo Terminal", "hub_type": "AIRPORT", "city": "Toronto", "country_code": "CA", "latitude": 43.6777, "longitude": -79.6248},
    {"hub_id": "HUB_TOR_01", "hub_name": "Toronto Ontario Sorting Hub", "hub_type": "REGIONAL_HUB", "city": "Toronto", "country_code": "CA", "latitude": 43.6532, "longitude": -79.3832},
    {"hub_id": "DEP_TOR_01", "hub_name": "Toronto Downtown Delivery Depot", "hub_type": "LOCAL_DEPOT", "city": "Toronto", "country_code": "CA", "latitude": 43.6500, "longitude": -79.3800},
]

def generate_hubs_reference():
    filepath = os.path.join(REF_DIR, "logistics_network_hubs.csv")
    fieldnames = ["hub_id", "hub_name", "hub_type", "city", "country_code", "latitude", "longitude"]
    with open(filepath, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(HUBS)
    print(f"Generated {len(HUBS)} hubs at {filepath}")
    return HUBS

# -------------------------------------------------------------
# 3. TMS Carriers Reference
# -------------------------------------------------------------
CARRIERS = [
    {"carrier_id": "CAR_EXP_01", "carrier_name": "FastColis Express Line", "vehicle_type": "LCV_VAN", "fuel_type": "DIESEL", "euro_class": "EURO_6", "capacity_tons": 1.2, "service_tier": "EXPRESS"},
    {"carrier_id": "CAR_STD_02", "carrier_name": "EuroFreight Road Haulage", "vehicle_type": "HEAVY_TRUCK_ARTICULATED", "fuel_type": "DIESEL", "euro_class": "EURO_6", "capacity_tons": 24.0, "service_tier": "STANDARD"},
    {"carrier_id": "CAR_AIR_03", "carrier_name": "TransEuro Air Cargo", "vehicle_type": "AIR_CARGO", "fuel_type": "JET_A1", "euro_class": "NONE", "capacity_tons": 50.0, "service_tier": "EXPRESS"},
    {"carrier_id": "CAR_ECO_04", "carrier_name": "GreenVelos Urban Delivery", "vehicle_type": "ELECTRIC_CARGO_BIKE", "fuel_type": "ELECTRIC", "euro_class": "ZERO_EMISSION", "capacity_tons": 0.25, "service_tier": "ECO"},
    {"carrier_id": "CAR_ELCV_05", "carrier_name": "CleanFleet Electric Logistics", "vehicle_type": "ELECTRIC_LCV", "fuel_type": "ELECTRIC", "euro_class": "ZERO_EMISSION", "capacity_tons": 1.0, "service_tier": "ECO"},
    {"carrier_id": "CAR_RAIL_06", "carrier_name": "EuroRail Intermodal Freight", "vehicle_type": "FREIGHT_TRAIN_ELECTRIC", "fuel_type": "ELECTRIC", "euro_class": "ZERO_EMISSION", "capacity_tons": 800.0, "service_tier": "STANDARD"},
]

def generate_tms_carriers():
    filepath = os.path.join(DATA_DIR, "raw_tms_carriers.csv")
    fieldnames = ["carrier_id", "carrier_name", "vehicle_type", "fuel_type", "euro_class", "capacity_tons", "service_tier"]
    with open(filepath, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(CARRIERS)
    print(f"Generated {len(CARRIERS)} TMS carriers at {filepath}")
    return CARRIERS

# -------------------------------------------------------------
# 4. ERP Orders & Tracking Scans Generator
# -------------------------------------------------------------
def haversine_km(lat1, lon1, lat2, lon2):
    R = 6371.0
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)
    a = math.sin(delta_phi / 2.0) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2.0) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c

def generate_orders_and_scans(num_parcels=1500):
    orders = []
    scans = []

    hubs_by_city = {}
    for hub in HUBS:
        city = hub["city"]
        if city not in hubs_by_city:
            hubs_by_city[city] = {}
        hubs_by_city[city][hub["hub_type"]] = hub

    cities = list(hubs_by_city.keys())

    # ---------------------------------------------------------
    # Benchmark Parcel P001 (Exact Walkthrough Compliance)
    # ---------------------------------------------------------
    p001_date = datetime(2026, 9, 15, 8, 30, 0)
    p001_order = {
        "tracking_id": "P001",
        "order_date": p001_date.strftime("%Y-%m-%d"),
        "customer_id": "CUST_WALKTHROUGH_01",
        "origin_city": "Paris",
        "origin_country": "FR",
        "destination_city": "Madrid",
        "destination_country": "ES",
        "weight_kg": 8.0,
        "volume_m3": 0.045,
        "service_tier": "EXPRESS",
        "declared_value_eur": 250.0
    }
    orders.append(p001_order)

    # Scans for P001 matching the 4 segments:
    # 1. Warehouse (WH_CDG_01) -> Airport (APT_CDG) [LCV: 35km]
    # 2. Airport (APT_CDG) -> Airport (APT_MAD) [Air: 1200km]
    # 3. Airport (APT_MAD) -> Local Depot (DEP_MAD_01) [Heavy Truck: 180km]
    # 4. Local Depot (DEP_MAD_01) -> Customer [Bicycle: 8km]
    t = p001_date
    scans.append({"tracking_id": "P001", "timestamp": t.strftime("%Y-%m-%dT%H:%M:%SZ"), "hub_id": "WH_CDG_01", "event_type": "PICKUP", "scanner_device_id": "SCAN_WH_01"})
    t += timedelta(hours=1, minutes=15)
    scans.append({"tracking_id": "P001", "timestamp": t.strftime("%Y-%m-%dT%H:%M:%SZ"), "hub_id": "APT_CDG", "event_type": "ARRIVAL_HUB", "scanner_device_id": "SCAN_APT_01"})
    t += timedelta(hours=2)
    scans.append({"tracking_id": "P001", "timestamp": t.strftime("%Y-%m-%dT%H:%M:%SZ"), "hub_id": "APT_CDG", "event_type": "DEPARTURE_HUB", "scanner_device_id": "SCAN_APT_02"})
    t += timedelta(hours=2, minutes=30)
    scans.append({"tracking_id": "P001", "timestamp": t.strftime("%Y-%m-%dT%H:%M:%SZ"), "hub_id": "APT_MAD", "event_type": "ARRIVAL_HUB", "scanner_device_id": "SCAN_MAD_01"})
    t += timedelta(hours=3)
    scans.append({"tracking_id": "P001", "timestamp": t.strftime("%Y-%m-%dT%H:%M:%SZ"), "hub_id": "APT_MAD", "event_type": "DEPARTURE_HUB", "scanner_device_id": "SCAN_MAD_02"})
    t += timedelta(hours=2, minutes=45)
    scans.append({"tracking_id": "P001", "timestamp": t.strftime("%Y-%m-%dT%H:%M:%SZ"), "hub_id": "DEP_MAD_01", "event_type": "ARRIVAL_HUB", "scanner_device_id": "SCAN_DEP_01"})
    t += timedelta(hours=1, minutes=30)
    scans.append({"tracking_id": "P001", "timestamp": t.strftime("%Y-%m-%dT%H:%M:%SZ"), "hub_id": "DEP_MAD_01", "event_type": "OUT_FOR_DELIVERY", "scanner_device_id": "SCAN_DEP_02"})
    t += timedelta(minutes=45)
    scans.append({"tracking_id": "P001", "timestamp": t.strftime("%Y-%m-%dT%H:%M:%SZ"), "hub_id": "DEP_MAD_01", "event_type": "DELIVERED", "scanner_device_id": "SCAN_MBL_01"})

    # ---------------------------------------------------------
    # Generate Remaining Parcels P002 to P{num_parcels}
    # ---------------------------------------------------------
    start_date = datetime(2026, 9, 1)
    
    for i in range(2, num_parcels + 1):
        tracking_id = f"P{i:04d}"
        orig_city = random.choice(cities)
        dest_city = random.choice([c for c in cities if c != orig_city] + [orig_city]) # some domestic, some international
        
        orig_country = hubs_by_city[orig_city]["WAREHOUSE"]["country_code"]
        dest_country = hubs_by_city[dest_city]["WAREHOUSE"]["country_code"]
        
        order_time = start_date + timedelta(days=random.randint(0, 40), hours=random.randint(6, 18), minutes=random.randint(0, 59))
        service_tier = random.choices(["STANDARD", "EXPRESS", "ECO"], weights=[0.55, 0.30, 0.15])[0]
        
        # Real-world weights: ~5% missing for imputation testing
        if random.random() < 0.05:
            weight_kg = None
        else:
            # Lognormal distribution around 3.5 kg
            weight_kg = round(min(50.0, max(0.2, random.lognormvariate(1.2, 0.8))), 2)
            
        volume_m3 = round((weight_kg if weight_kg else 4.0) * random.uniform(0.003, 0.008), 4)
        declared_value = round(random.uniform(15.0, 850.0), 2)
        
        orders.append({
            "tracking_id": tracking_id,
            "order_date": order_time.strftime("%Y-%m-%d"),
            "customer_id": f"CUST_{random.randint(1000, 9999)}",
            "origin_city": orig_city,
            "origin_country": orig_country,
            "destination_city": dest_city,
            "destination_country": dest_country,
            "weight_kg": weight_kg if weight_kg is not None else "",
            "volume_m3": volume_m3,
            "service_tier": service_tier,
            "declared_value_eur": declared_value
        })

        # -----------------------------------------------------
        # Generate Checkpoint Scans
        # ~10% have incomplete scans to test ML prediction
        # -----------------------------------------------------
        is_incomplete = (random.random() < 0.10)
        curr_time = order_time + timedelta(hours=random.randint(1, 4))
        
        orig_wh = hubs_by_city[orig_city]["WAREHOUSE"]
        orig_hub = hubs_by_city[orig_city].get("REGIONAL_HUB", orig_wh)
        orig_apt = hubs_by_city[orig_city].get("AIRPORT")
        
        dest_depot = hubs_by_city[dest_city].get("LOCAL_DEPOT", hubs_by_city[dest_city]["WAREHOUSE"])
        dest_hub = hubs_by_city[dest_city].get("REGIONAL_HUB", dest_depot)
        dest_apt = hubs_by_city[dest_city].get("AIRPORT")
        
        # Incomplete scenario: only pickup recorded
        if is_incomplete:
            scans.append({
                "tracking_id": tracking_id,
                "timestamp": curr_time.strftime("%Y-%m-%dT%H:%M:%SZ"),
                "hub_id": orig_wh["hub_id"],
                "event_type": "PICKUP",
                "scanner_device_id": f"SCAN_{orig_wh['hub_id']}_01"
            })
            continue

        # Complete multi-modal transit sequence
        is_air = (service_tier == "EXPRESS" and orig_country != dest_country and orig_apt and dest_apt)
        
        # 1. Pickup at origin warehouse
        scans.append({
            "tracking_id": tracking_id,
            "timestamp": curr_time.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "hub_id": orig_wh["hub_id"],
            "event_type": "PICKUP",
            "scanner_device_id": f"SCAN_{orig_wh['hub_id']}_01"
        })
        
        if is_air:
            # Transit to airport via LCV/truck
            curr_time += timedelta(hours=random.randint(1, 3))
            scans.append({"tracking_id": tracking_id, "timestamp": curr_time.strftime("%Y-%m-%dT%H:%M:%SZ"), "hub_id": orig_apt["hub_id"], "event_type": "ARRIVAL_HUB", "scanner_device_id": f"SCAN_{orig_apt['hub_id']}_01"})
            curr_time += timedelta(hours=random.randint(2, 4))
            scans.append({"tracking_id": tracking_id, "timestamp": curr_time.strftime("%Y-%m-%dT%H:%M:%SZ"), "hub_id": orig_apt["hub_id"], "event_type": "DEPARTURE_HUB", "scanner_device_id": f"SCAN_{orig_apt['hub_id']}_02"})
            
            # Flight leg
            flight_hours = max(2, int(haversine_km(orig_apt["latitude"], orig_apt["longitude"], dest_apt["latitude"], dest_apt["longitude"]) / 650.0))
            curr_time += timedelta(hours=flight_hours)
            scans.append({"tracking_id": tracking_id, "timestamp": curr_time.strftime("%Y-%m-%dT%H:%M:%SZ"), "hub_id": dest_apt["hub_id"], "event_type": "ARRIVAL_HUB", "scanner_device_id": f"SCAN_{dest_apt['hub_id']}_01"})
            curr_time += timedelta(hours=random.randint(2, 5))
            scans.append({"tracking_id": tracking_id, "timestamp": curr_time.strftime("%Y-%m-%dT%H:%M:%SZ"), "hub_id": dest_apt["hub_id"], "event_type": "DEPARTURE_HUB", "scanner_device_id": f"SCAN_{dest_apt['hub_id']}_02"})
        else:
            # Road leg via Regional sorting hubs
            curr_time += timedelta(hours=random.randint(2, 5))
            scans.append({"tracking_id": tracking_id, "timestamp": curr_time.strftime("%Y-%m-%dT%H:%M:%SZ"), "hub_id": orig_hub["hub_id"], "event_type": "ARRIVAL_HUB", "scanner_device_id": f"SCAN_{orig_hub['hub_id']}_01"})
            curr_time += timedelta(hours=random.randint(3, 8))
            scans.append({"tracking_id": tracking_id, "timestamp": curr_time.strftime("%Y-%m-%dT%H:%M:%SZ"), "hub_id": orig_hub["hub_id"], "event_type": "DEPARTURE_HUB", "scanner_device_id": f"SCAN_{orig_hub['hub_id']}_02"})
            
            if orig_hub != dest_hub:
                road_dist = haversine_km(orig_hub["latitude"], orig_hub["longitude"], dest_hub["latitude"], dest_hub["longitude"])
                transit_hours = max(3, int(road_dist / 65.0))
                curr_time += timedelta(hours=transit_hours)
                scans.append({"tracking_id": tracking_id, "timestamp": curr_time.strftime("%Y-%m-%dT%H:%M:%SZ"), "hub_id": dest_hub["hub_id"], "event_type": "ARRIVAL_HUB", "scanner_device_id": f"SCAN_{dest_hub['hub_id']}_01"})
                curr_time += timedelta(hours=random.randint(2, 6))
                scans.append({"tracking_id": tracking_id, "timestamp": curr_time.strftime("%Y-%m-%dT%H:%M:%SZ"), "hub_id": dest_hub["hub_id"], "event_type": "DEPARTURE_HUB", "scanner_device_id": f"SCAN_{dest_hub['hub_id']}_02"})

        # Final delivery leg from local depot
        curr_time += timedelta(hours=random.randint(2, 4))
        scans.append({"tracking_id": tracking_id, "timestamp": curr_time.strftime("%Y-%m-%dT%H:%M:%SZ"), "hub_id": dest_depot["hub_id"], "event_type": "ARRIVAL_HUB", "scanner_device_id": f"SCAN_{dest_depot['hub_id']}_01"})
        curr_time += timedelta(hours=random.randint(1, 3))
        scans.append({"tracking_id": tracking_id, "timestamp": curr_time.strftime("%Y-%m-%dT%H:%M:%SZ"), "hub_id": dest_depot["hub_id"], "event_type": "OUT_FOR_DELIVERY", "scanner_device_id": f"SCAN_{dest_depot['hub_id']}_02"})
        curr_time += timedelta(minutes=random.randint(20, 120))
        scans.append({"tracking_id": tracking_id, "timestamp": curr_time.strftime("%Y-%m-%dT%H:%M:%SZ"), "hub_id": dest_depot["hub_id"], "event_type": "DELIVERED", "scanner_device_id": f"SCAN_MBL_{random.randint(10, 99)}"})

    # Write orders CSV
    orders_path = os.path.join(DATA_DIR, "raw_erp_orders.csv")
    order_fields = ["tracking_id", "order_date", "customer_id", "origin_city", "origin_country", "destination_city", "destination_country", "weight_kg", "volume_m3", "service_tier", "declared_value_eur"]
    with open(orders_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=order_fields)
        writer.writeheader()
        writer.writerows(orders)
    print(f"Generated {len(orders)} ERP orders at {orders_path}")

    # Write scans CSV
    scans_path = os.path.join(DATA_DIR, "raw_tracking_scans.csv")
    scan_fields = ["tracking_id", "timestamp", "hub_id", "event_type", "scanner_device_id"]
    with open(scans_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=scan_fields)
        writer.writeheader()
        writer.writerows(scans)
    print(f"Generated {len(scans)} tracking scans at {scans_path}")

    return orders, scans

if __name__ == "__main__":
    print("Starting synthetic data generation for Smart Logistics CO2 Calculator...")
    generate_ademe_factors()
    generate_hubs_reference()
    generate_tms_carriers()
    orders, scans = generate_orders_and_scans(num_parcels=1500)
    print("Phase 2 data generation completed successfully!")
