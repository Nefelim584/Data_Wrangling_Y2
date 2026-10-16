# Smart Logistics $\text{CO}_2$ Analytics & Carbon Footprint Insights Report
**Deliverable:** Deliverable 3 ($\text{CO}_2$ analysis: emissions by parcel, journey, mode, or flow)  
**Total Shipments Analyzed:** 1,500 parcels  
**Total Logistics Carbon Footprint:** **13,801.38 $\text{kgCO}_2\text{e}$** (13.80 metric tons)

---

## 1. Emissions Breakdown by Transport Mode

The modal breakdown reveals where decarbonization efforts will yield the highest return on investment:

| Transport Mode | Segments | Total Distance (km) | Total Payload (t.km) | Emissions ($\text{kgCO}_2\text{e}$) | % Network Emissions | Carbon Intensity |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **LCV** | 2,739 | 34,011.8 | 156.3 | **10,577.67** | **76.64%** | 67671.1 g/t.km |
| **AIR_FREIGHT** | 329 | 922,041.6 | 4,514.1 | **2,257.06** | **16.35%** | 500.0 g/t.km |
| **HEAVY_TRUCK** | 883 | 2,644,343.0 | 11,745.5 | **966.65** | **7.0%** | 82.3 g/t.km |
| **BICYCLE** | 1,370 | 14,897.0 | 68.9 | **0.00** | **0.0%** | 0.0 kg/km |

> **Key Insight:** While **LCV delivery vans** handle the majority of segment operations and first/last-mile logistics, **Air Freight** generates disproportionate carbon emissions per ton-kilometer (500.0 g/t.km vs 82.3 g/t.km for Heavy Trucks), making modal shift to electrified rail or optimized road corridors the primary decarbonization lever.

---

## 2. Corridor & Geographic Flow Analysis

Top 10 highest carbon-emitting corridors:

| Rank | Corridor | Parcel Volume | Total Emissions ($\text{{kgCO}}_2\text{{e}}$) | Avg per Parcel ($\text{{kgCO}}_2\text{{e}}$) | Avg Distance (km) |
| :---: | :--- | :---: | :---: | :---: | :---: |
| 1 | **CA -> FR** | 46 | 924.88 | 20.11 | 6,894.8 |
| 2 | **FR -> FR** | 102 | 897.03 | 8.79 | 391.9 |
| 3 | **DE -> FR** | 100 | 840.52 | 8.41 | 898.9 |
| 4 | **FR -> ES** | 90 | 769.56 | 8.55 | 1,038.2 |
| 5 | **ES -> FR** | 95 | 766.35 | 8.07 | 1,085.9 |
| 6 | **CA -> ES** | 42 | 763.04 | 18.17 | 7,252.6 |
| 7 | **CA -> DE** | 42 | 758.03 | 18.05 | 7,259.6 |
| 8 | **FR -> CA** | 52 | 757.97 | 14.58 | 7,020.1 |
| 9 | **DE -> ES** | 95 | 754.44 | 7.94 | 1,719.8 |
| 10 | **ES -> CA** | 65 | 751.01 | 11.55 | 6,839.1 |

---

## 3. Domestic vs. International Logistics Footprint

| Flow Classification | Parcel Volume | Total Emissions ($\text{{kgCO}}_2\text{{e}}$) | Avg per Parcel ($\text{{kgCO}}_2\text{{e}}$) | Avg Distance (km) |
| :--- | :---: | :---: | :---: | :---: |
| **Domestic** | 330 | 2,364.87 | **7.17 kg** | 342.3 km |
| **International** | 1,170 | 12,804.82 | **10.94 kg** | 3,082.3 km |

---

## 4. Emissions by Parcel Weight Class

| Weight Bracket | Parcel Count | Total Emissions ($\text{{kgCO}}_2\text{{e}}$) | Avg per Parcel ($\text{{kgCO}}_2\text{{e}}$) | Avg Distance (km) |
| :--- | :---: | :---: | :---: | :---: |
| **Small (< 2 kg)** | 352 | 2,932.91 | **8.33 kg** | 2,309.5 km |
| **Medium (2 - 10 kg)** | 1,036 | 10,353.69 | **9.99 kg** | 2,559.1 km |
| **Heavy (> 10 kg)** | 112 | 1,883.09 | **16.81 kg** | 2,277.7 km |

---

## 5. Statistical Distribution & Benchmark Comparison

- **Mean Parcel Footprint:** 10.11 $\text{kgCO}_2\text{e}$
- **Median ($P_{50}$):** 8.61 $\text{kgCO}_2\text{e}$
- **Interquartile Range ($P_{25} - P_{75}$):** 6.52 – 11.08 $\text{kgCO}_2\text{e}$
- **Top 10% ($P_{90}$):** 16.63 $\text{kgCO}_2\text{e}$
- **Extreme Peak ($P_{99}$):** 43.83 $\text{kgCO}_2\text{e}$

### Benchmark Parcel `P001` Profile:
- **Corridor:** FR $\rightarrow$ ES
- **Weight:** 8.0 kg
- **Distance:** 1423.0 km across 4 segments
- **Calculated Emissions:** **15.81 $\text{kgCO}_2\text{e}$** (Places in the 80th percentile due to international multi-modal air freight leg).
