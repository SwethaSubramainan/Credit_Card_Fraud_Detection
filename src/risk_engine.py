# ============================================================
# SMART FRAUD RISK DECISION ENGINE
# ============================================================

"""
This module converts machine-learning outputs into
business-friendly transaction decisions.

The ML model answers:
    "How suspicious is this transaction?"

The Risk Engine answers:
    "What action should the system take?"
"""


# ------------------------------------------------------------
# BUSINESS RULE CONFIGURATION
# ------------------------------------------------------------

# Transactions above this anomaly percentile
# should be reviewed even when the supervised model
# does not classify them as fraud.
ANOMALY_REVIEW_THRESHOLD = 90.0


# This is NOT the trained fraud classification threshold.
#
# The actual optimized model threshold is stored in
# model_metadata.json (~0.971).
#
# This lower value is only a configurable business rule
# used to send elevated-but-not-blocked transactions
# for manual review.
FRAUD_SCORE_REVIEW_THRESHOLD = 0.50


# ============================================================
# SMART RISK DECISION FUNCTION
# ============================================================

def evaluate_transaction_risk(
    prediction_result
):

    """
    Convert fraud model and anomaly detector outputs into
    a business action.

    Possible decisions:

    APPROVE
        Transaction appears normal.

    MANUAL_REVIEW
        Transaction is suspicious but not strong enough
        for automatic blocking.

    BLOCK
        Fraud model classified the transaction as fraud.
    """

    # --------------------------------------------------------
    # READ MODEL OUTPUTS
    # --------------------------------------------------------

    prediction = int(
        prediction_result.get(
            "prediction",
            0
        )
    )

    fraud_score = float(
        prediction_result.get(
            "fraud_score",
            0.0
        )
    )

    anomaly_risk = float(
        prediction_result.get(
            "anomaly_risk",
            0.0
        )
    )

    anomaly_status = (
        prediction_result.get(
            "anomaly_status",
            "Unknown"
        )
    )


    # ========================================================
    # RULE 1
    # SUPERVISED MODEL CONFIRMS FRAUD
    # ========================================================

    if prediction == 1:

        # Fraud + extremely abnormal pattern
        if anomaly_risk >= 98:

            priority = "CRITICAL"

            decision_reason = (
                "Transaction was classified as fraud "
                "and also shows a highly anomalous pattern."
            )

        else:

            priority = "HIGH"

            decision_reason = (
                "Transaction exceeded the optimized "
                "fraud detection threshold."
            )


        return {
            "decision": "BLOCK",

            "priority": priority,

            "review_required": True,

            "decision_reason":
                decision_reason,

            "recommended_action":
                "Block transaction and send alert "
                "for fraud analyst review.",

            "fraud_score":
                fraud_score,

            "anomaly_risk":
                anomaly_risk,

            "anomaly_status":
                anomaly_status
        }


    # ========================================================
    # RULE 2
    # MODEL SAYS GENUINE BUT ANOMALY DETECTOR DISAGREES
    # ========================================================

    if anomaly_risk >= 98:

        return {
            "decision": "MANUAL_REVIEW",

            "priority": "HIGH",

            "review_required": True,

            "decision_reason": (
                "The supervised model classified the "
                "transaction as genuine, but the "
                "Isolation Forest detected a highly "
                "unusual transaction pattern."
            ),

            "recommended_action": (
                "Temporarily hold or verify the transaction "
                "before approval."
            ),

            "fraud_score":
                fraud_score,

            "anomaly_risk":
                anomaly_risk,

            "anomaly_status":
                anomaly_status
        }


    # ========================================================
    # RULE 3
    # UNUSUAL ANOMALY PATTERN
    # ========================================================

    if anomaly_risk >= ANOMALY_REVIEW_THRESHOLD:

        return {
            "decision": "MANUAL_REVIEW",

            "priority": "MEDIUM",

            "review_required": True,

            "decision_reason": (
                "The transaction is outside the normal "
                "behavior pattern according to the "
                "Isolation Forest anomaly detector."
            ),

            "recommended_action": (
                "Send transaction to analyst review queue."
            ),

            "fraud_score":
                fraud_score,

            "anomaly_risk":
                anomaly_risk,

            "anomaly_status":
                anomaly_status
        }


    # ========================================================
    # RULE 4
    # ELEVATED SUPERVISED FRAUD SCORE
    # ========================================================

    if fraud_score >= FRAUD_SCORE_REVIEW_THRESHOLD:

        return {
            "decision": "MANUAL_REVIEW",

            "priority": "MEDIUM",

            "review_required": True,

            "decision_reason": (
                "The transaction did not exceed the final "
                "fraud classification threshold, but its "
                "fraud model score is elevated."
            ),

            "recommended_action": (
                "Review transaction before final approval."
            ),

            "fraud_score":
                fraud_score,

            "anomaly_risk":
                anomaly_risk,

            "anomaly_status":
                anomaly_status
        }


    # ========================================================
    # RULE 5
    # NORMAL TRANSACTION
    # ========================================================

    return {
        "decision": "APPROVE",

        "priority": "LOW",

        "review_required": False,

        "decision_reason": (
            "Fraud score and anomaly risk are both "
            "within normal operating limits."
        ),

        "recommended_action": (
            "Approve transaction."
        ),

        "fraud_score":
            fraud_score,

        "anomaly_risk":
            anomaly_risk,

        "anomaly_status":
            anomaly_status
    }