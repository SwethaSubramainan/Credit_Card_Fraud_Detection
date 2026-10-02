# ============================================================
# FASTAPI BACKEND FOR CREDIT CARD FRAUD DETECTION
# ============================================================

import json

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from src.predictor import predict_transaction

from database.db import (
    save_transaction,
    get_recent_transactions,
    get_statistics
)


# ------------------------------------------------------------
# CREATE FASTAPI APPLICATION
# ------------------------------------------------------------

app = FastAPI(
    title="Credit Card Fraud Detection API",
    description=(
        "Real-time fraud detection API using "
        "SMOTE + LightGBM and Isolation Forest"
    ),
    version="1.0.0"
)


# ============================================================
# INPUT SCHEMA
# ============================================================

class TransactionInput(BaseModel):

    Time: float

    V1: float
    V2: float
    V3: float
    V4: float
    V5: float
    V6: float
    V7: float
    V8: float
    V9: float
    V10: float
    V11: float
    V12: float
    V13: float
    V14: float
    V15: float
    V16: float
    V17: float
    V18: float
    V19: float
    V20: float
    V21: float
    V22: float
    V23: float
    V24: float
    V25: float
    V26: float
    V27: float
    V28: float

    Amount: float


# ============================================================
# HOME ENDPOINT
# ============================================================

@app.get("/")
def home():

    return {
        "message": "Credit Card Fraud Detection API",
        "status": "running"
    }


# ============================================================
# HEALTH CHECK ENDPOINT
# ============================================================

@app.get("/health")
def health_check():

    return {
        "status": "healthy",
        "model": "SMOTE + LightGBM",
        "anomaly_detector": "Isolation Forest",
        "explainability": "LightGBM feature contributions"
    }


# ============================================================
# FRAUD PREDICTION ENDPOINT
# ============================================================

@app.post("/predict")
def predict_fraud(
    transaction: TransactionInput
):

    try:

        # ----------------------------------------------------
        # CONVERT INPUT INTO DICTIONARY
        # ----------------------------------------------------

        transaction_data = (
            transaction.model_dump()
        )


        # ----------------------------------------------------
        # RUN FRAUD + ANOMALY PREDICTION
        # ----------------------------------------------------

        result = predict_transaction(
            transaction_data
        )


        # ----------------------------------------------------
        # SAVE RESULT INTO SQLITE
        # ----------------------------------------------------

        save_transaction(
            transaction_data,
            result
        )


        # ----------------------------------------------------
        # RETURN API RESPONSE
        # ----------------------------------------------------

        return {
            "success": True,
            "result": result
        }


    except Exception as error:

        raise HTTPException(
            status_code=500,
            detail=str(error)
        )


# ============================================================
# DASHBOARD STATISTICS ENDPOINT
# ============================================================

@app.get("/stats")
def dashboard_statistics():

    try:

        return get_statistics()

    except Exception as error:

        raise HTTPException(
            status_code=500,
            detail=str(error)
        )


# ============================================================
# RECENT TRANSACTIONS ENDPOINT
# ============================================================

@app.get("/transactions")
def recent_transactions(
    limit: int = 20
):

    try:

        rows = get_recent_transactions(
            limit
        )

        transactions = []


        for row in rows:

            # ------------------------------------------------
            # DECODE REASON CODES
            # ------------------------------------------------

            reason_codes = []

            if len(row) > 10 and row[10]:

                try:

                    reason_codes = json.loads(
                        row[10]
                    )

                except json.JSONDecodeError:

                    reason_codes = []


            # ------------------------------------------------
            # BUILD API RESPONSE
            # ------------------------------------------------

            transactions.append(
                {
                    "id": row[0],

                    "transaction_time": row[1],

                    "amount": row[2],

                    "prediction": row[3],

                    "label": row[4],

                    "fraud_score": row[5],

                    "threshold": row[6],

                    "anomaly_risk": row[7],

                    "anomaly_status": row[8],

                    "created_at": row[9],

                    "reason_codes": reason_codes
                }
            )


        return {
            "transactions": transactions
        }


    except Exception as error:

        raise HTTPException(
            status_code=500,
            detail=str(error)
        )