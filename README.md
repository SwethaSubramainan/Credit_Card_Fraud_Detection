# 💳 FraudGuard AI
## Real-Time Credit Card Fraud Detection & Risk Scoring System

FraudGuard AI is an end-to-end machine learning project designed to detect suspicious credit card transactions, identify unusual transaction patterns, generate explainable fraud alerts, and convert model predictions into practical risk decisions.

The system combines a supervised **SMOTE + LightGBM fraud classifier** with an **Isolation Forest anomaly detector**, a **Smart Risk Decision Engine**, and a **Human-in-the-Loop Analyst Case Management workflow**.

The project also includes a FastAPI backend, Streamlit monitoring dashboard, SQLite transaction database, transaction simulator, explainability layer, and automated API tests.

---

## 🎯 Problem Statement

Credit card fraud datasets are extremely imbalanced, where fraudulent transactions represent only a very small percentage of all transactions.

Traditional accuracy-based models can therefore appear highly accurate while failing to identify important fraud cases.

This project focuses on:

- Handling severe class imbalance
- Detecting fraudulent transactions
- Identifying unusual transaction behavior
- Optimizing the fraud classification threshold
- Generating explainable fraud alerts
- Converting ML predictions into business decisions
- Supporting human analyst investigation
- Storing analyst feedback for future model improvement

---

## 🚀 Key Features

### 1. Fraud Detection

The primary fraud detection model uses:

- LightGBM
- SMOTE oversampling
- Robust train/validation/test separation
- Threshold optimization using validation data
- Precision, Recall, F1, Average Precision, and ROC-AUC evaluation

The model does not rely only on accuracy because of the highly imbalanced nature of the dataset.

---

### 2. Anomaly Detection

An Isolation Forest model is trained using genuine training transactions.

It provides an additional anomaly signal that helps identify transactions that may appear unusual even when the supervised fraud classifier predicts them as genuine.

Anomaly risk is represented as a percentile relative to genuine training behavior.

Example anomaly states:

- Normal Pattern
- Unusual
- Highly Anomalous

---

### 3. Smart Risk Decision Engine

Machine learning outputs are converted into operational actions using a rule-based decision engine.

Possible decisions:

- `APPROVE`
- `MANUAL_REVIEW`
- `BLOCK`

The decision engine considers:

- Fraud prediction
- Fraud score
- Optimized fraud threshold
- Isolation Forest anomaly risk
- Anomaly status

Each decision also includes:

- Priority
- Review requirement
- Decision reason
- Recommended action

---

### 4. Explainable Fraud Alerts

Fraud predictions include the strongest positive LightGBM feature contributions.

Example:

```text
V14 increased the model's fraud risk score
V10 increased the model's fraud risk score
V12 increased the model's fraud risk score
