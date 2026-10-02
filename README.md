# Real-Time Credit Card Fraud Detection & Risk Monitoring System

## Project Overview

This project is an end-to-end machine learning system designed to detect fraudulent credit card transactions in near real time.

The system combines:

- SMOTE for handling class imbalance
- LightGBM for supervised fraud detection
- Isolation Forest for anomaly detection
- FastAPI for real-time prediction APIs
- SQLite for transaction logging
- Streamlit for fraud monitoring dashboard
- A transaction simulator to mimic real-time transaction flow

The dataset used is the Kaggle Credit Card Fraud Detection dataset containing highly imbalanced transaction data.

---

## Problem Statement

Credit card fraud detection is challenging because fraudulent transactions represent only a very small percentage of total transactions.

A traditional model can achieve very high accuracy while still missing many fraud cases.

Therefore, this project focuses on:

- Precision
- Recall
- F1-score
- Average Precision
- ROC-AUC
- False positives
- False negatives

instead of relying only on accuracy.

---

## Dataset

Dataset: Kaggle Credit Card Fraud Detection

Original dataset size:

- Transactions: 284,807
- Features: 30 input features
- Target: `Class`

Target values:

- `0` = Genuine transaction
- `1` = Fraud transaction

After duplicate removal:

- Total transactions: 283,726
- Genuine transactions: 283,253
- Fraud transactions: 473

Fraud percentage:

- Approximately 0.1667%

---

## Data Preprocessing

The preprocessing pipeline includes:

1. Removing duplicate transactions
2. Separating input features and target
3. Stratified train-validation-test split
4. Scaling `Time` and `Amount` using RobustScaler
5. Applying SMOTE only to the training dataset

Data split:

- Training set: 80%
- Validation set: 10%
- Test set: 10%

---

## Models Evaluated

The following models were evaluated:

- Logistic Regression
- LightGBM
- Class-Weighted LightGBM
- SMOTE + LightGBM
- Isolation Forest

Threshold optimization was performed using validation data.

---

## Final Supervised Model

The selected supervised fraud detection model is:

**SMOTE + LightGBM**

Validation threshold:

`0.9710`

Final test performance:

| Metric | Result |
|---|---:|
| Precision | 97.30% |
| Recall | 76.60% |
| F1-score | 85.71% |
| Average Precision | 83.68% |
| ROC-AUC | 99.11% |

Final test confusion matrix:

```text
True Negatives  = 28,325
False Positives = 1
False Negatives = 11
True Positives  = 36