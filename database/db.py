# ============================================================
# SQLITE DATABASE MODULE
# Fraud Detection + Smart Risk + Analyst Case Management
# ============================================================

import sqlite3
import json
from pathlib import Path
from datetime import datetime


# ------------------------------------------------------------
# DATABASE PATH
# ------------------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parent.parent

DATABASE_PATH = (
    PROJECT_ROOT
    / "database"
    / "fraud.db"
)


# ============================================================
# INITIALIZE / MIGRATE DATABASE
# ============================================================

def initialize_database():

    connection = sqlite3.connect(
        DATABASE_PATH
    )

    cursor = connection.cursor()


    # --------------------------------------------------------
    # CREATE TABLE FOR NEW DATABASES
    # --------------------------------------------------------

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS transactions (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            transaction_time REAL,

            amount REAL,

            prediction INTEGER,

            label TEXT,

            fraud_score REAL,

            threshold REAL,

            anomaly_risk REAL,

            anomaly_status TEXT,

            created_at TEXT,

            reason_codes TEXT,

            decision TEXT,

            priority TEXT,

            review_required INTEGER,

            decision_reason TEXT,

            recommended_action TEXT,

            case_status TEXT,

            analyst_verdict TEXT,

            analyst_notes TEXT,

            reviewed_at TEXT
        )
        """
    )


    # --------------------------------------------------------
    # CHECK EXISTING COLUMNS
    # --------------------------------------------------------

    cursor.execute(
        "PRAGMA table_info(transactions)"
    )

    existing_columns = [
        row[1]
        for row in cursor.fetchall()
    ]


    # --------------------------------------------------------
    # SAFE DATABASE MIGRATION
    # Existing records will NOT be deleted
    # --------------------------------------------------------

    migrations = {

        "reason_codes":
            "TEXT",

        "decision":
            "TEXT",

        "priority":
            "TEXT",

        "review_required":
            "INTEGER",

        "decision_reason":
            "TEXT",

        "recommended_action":
            "TEXT",

        # Analyst case-management fields
        "case_status":
            "TEXT",

        "analyst_verdict":
            "TEXT",

        "analyst_notes":
            "TEXT",

        "reviewed_at":
            "TEXT"
    }


    for column_name, column_type in migrations.items():

        if column_name not in existing_columns:

            cursor.execute(
                f"""
                ALTER TABLE transactions
                ADD COLUMN {column_name} {column_type}
                """
            )


    connection.commit()
    connection.close()


# ============================================================
# SAVE TRANSACTION RESULT
# ============================================================

def save_transaction(
    transaction_data,
    prediction_result
):

    connection = sqlite3.connect(
        DATABASE_PATH
    )

    cursor = connection.cursor()


    # --------------------------------------------------------
    # STORE REASON CODES AS JSON
    # --------------------------------------------------------

    reason_codes_json = json.dumps(
        prediction_result.get(
            "reason_codes",
            []
        )
    )


    # --------------------------------------------------------
    # REVIEW FLAG
    # --------------------------------------------------------

    review_required = int(
        bool(
            prediction_result.get(
                "review_required",
                False
            )
        )
    )


    # --------------------------------------------------------
    # INITIAL CASE STATUS
    # --------------------------------------------------------

    if review_required:

        case_status = "NEW"

    else:

        case_status = "AUTO_RESOLVED"


    # --------------------------------------------------------
    # INSERT TRANSACTION
    # --------------------------------------------------------

    cursor.execute(
        """
        INSERT INTO transactions (

            transaction_time,
            amount,
            prediction,
            label,
            fraud_score,
            threshold,
            anomaly_risk,
            anomaly_status,
            created_at,
            reason_codes,

            decision,
            priority,
            review_required,
            decision_reason,
            recommended_action,

            case_status,
            analyst_verdict,
            analyst_notes,
            reviewed_at

        )

        VALUES (
            ?, ?, ?, ?, ?, ?, ?, ?, ?, ?,
            ?, ?, ?, ?, ?,
            ?, ?, ?, ?
        )
        """,

        (

            float(
                transaction_data["Time"]
            ),

            float(
                transaction_data["Amount"]
            ),

            int(
                prediction_result["prediction"]
            ),

            prediction_result["label"],

            float(
                prediction_result["fraud_score"]
            ),

            float(
                prediction_result["threshold"]
            ),

            float(
                prediction_result["anomaly_risk"]
            ),

            prediction_result[
                "anomaly_status"
            ],

            datetime.now().isoformat(),

            reason_codes_json,

            prediction_result.get(
                "decision"
            ),

            prediction_result.get(
                "priority"
            ),

            review_required,

            prediction_result.get(
                "decision_reason"
            ),

            prediction_result.get(
                "recommended_action"
            ),

            case_status,

            None,

            None,

            None
        )
    )


    connection.commit()
    connection.close()


# ============================================================
# UPDATE ANALYST CASE
# ============================================================

def update_case_review(
    transaction_id,
    case_status,
    analyst_verdict=None,
    analyst_notes=None
):

    """
    Update a fraud-review case.

    Example statuses:
        NEW
        UNDER_REVIEW
        CLOSED

    Example verdicts:
        CONFIRMED_FRAUD
        FALSE_POSITIVE
    """

    connection = sqlite3.connect(
        DATABASE_PATH
    )

    cursor = connection.cursor()


    reviewed_at = None


    # Add completion timestamp only
    # when analyst gives a final verdict
    if analyst_verdict in [
        "CONFIRMED_FRAUD",
        "FALSE_POSITIVE"
    ]:

        reviewed_at = (
            datetime.now().isoformat()
        )

        case_status = "CLOSED"


    cursor.execute(
        """
        UPDATE transactions

        SET
            case_status = ?,
            analyst_verdict = ?,
            analyst_notes = ?,
            reviewed_at = ?

        WHERE id = ?
        """,

        (
            case_status,
            analyst_verdict,
            analyst_notes,
            reviewed_at,
            int(transaction_id)
        )
    )


    updated_rows = (
        cursor.rowcount
    )


    connection.commit()
    connection.close()


    return updated_rows > 0


# ============================================================
# GET RECENT TRANSACTIONS
# ============================================================

def get_recent_transactions(
    limit=20
):

    connection = sqlite3.connect(
        DATABASE_PATH
    )

    cursor = connection.cursor()


    cursor.execute(
        """
        SELECT *

        FROM transactions

        ORDER BY id DESC

        LIMIT ?
        """,

        (
            limit,
        )
    )


    rows = cursor.fetchall()

    connection.close()

    return rows


# ============================================================
# GET ANALYST REVIEW CASES
# ============================================================

def get_review_cases(
    limit=50
):

    connection = sqlite3.connect(
        DATABASE_PATH
    )

    cursor = connection.cursor()


    cursor.execute(
        """
        SELECT *

        FROM transactions

        WHERE review_required = 1

        ORDER BY id DESC

        LIMIT ?
        """,

        (
            limit,
        )
    )


    rows = cursor.fetchall()

    connection.close()

    return rows


# ============================================================
# GET DASHBOARD STATISTICS
# ============================================================

def get_statistics():

    connection = sqlite3.connect(
        DATABASE_PATH
    )

    cursor = connection.cursor()


    # --------------------------------------------------------
    # TOTAL TRANSACTIONS
    # --------------------------------------------------------

    cursor.execute(
        """
        SELECT COUNT(*)
        FROM transactions
        """
    )

    total_transactions = (
        cursor.fetchone()[0]
    )


    # --------------------------------------------------------
    # FRAUD TRANSACTIONS
    # --------------------------------------------------------

    cursor.execute(
        """
        SELECT COUNT(*)

        FROM transactions

        WHERE prediction = 1
        """
    )

    fraud_transactions = (
        cursor.fetchone()[0]
    )


    # --------------------------------------------------------
    # ANOMALY ALERTS
    # --------------------------------------------------------

    cursor.execute(
        """
        SELECT COUNT(*)

        FROM transactions

        WHERE anomaly_risk >= 90
        """
    )

    anomalous_transactions = (
        cursor.fetchone()[0]
    )


    # --------------------------------------------------------
    # APPROVED TRANSACTIONS
    # --------------------------------------------------------

    cursor.execute(
        """
        SELECT COUNT(*)

        FROM transactions

        WHERE decision = 'APPROVE'
        """
    )

    approved_transactions = (
        cursor.fetchone()[0]
    )


    # --------------------------------------------------------
    # MANUAL REVIEW TRANSACTIONS
    # --------------------------------------------------------

    cursor.execute(
        """
        SELECT COUNT(*)

        FROM transactions

        WHERE decision = 'MANUAL_REVIEW'
        """
    )

    manual_review_transactions = (
        cursor.fetchone()[0]
    )


    # --------------------------------------------------------
    # BLOCKED TRANSACTIONS
    # --------------------------------------------------------

    cursor.execute(
        """
        SELECT COUNT(*)

        FROM transactions

        WHERE decision = 'BLOCK'
        """
    )

    blocked_transactions = (
        cursor.fetchone()[0]
    )


    # --------------------------------------------------------
    # OPEN ANALYST CASES
    # --------------------------------------------------------

    cursor.execute(
        """
        SELECT COUNT(*)

        FROM transactions

        WHERE review_required = 1
        AND (
            case_status = 'NEW'
            OR case_status = 'UNDER_REVIEW'
        )
        """
    )

    open_review_cases = (
        cursor.fetchone()[0]
    )


    # --------------------------------------------------------
    # CONFIRMED FRAUD CASES
    # --------------------------------------------------------

    cursor.execute(
        """
        SELECT COUNT(*)

        FROM transactions

        WHERE analyst_verdict = 'CONFIRMED_FRAUD'
        """
    )

    confirmed_fraud_cases = (
        cursor.fetchone()[0]
    )


    # --------------------------------------------------------
    # FALSE POSITIVE CASES
    # --------------------------------------------------------

    cursor.execute(
        """
        SELECT COUNT(*)

        FROM transactions

        WHERE analyst_verdict = 'FALSE_POSITIVE'
        """
    )

    false_positive_cases = (
        cursor.fetchone()[0]
    )


    connection.close()


    return {

        "total_transactions":
            total_transactions,

        "fraud_transactions":
            fraud_transactions,

        "anomalous_transactions":
            anomalous_transactions,

        "approved_transactions":
            approved_transactions,

        "manual_review_transactions":
            manual_review_transactions,

        "blocked_transactions":
            blocked_transactions,

        "open_review_cases":
            open_review_cases,

        "confirmed_fraud_cases":
            confirmed_fraud_cases,

        "false_positive_cases":
            false_positive_cases
    }


# ============================================================
# INITIALIZE DATABASE WHEN MODULE IS IMPORTED
# ============================================================

initialize_database()