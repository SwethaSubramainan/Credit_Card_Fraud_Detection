# ============================================================
# STREAMLIT FRAUD MONITORING DASHBOARD
# ============================================================

import streamlit as st
import pandas as pd
import requests


# ------------------------------------------------------------
# PAGE CONFIGURATION
# ------------------------------------------------------------

st.set_page_config(
    page_title="FraudGuard AI",
    page_icon="💳",
    layout="wide"
)


# ------------------------------------------------------------
# API CONFIGURATION
# ------------------------------------------------------------

API_BASE_URL = "http://127.0.0.1:8000"


# ------------------------------------------------------------
# DASHBOARD TITLE
# ------------------------------------------------------------

st.title("💳 FraudGuard AI")

st.subheader(
    "Real-Time Credit Card Fraud Monitoring System"
)

st.caption(
    "SMOTE + LightGBM Fraud Detection with "
    "Isolation Forest Anomaly Monitoring"
)


# ============================================================
# FORMAT FRAUD REASON CODES
# ============================================================

def format_reason_codes(reason_codes):

    if not isinstance(reason_codes, list):
        return "—"

    if len(reason_codes) == 0:
        return "—"

    features = []

    for reason in reason_codes:

        if isinstance(reason, dict):

            feature = reason.get(
                "feature"
            )

            if feature:

                features.append(
                    feature
                )

    if not features:
        return "—"

    return ", ".join(
        features
    )


# ============================================================
# LIVE DASHBOARD
# Refreshes automatically every 2 seconds
# ============================================================

@st.fragment(run_every=2)
def live_dashboard():

    # --------------------------------------------------------
    # GET DASHBOARD STATISTICS
    # --------------------------------------------------------

    try:

        stats_response = requests.get(
            f"{API_BASE_URL}/stats",
            timeout=5
        )

        stats_response.raise_for_status()

        stats = stats_response.json()

        api_online = True

    except requests.RequestException:

        stats = {
            "total_transactions": 0,
            "fraud_transactions": 0,
            "anomalous_transactions": 0
        }

        api_online = False


    # --------------------------------------------------------
    # KPI CARDS
    # --------------------------------------------------------

    col1, col2, col3 = st.columns(3)

    with col1:

        st.metric(
            "Total Transactions",
            stats["total_transactions"]
        )

    with col2:

        st.metric(
            "Fraud Alerts",
            stats["fraud_transactions"]
        )

    with col3:

        st.metric(
            "Anomaly Alerts",
            stats["anomalous_transactions"]
        )


    # --------------------------------------------------------
    # API STATUS
    # --------------------------------------------------------

    if api_online:

        st.success(
            "🟢 Fraud Detection API Online"
        )

    else:

        st.error(
            "🔴 Fraud Detection API Offline"
        )


    st.divider()


    # ========================================================
    # TRANSACTION DISTRIBUTION
    # ========================================================

    st.subheader(
        "Transaction Distribution"
    )


    genuine_transactions = (
        stats["total_transactions"]
        - stats["fraud_transactions"]
    )


    fraud_transactions = (
        stats["fraud_transactions"]
    )


    distribution_df = pd.DataFrame(
        {
            "Transaction Type": [
                "Genuine",
                "Fraud"
            ],

            "Count": [
                genuine_transactions,
                fraud_transactions
            ]
        }
    )


    st.bar_chart(
        distribution_df.set_index(
            "Transaction Type"
        ),
        width="stretch"
    )


    st.divider()


    # ========================================================
    # RECENT TRANSACTIONS
    # ========================================================

    st.subheader(
        "Recent Transactions"
    )


    try:

        transactions_response = requests.get(
            f"{API_BASE_URL}/transactions",
            params={"limit": 20},
            timeout=5
        )

        transactions_response.raise_for_status()


        transactions = (
            transactions_response.json()[
                "transactions"
            ]
        )


        if transactions:

            transactions_df = pd.DataFrame(
                transactions
            )


            # ------------------------------------------------
            # CONVERT FRAUD SCORE TO PERCENTAGE
            # ------------------------------------------------

            transactions_df["fraud_score"] = (
                transactions_df["fraud_score"]
                * 100
            )


            # ------------------------------------------------
            # CREATE WHY FLAGGED COLUMN
            # ------------------------------------------------

            if "reason_codes" in transactions_df.columns:

                transactions_df[
                    "Why Flagged?"
                ] = transactions_df[
                    "reason_codes"
                ].apply(
                    format_reason_codes
                )

            else:

                transactions_df[
                    "Why Flagged?"
                ] = "—"


            # ------------------------------------------------
            # RENAME COLUMNS
            # ------------------------------------------------

            transactions_df.rename(
                columns={
                    "id": "ID",

                    "amount": "Amount",

                    "label": "Prediction",

                    "fraud_score":
                        "Fraud Score (%)",

                    "anomaly_risk":
                        "Anomaly Risk",

                    "anomaly_status":
                        "Anomaly Status",

                    "created_at":
                        "Timestamp"
                },
                inplace=True
            )


            # ------------------------------------------------
            # SELECT DISPLAY COLUMNS
            # ------------------------------------------------

            display_df = transactions_df[
                [
                    "ID",
                    "Amount",
                    "Prediction",
                    "Fraud Score (%)",
                    "Anomaly Risk",
                    "Anomaly Status",
                    "Why Flagged?",
                    "Timestamp"
                ]
            ].copy()


            # ------------------------------------------------
            # FRAUD ROW HIGHLIGHTING
            # ------------------------------------------------

            def highlight_fraud(row):

                if row["Prediction"] == "Fraud":

                    return [
                        "background-color: #ffcccc;"
                        "color: #8b0000;"
                        "font-weight: bold;"
                    ] * len(row)

                return [
                    ""
                ] * len(row)


            styled_df = (
                display_df.style.apply(
                    highlight_fraud,
                    axis=1
                )
            )


            # ------------------------------------------------
            # DISPLAY TRANSACTION TABLE
            # ------------------------------------------------

            st.dataframe(
                styled_df,
                width="stretch"
            )


            st.caption(
                "Why Flagged? shows the strongest "
                "positive LightGBM feature contributions "
                "for fraud alerts. V1-V28 are anonymized "
                "dataset features."
            )


            st.divider()


            # =================================================
            # LATEST FRAUD ALERT DETAILS
            # =================================================

            st.subheader(
                "🚨 Latest Fraud Alert Details"
            )


            fraud_rows = transactions_df[
                transactions_df[
                    "Prediction"
                ] == "Fraud"
            ]


            if not fraud_rows.empty:

                # Most recent fraud transaction
                latest_fraud = (
                    fraud_rows.iloc[0]
                )


                detail_col1, detail_col2, detail_col3, detail_col4 = (
                    st.columns(4)
                )


                with detail_col1:

                    st.metric(
                        "Transaction ID",
                        int(
                            latest_fraud["ID"]
                        )
                    )


                with detail_col2:

                    st.metric(
                        "Amount",
                        f"{latest_fraud['Amount']:.2f}"
                    )


                with detail_col3:

                    st.metric(
                        "Fraud Score",
                        (
                            f"{latest_fraud['Fraud Score (%)']:.2f}%"
                        )
                    )


                with detail_col4:

                    st.metric(
                        "Anomaly Risk",
                        (
                            f"{latest_fraud['Anomaly Risk']:.2f}"
                        )
                    )


                st.write(
                    "**Anomaly Status:**",
                    latest_fraud[
                        "Anomaly Status"
                    ]
                )


                st.write(
                    "**Detected At:**",
                    latest_fraud[
                        "Timestamp"
                    ]
                )


                # --------------------------------------------
                # EXPLAINABILITY DETAILS
                # --------------------------------------------

                reason_codes = (
                    latest_fraud.get(
                        "reason_codes",
                        []
                    )
                )


                if isinstance(
                    reason_codes,
                    list
                ) and reason_codes:

                    explanation_rows = []


                    for reason in reason_codes:

                        explanation_rows.append(
                            {
                                "Feature":
                                    reason.get(
                                        "feature",
                                        "Unknown"
                                    ),

                                "Contribution":
                                    round(
                                        float(
                                            reason.get(
                                                "contribution",
                                                0
                                            )
                                        ),
                                        4
                                    ),

                                "Explanation":
                                    reason.get(
                                        "reason",
                                        ""
                                    )
                            }
                        )


                    explanation_df = pd.DataFrame(
                        explanation_rows
                    )


                    st.write(
                        "**Top Fraud Drivers**"
                    )


                    st.dataframe(
                        explanation_df,
                        width="stretch",
                        hide_index=True
                    )


                    st.caption(
                        "Contribution values are LightGBM "
                        "model-output contributions. "
                        "They are not probability percentages. "
                        "Positive values push the prediction "
                        "toward the fraud class."
                    )


                else:

                    st.info(
                        "Reason codes are not available "
                        "for this older transaction."
                    )


            else:

                st.info(
                    "No fraud transaction is present "
                    "in the most recent 20 transactions."
                )


            st.divider()


            # =================================================
            # ANOMALY RISK VISUALIZATION
            # =================================================

            st.subheader(
                "Anomaly Risk Trend"
            )


            st.caption(
                "Isolation Forest anomaly risk for the "
                "most recent transactions. "
                "Risk values above 90 trigger an anomaly alert."
            )


            anomaly_chart_df = display_df[
                [
                    "ID",
                    "Anomaly Risk"
                ]
            ].copy()


            # Sort from oldest to newest transaction
            anomaly_chart_df = (
                anomaly_chart_df
                .sort_values(
                    "ID"
                )
            )


            # Add anomaly alert threshold
            anomaly_chart_df[
                "Alert Threshold"
            ] = 90.0


            # Use transaction ID as chart index
            anomaly_chart_df = (
                anomaly_chart_df
                .set_index(
                    "ID"
                )
            )


            st.line_chart(
                anomaly_chart_df[
                    [
                        "Anomaly Risk",
                        "Alert Threshold"
                    ]
                ],
                width="stretch"
            )


        else:

            st.info(
                "No transactions have been "
                "processed yet."
            )


    except requests.RequestException:

        st.warning(
            "Fraud Detection API is currently offline."
        )


# ------------------------------------------------------------
# RUN LIVE DASHBOARD
# ------------------------------------------------------------

live_dashboard()


# ============================================================
# MODEL INFORMATION
# ============================================================

st.divider()

st.subheader(
    "Model Information"
)


col1, col2, col3 = st.columns(3)


with col1:

    st.write(
        "**Primary Model**"
    )

    st.write(
        "SMOTE + LightGBM"
    )


with col2:

    st.write(
        "**Anomaly Detector**"
    )

    st.write(
        "Isolation Forest"
    )


with col3:

    st.write(
        "**Test ROC-AUC**"
    )

    st.write(
        "0.9911"
    )