# ============================================================
# TEST FRAUD PREDICTION + ANOMALY DETECTION -- 2nd code
# ============================================================

import pandas as pd

from src.predictor import predict_transaction


# ------------------------------------------------------------
# LOAD DATASET
# ------------------------------------------------------------

df = pd.read_csv(
    "data/raw/creditcard.csv"
)


# ------------------------------------------------------------
# SELECT ONE FRAUD TRANSACTION
# ------------------------------------------------------------

sample = df[
    df["Class"] == 1
].iloc[0]


# Store actual class
actual_class = int(
    sample["Class"]
)


# Remove target column
transaction_data = sample.drop(
    "Class"
).to_dict()


# ------------------------------------------------------------
# MAKE PREDICTION
# ------------------------------------------------------------

result = predict_transaction(
    transaction_data
)


# ------------------------------------------------------------
# DISPLAY RESULT
# ------------------------------------------------------------

print("Fraud Detection Result")
print("--------------------------------")

print(
    "Actual Class:",
    actual_class
)

print(
    "Predicted Class:",
    result["prediction"]
)

print(
    "Prediction Label:",
    result["label"]
)

print(
    "Fraud Score:",
    round(
        result["fraud_score_percent"],
        4
    ),
    "%"
)

print(
    "Model Threshold:",
    round(
        result["threshold"],
        4
    )
)

print(
    "Anomaly Risk:",
    round(
        result["anomaly_risk"],
        2
    ),
    "/ 100"
)

print(
    "Anomaly Status:",
    result["anomaly_status"]
)


# # ============================================================
# # TEST FRAUD PREDICTION -- 1st code
# # ============================================================

# import pandas as pd

# from src.predictor import predict_transaction


# # ------------------------------------------------------------
# # LOAD DATASET
# # ------------------------------------------------------------

# df = pd.read_csv(
#     "data/raw/creditcard.csv"
# )


# # ------------------------------------------------------------
# # SELECT ONE SAMPLE TRANSACTION
# # ------------------------------------------------------------

# sample = df.drop(
#     "Class",
#     axis=1
# ).iloc[0]


# # Convert row into dictionary
# transaction_data = sample.to_dict()


# # ------------------------------------------------------------
# # MAKE PREDICTION
# # ------------------------------------------------------------

# result = predict_transaction(
#     transaction_data
# )


# # ------------------------------------------------------------
# # DISPLAY RESULT
# # ------------------------------------------------------------

# print("Prediction Result")
# print("-------------------------")

# print(
#     "Label:",
#     result["label"]
# )

# print(
#     "Fraud Probability:",
#     round(
#         result["fraud_probability"] * 100,
#         2
#     ),
#     "%"
# )

# print(
#     "Threshold:",
#     round(
#         result["threshold"],
#         4
#     )
# )