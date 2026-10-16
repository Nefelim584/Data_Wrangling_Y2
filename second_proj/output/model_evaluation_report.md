# Machine Learning $\text{CO}_2$ Predictive Model Evaluation Report
**Study Project:** Smart Logistics $\text{CO}_2$ Calculator  
**Deliverable:** Deliverable 4 (Predictive model: estimate $\text{CO}_2$ when some data is missing)

---

## 1. Executive Summary
When parcels experience missing tracking scans or incomplete journey checkpoints, direct empirical journey reconstruction is impossible. To maintain carbon accounting completeness across 100% of parcels, a predictive machine learning model was trained to estimate carbon emissions ($\text{kgCO}_2\text{e}$) using parcel characteristics and regional corridor features.

- **Model Architecture:** Random Forest Regressor (30 Estimators, Max Depth 7, Variance Reduction Criterion)
- **Training Population:** 1,370 parcels with fully reconstructed, multi-segment verified journeys
- **Validation Strategy:** 5-Fold Cross-Validation

---

## 2. Model Performance Metrics

| Metric | 5-Fold Cross-Validation Score | Interpretation |
| :--- | :---: | :--- |
| **Coefficient of Determination ($R^2$)** | **0.825** | Explains majority of parcel emission variances across international and domestic lanes |
| **Root Mean Squared Error (RMSE)** | **3.032 $\text{kgCO}_2\text{e}$** | Low residual spread across extreme high-distance and high-weight parcels |
| **Mean Absolute Error (MAE)** | **2.072 $\text{kgCO}_2\text{e}$** | On average, predictions are within ~2.072 kg of empirical emissions |

---

## 3. Feature Importance Analysis

| Rank | Feature | Importance Share | Description |
| :---: | :--- | :---: | :--- |
| 1 | `ton_km_est` | 35.9% | Engineered predictive feature |
| 2 | `air_potential_flag` | 21.8% | Engineered predictive feature |
| 3 | `weight_kg` | 11.8% | Engineered predictive feature |
| 4 | `is_express` | 11.5% | Engineered predictive feature |
| 5 | `direct_distance_km` | 10.7% | Engineered predictive feature |
| 6 | `volume_m3` | 7.3% | Engineered predictive feature |
| 7 | `is_international` | 1.0% | Engineered predictive feature |
| 8 | `is_eco` | 0.1% | Engineered predictive feature |

---

## 4. Practical Application
The trained model artifact is serialized to `second_proj/output/model_artifact.json` and consumed by `predict_emissions.py` to fill the `ml_emissions` column in the master dataset for all incomplete shipments.
