# ============================================================
# SQLITE DATABASE MODULE
# ============================================================

import sqlite3
import json
from pathlib import Path
from datetime import datetime


# ------------------------------------------------------------
# DATABASE PATH
# ------------------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parent.parent

DATABASE_PATH = PROJECT_ROOT / "database" / "fraud.db"


# ------------------------------------------------------------
# CREATE / UPDATE DATABASE TABLE
# ------------------------------------------------------------

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

            reason_codes TEXT
        )
        """
    )


    # --------------------------------------------------------
    # MIGRATE EXISTING DATABASE
    # --------------------------------------------------------

    cursor.execute(
        "PRAGMA table_info(transactions)"
    )

    existing_columns = [
        row[1]
        for row in cursor.fetchall()
    ]


    # Add reason_codes column if old database
    # does not already contain it
    if "reason_codes" not in existing_columns:

        cursor.execute(
            """
            ALTER TABLE transactions
            ADD COLUMN reason_codes TEXT
            """
        )


    connection.commit()
    connection.close()


# ------------------------------------------------------------
# SAVE TRANSACTION RESULT
# ------------------------------------------------------------

def save_transaction(
    transaction_data,
    prediction_result
):

    connection = sqlite3.connect(
        DATABASE_PATH
    )

    cursor = connection.cursor()


    # Convert reason codes list into JSON text
    reason_codes_json = json.dumps(
        prediction_result.get(
            "reason_codes",
            []
        )
    )


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

            reason_codes

        )

        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
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

            reason_codes_json

        )
    )


    connection.commit()
    connection.close()


# ------------------------------------------------------------
# GET RECENT TRANSACTIONS
# ------------------------------------------------------------

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


# ------------------------------------------------------------
# GET BASIC DASHBOARD STATISTICS
# ------------------------------------------------------------

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
    # ANOMALOUS TRANSACTIONS
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


    connection.close()


    return {

        "total_transactions":
            total_transactions,

        "fraud_transactions":
            fraud_transactions,

        "anomalous_transactions":
            anomalous_transactions

    }


# ------------------------------------------------------------
# INITIALIZE DATABASE WHEN MODULE IS IMPORTED
# ------------------------------------------------------------

initialize_database()