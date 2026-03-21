# 📊 Dataset Insights — Diabetes Prediction

## 📁 Dataset Overview

The dataset contains medical diagnostic features used to predict whether a patient has diabetes.

Target Variable:

* `Outcome` → 0 (No Diabetes), 1 (Diabetes)

---

## 🔍 Initial Observations

* Dataset contains **no explicit missing values**
* However, several features contain **invalid zero values**, which are not medically realistic

Affected columns:

* Glucose
* BloodPressure
* SkinThickness
* Insulin
* BMI

👉 These were treated as **missing values during preprocessing**

---

## ⚠️ Data Quality Issues

### 1. Invalid Zero Values

* BMI = 0 ❌ (not possible)
* Glucose = 0 ❌ (unrealistic)
* Insulin = 0 ❌ (likely missing)

👉 Insight:
These zeros represent **missing or unrecorded data**, not actual measurements.

---

### 2. Presence of Outliers

* Features like **Insulin** and **BMI** show extreme values
* Outliers may affect model performance

👉 Action:
Outliers handled using **IQR-based filtering**

---

## 📊 Feature Relationships

* **Glucose** shows strong correlation with diabetes outcome
* **BMI** and **Age** show moderate correlation
* Some features have weak or non-linear relationships

👉 Insight:
Not all features contribute equally — feature engineering is necessary

---

## ⚖️ Class Distribution

* Dataset is **slightly imbalanced**
* Fewer positive diabetes cases compared to negative

👉 Impact:

* Accuracy alone is not sufficient
* Recall becomes important metric

---

## 🧠 Key Takeaways

* Raw data is **not clean and requires preprocessing**
* Domain knowledge is important (medical thresholds)
* Feature engineering can improve model performance
* Evaluation should focus on **recall**, not just accuracy

---

## 🚀 Next Steps

* Handle invalid values (0 → NaN → imputation)
* Perform feature engineering (BMI categories, age groups, etc.)
* Apply scaling where required
* Train and compare multiple models
* Select final model based on recall and F1-score

---

## 💡 Final Insight

This dataset highlights a common real-world scenario:

> Data may appear clean but still contain hidden issues
> (invalid values, outliers, imbalance)

Proper preprocessing and thoughtful feature engineering are critical for building reliable ML models.
