# ============================================================
# FRAUD PREDICTION + ANOMALY DETECTION + EXPLAINABILITY
# + SMART RISK DECISION MODULE
# ============================================================

from pathlib import Path
import json

import joblib
import numpy as np
import pandas as pd

from src.risk_engine import evaluate_transaction_risk


# ------------------------------------------------------------
# PROJECT PATHS
# ------------------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parent.parent
MODEL_FOLDER = PROJECT_ROOT / "models"

MODEL_PATH = (
    MODEL_FOLDER
    / "lightgbm_fraud_model.pkl"
)

SCALER_PATH = (
    MODEL_FOLDER
    / "scaler.pkl"
)

METADATA_PATH = (
    MODEL_FOLDER
    / "model_metadata.json"
)

ISOLATION_MODEL_PATH = (
    MODEL_FOLDER
    / "isolation_forest.pkl"
)

ANOMALY_REFERENCE_PATH = (
    MODEL_FOLDER
    / "anomaly_reference.npy"
)


# ------------------------------------------------------------
# LOAD SAVED MODELS
# ------------------------------------------------------------

fraud_model = joblib.load(
    MODEL_PATH
)

scaler = joblib.load(
    SCALER_PATH
)

isolation_model = joblib.load(
    ISOLATION_MODEL_PATH
)

anomaly_reference = np.load(
    ANOMALY_REFERENCE_PATH
)


# ------------------------------------------------------------
# LOAD MODEL METADATA
# ------------------------------------------------------------

with open(
    METADATA_PATH,
    "r"
) as file:

    metadata = json.load(file)


THRESHOLD = metadata[
    "threshold"
]

FEATURES = metadata[
    "features"
]

SCALED_COLUMNS = metadata[
    "scaled_columns"
]


# ============================================================
# ANOMALY RISK CALCULATION
# ============================================================

def calculate_anomaly_risk(
    raw_anomaly_score
):

    position = np.searchsorted(
        anomaly_reference,
        raw_anomaly_score,
        side="right"
    )

    anomaly_risk = (
        position
        / len(anomaly_reference)
    ) * 100

    return float(
        np.clip(
            anomaly_risk,
            0,
            100
        )
    )


# ============================================================
# FRAUD EXPLAINABILITY
# ============================================================

def get_fraud_reason_codes(
    input_df,
    top_n=3
):

    """
    Return the strongest positive LightGBM
    feature contributions.

    V1-V28 are anonymized dataset features,
    so we do not assign artificial business
    meanings to them.
    """

    contributions = (
        fraud_model.booster_.predict(
            input_df,
            pred_contrib=True
        )
    )

    contribution_values = (
        np.asarray(
            contributions
        )[0]
    )


    # Last value is LightGBM bias value
    feature_contributions = (
        contribution_values[:-1]
    )


    positive_drivers = []


    for feature, contribution in zip(
        FEATURES,
        feature_contributions
    ):

        contribution = float(
            contribution
        )


        if contribution > 0:

            positive_drivers.append(
                {
                    "feature":
                        feature,

                    "contribution":
                        contribution,

                    "reason":
                        (
                            f"{feature} increased "
                            f"the model's fraud risk score"
                        )
                }
            )


    positive_drivers.sort(
        key=lambda item:
            item["contribution"],
        reverse=True
    )


    return positive_drivers[
        :top_n
    ]


# ============================================================
# MAIN TRANSACTION PREDICTION FUNCTION
# ============================================================

def predict_transaction(
    transaction_data
):

    # --------------------------------------------------------
    # CREATE INPUT DATAFRAME
    # --------------------------------------------------------

    input_df = pd.DataFrame(
        [transaction_data],
        columns=FEATURES
    )


    # --------------------------------------------------------
    # SCALE TIME AND AMOUNT
    # --------------------------------------------------------

    input_df[
        SCALED_COLUMNS
    ] = scaler.transform(
        input_df[
            SCALED_COLUMNS
        ]
    )


    # ========================================================
    # LIGHTGBM FRAUD MODEL
    # ========================================================

    fraud_score = (
        fraud_model.predict_proba(
            input_df
        )[0][1]
    )


    # --------------------------------------------------------
    # APPLY OPTIMIZED VALIDATION THRESHOLD
    # --------------------------------------------------------

    prediction = int(
        fraud_score
        >= THRESHOLD
    )


    if prediction == 1:

        label = "Fraud"

    else:

        label = "Genuine"


    # ========================================================
    # FRAUD REASON CODES
    # ========================================================

    if prediction == 1:

        reason_codes = (
            get_fraud_reason_codes(
                input_df,
                top_n=3
            )
        )

    else:

        reason_codes = []


    # ========================================================
    # ISOLATION FOREST ANOMALY DETECTION
    # ========================================================

    raw_anomaly_score = (
        -isolation_model
        .decision_function(
            input_df
        )[0]
    )


    anomaly_risk = (
        calculate_anomaly_risk(
            raw_anomaly_score
        )
    )


    # ========================================================
    # ANOMALY STATUS
    # ========================================================

    if anomaly_risk >= 98:

        anomaly_status = (
            "Highly Anomalous"
        )

    elif anomaly_risk >= 90:

        anomaly_status = (
            "Unusual"
        )

    else:

        anomaly_status = (
            "Normal Pattern"
        )


    # ========================================================
    # BUILD BASE ML RESULT
    # ========================================================

    result = {

        "prediction":
            prediction,

        "label":
            label,

        "fraud_score":
            float(
                fraud_score
            ),

        "fraud_score_percent":
            float(
                fraud_score
                * 100
            ),

        "threshold":
            float(
                THRESHOLD
            ),

        "raw_anomaly_score":
            float(
                raw_anomaly_score
            ),

        "anomaly_risk":
            float(
                anomaly_risk
            ),

        "anomaly_status":
            anomaly_status,

        "reason_codes":
            reason_codes
    }


    # ========================================================
    # SMART RISK DECISION ENGINE
    # ========================================================

    risk_decision = (
        evaluate_transaction_risk(
            result
        )
    )


    # Add business decision fields
    # to the final prediction response

    result[
        "decision"
    ] = risk_decision[
        "decision"
    ]

    result[
        "priority"
    ] = risk_decision[
        "priority"
    ]

    result[
        "review_required"
    ] = risk_decision[
        "review_required"
    ]

    result[
        "decision_reason"
    ] = risk_decision[
        "decision_reason"
    ]

    result[
        "recommended_action"
    ] = risk_decision[
        "recommended_action"
    ]


    # ========================================================
    # RETURN FINAL RESULT
    # ========================================================

    return result