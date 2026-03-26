# 🧠 AI Diabetes Tracking System (Prediction & Tracking)

## 🚀 Overview

This project is a **full-stack AI-powered health monitoring system** that predicts diabetes risk and tracks patient health over time.

Unlike basic ML projects, this system is designed as a **real-world application**, combining machine learning, backend engineering, database management, and deployment.

---

## 🌐 Live Demo

🔗 https://ai-powered-diabetes-tracking-system.onrender.com

---
## Demo Video Link
https://www.loom.com/share/9528827c8ff2429e9af5b61733f44c04

## 💡 Key Features

### 🧠 Machine Learning Pipeline

* End-to-end pipeline (EDA → Preprocessing → Feature Engineering → Model Training)
* Multiple models compared using **cross-validation**
* Models evaluated using:

  * Accuracy
  * Precision
  * Recall
  * F1 Score
* Final model selected based on **Recall (medical priority)**

---

### 🤖 Model Performance

| Model               | Accuracy | Precision | Recall | F1 Score |
| ------------------- | -------- | --------- | ------ | -------- |
| Random Forest       | 0.89     | 0.84      | 0.79   | 0.82     |
| Decision Tree       | 0.85     | 0.78      | 0.76   | 0.77     |
| Logistic Regression | 0.85     | 0.78      | 0.75   | 0.76     |
| SVM                 | 0.86     | 0.82      | 0.72   | 0.77     |

👉 Final Model: **Random Forest**

---

### ⚙️ Backend (FastAPI)

* REST API built with FastAPI
* High-performance async endpoints
* Swagger UI for testing (`/docs`)

---

### 🔐 Authentication

* JWT-based login system
* Secure protected endpoints

---

### 🗄️ Database Integration

* PostgreSQL database
* SQLAlchemy ORM
* Stores:

  * User data
  * Predictions
  * Historical records

---

### 📊 Health Tracking System

* Tracks user prediction history
* Analyzes trends over time
* Detects:

  * Improvement ✅
  * Stable ➖
  * Increasing Risk ⚠️

---

### 📄 Report Generation

* Downloadable PDF reports
* Includes prediction + insights

---

### 🌐 Deployment

* Backend deployed on Render
* Cloud PostgreSQL database
* Production-ready API

---

## 🧠 System Architecture

User → FastAPI → ML Model → Prediction
                ↓
              Database
                ↓
      History + Trend Analysis + Insights

---

## 📂 Project Structure

```
├── api/                # FastAPI backend
├── src/                # ML scripts
├── data/               # datasets
├── notebooks/          # EDA & experiments
├── models/             # trained model
├── results/            # evaluation outputs
├── requirements.txt
├── runtime.txt
├── README.md
```

---

## 🚀 How to Run Locally

```bash
pip install -r requirements.txt
uvicorn api.main:app --reload
```

---

## 💀 What Makes This Project Special

✔ Not just prediction — full monitoring system
✔ Real-world ML decision making (recall-based)
✔ Backend + ML + DB integration
✔ Trend analysis system
✔ Deployed production API

---


## 🧠 Learning Outcome

This project demonstrates:

* End-to-end ML system design
* Model evaluation & selection strategy
* Backend API development
* Database integration
* Deployment & debugging in production

---

## 📌 Final Note

> This is not just a machine learning model — it is a complete AI system built to simulate real-world healthcare applications.
