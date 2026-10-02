# ============================================================
# FRAUDGUARD AI - FASTAPI BACKEND
# Fraud Detection + Smart Risk + Analyst Case Management
# ============================================================

import json

from typing import Literal, Optional

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from src.predictor import predict_transaction

from database.db import (
    save_transaction,
    get_recent_transactions,
    get_statistics,
    get_review_cases,
    update_case_review
)


# ============================================================
# CREATE FASTAPI APPLICATION
# ============================================================

app = FastAPI(
    title="FraudGuard AI API",
    description=(
        "Real-time credit card fraud detection using "
        "SMOTE + LightGBM, Isolation Forest, explainability, "
        "Smart Risk Decision Engine and Analyst Case Management."
    ),
    version="3.0.0"
)


# ============================================================
# TRANSACTION INPUT SCHEMA
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
# ANALYST REVIEW INPUT SCHEMA
# ============================================================

class AnalystReviewInput(BaseModel):

    case_status: Literal[
        "NEW",
        "UNDER_REVIEW",
        "CLOSED"
    ]

    analyst_verdict: Optional[
        Literal[
            "CONFIRMED_FRAUD",
            "FALSE_POSITIVE"
        ]
    ] = None

    analyst_notes: Optional[str] = None


# ============================================================
# DATABASE ROW -> API OBJECT
# ============================================================

def transaction_row_to_dict(row):

    # --------------------------------------------------------
    # DECODE REASON CODES
    # --------------------------------------------------------

    reason_codes = []

    if len(row) > 10 and row[10]:

        try:

            reason_codes = json.loads(
                row[10]
            )

        except json.JSONDecodeError:

            reason_codes = []


    # --------------------------------------------------------
    # REVIEW FLAG
    # --------------------------------------------------------

    review_required = False

    if len(row) > 13 and row[13] is not None:

        review_required = bool(
            row[13]
        )


    # --------------------------------------------------------
    # BUILD RESPONSE
    # --------------------------------------------------------

    return {

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

        "reason_codes": reason_codes,


        # Smart Risk Engine
        "decision": (
            row[11]
            if len(row) > 11
            else None
        ),

        "priority": (
            row[12]
            if len(row) > 12
            else None
        ),

        "review_required":
            review_required,

        "decision_reason": (
            row[14]
            if len(row) > 14
            else None
        ),

        "recommended_action": (
            row[15]
            if len(row) > 15
            else None
        ),


        # Analyst Case Management
        "case_status": (
            row[16]
            if len(row) > 16
            else None
        ),

        "analyst_verdict": (
            row[17]
            if len(row) > 17
            else None
        ),

        "analyst_notes": (
            row[18]
            if len(row) > 18
            else None
        ),

        "reviewed_at": (
            row[19]
            if len(row) > 19
            else None
        )
    }


# ============================================================
# HOME ENDPOINT
# ============================================================

@app.get("/")
def home():

    return {
        "message":
            "FraudGuard AI Fraud Detection API",

        "status":
            "running",

        "version":
            "3.0.0"
    }


# ============================================================
# HEALTH CHECK
# ============================================================

@app.get("/health")
def health_check():

    return {

        "status":
            "healthy",

        "model":
            "SMOTE + LightGBM",

        "anomaly_detector":
            "Isolation Forest",

        "explainability":
            "LightGBM feature contributions",

        "risk_engine":
            "Smart Risk Decision Engine",

        "case_management":
            "Analyst Feedback Workflow"
    }


# ============================================================
# FRAUD PREDICTION ENDPOINT
# ============================================================

@app.post("/predict")
def predict_fraud(
    transaction: TransactionInput
):

    try:

        transaction_data = (
            transaction.model_dump()
        )


        # Complete fraud prediction pipeline
        result = predict_transaction(
            transaction_data
        )


        # Save full result to database
        save_transaction(
            transaction_data,
            result
        )


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
# DASHBOARD STATISTICS
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
# RECENT TRANSACTIONS
# ============================================================

@app.get("/transactions")
def recent_transactions(
    limit: int = 20
):

    try:

        rows = get_recent_transactions(
            limit
        )


        transactions = [
            transaction_row_to_dict(
                row
            )
            for row in rows
        ]


        return {
            "transactions":
                transactions
        }


    except Exception as error:

        raise HTTPException(
            status_code=500,
            detail=str(error)
        )


# ============================================================
# ANALYST REVIEW QUEUE
# ============================================================

@app.get("/review-cases")
def review_cases(
    limit: int = 50
):

    try:

        rows = get_review_cases(
            limit
        )


        cases = [
            transaction_row_to_dict(
                row
            )
            for row in rows
        ]


        return {
            "review_cases":
                cases
        }


    except Exception as error:

        raise HTTPException(
            status_code=500,
            detail=str(error)
        )


# ============================================================
# UPDATE ANALYST REVIEW CASE
# ============================================================

@app.patch(
    "/review-cases/{transaction_id}"
)
def review_transaction(
    transaction_id: int,
    review: AnalystReviewInput
):

    try:

        # ----------------------------------------------------
        # FINAL VERDICT VALIDATION
        # ----------------------------------------------------

        if (
            review.case_status == "CLOSED"
            and review.analyst_verdict is None
        ):

            raise HTTPException(
                status_code=400,
                detail=(
                    "A CLOSED case requires an "
                    "analyst verdict."
                )
            )


        # ----------------------------------------------------
        # UPDATE DATABASE
        # ----------------------------------------------------

        updated = update_case_review(
            transaction_id=
                transaction_id,

            case_status=
                review.case_status,

            analyst_verdict=
                review.analyst_verdict,

            analyst_notes=
                review.analyst_notes
        )


        if not updated:

            raise HTTPException(
                status_code=404,
                detail=(
                    "Transaction not found."
                )
            )


        # ----------------------------------------------------
        # RESPONSE
        # ----------------------------------------------------

        final_status = (
            "CLOSED"
            if review.analyst_verdict
            in [
                "CONFIRMED_FRAUD",
                "FALSE_POSITIVE"
            ]
            else review.case_status
        )


        return {

            "success": True,

            "transaction_id":
                transaction_id,

            "case_status":
                final_status,

            "analyst_verdict":
                review.analyst_verdict,

            "analyst_notes":
                review.analyst_notes
        }


    except HTTPException:

        raise


    except Exception as error:

        raise HTTPException(
            status_code=500,
            detail=str(error)
        )