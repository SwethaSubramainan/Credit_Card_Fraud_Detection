# 2nd code
import time
import requests
import pandas as pd
from pathlib import Path

# ---------------------------------------------------------
# Project configuration
# ---------------------------------------------------------
PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATASET_PATH = PROJECT_ROOT / "data" / "raw" / "creditcard.csv"

API_URL = "http://127.0.0.1:8000/predict"


# ---------------------------------------------------------
# Load dataset
# ---------------------------------------------------------
df = pd.read_csv(DATASET_PATH)

# Separate genuine and fraudulent transactions
genuine_df = df[df["Class"] == 0]
fraud_df = df[df["Class"] == 1]

print("Dataset loaded successfully!")
print(f"Genuine transactions: {len(genuine_df)}")
print(f"Fraud transactions: {len(fraud_df)}")

print("\nStarting transaction simulation...")
print("Demo mode: Every 5th transaction will be a known fraud sample.\n")


# ---------------------------------------------------------
# Send transactions continuously
# ---------------------------------------------------------
transaction_number = 1

while True:

    # NOTE:
    # The real dataset contains only ~0.17% fraud.
    # For dashboard demonstration purposes only,
    # every 5th transaction is selected from known fraud samples.
    if transaction_number % 5 == 0:
        row = fraud_df.sample(n=1).iloc[0]
    else:
        row = genuine_df.sample(n=1).iloc[0]

    actual_class = int(row["Class"])

    # Remove target column before sending transaction to API
    transaction_data = row.drop("Class").to_dict()

    try:
        response = requests.post(
            API_URL,
            json=transaction_data,
            timeout=10
        )

        print("-----------------------------------")
        print(f"Transaction Number: {transaction_number}")
        print(f"Actual Class: {actual_class}")
        print("API Response:", response.json())

    except requests.exceptions.RequestException as error:
        print("-----------------------------------")
        print("API connection error:", error)

    transaction_number += 1

    # Wait 2 seconds before sending next transaction
    time.sleep(2)


# ============================================================
# REAL-TIME TRANSACTION SIMULATOR -- 1st code
# ============================================================

import time
import random
import requests
import pandas as pd


# ------------------------------------------------------------
# CONFIGURATION
# ------------------------------------------------------------

API_URL = "http://127.0.0.1:8000/predict"

DATASET_PATH = "data/raw/creditcard.csv"

DELAY_SECONDS = 2


# ------------------------------------------------------------
# LOAD DATASET
# ------------------------------------------------------------

df = pd.read_csv(DATASET_PATH)

print("Dataset loaded successfully!")
print("Starting transaction simulation...")


# ------------------------------------------------------------
# CONTINUOUS TRANSACTION STREAM
# ------------------------------------------------------------

while True:

    # Select one random transaction
    row = df.sample(1).iloc[0]

    # Store actual class only for simulator checking
    actual_class = int(row["Class"])

    # Remove target before sending to API
    transaction = row.drop(
        "Class"
    ).to_dict()

    try:

        # Send transaction to FastAPI
        response = requests.post(
            API_URL,
            json=transaction,
            timeout=10
        )

        # Read response
        result = response.json()

        print("\n-----------------------------------")

        print(
            "Actual Class:",
            actual_class
        )

        print(
            "API Response:",
            result
        )

    except Exception as error:

        print(
            "API connection error:",
            error
        )


    # Wait before sending next transaction
    time.sleep(
        DELAY_SECONDS
    )