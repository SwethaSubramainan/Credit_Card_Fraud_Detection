# ============================================================
# FRAUDGUARD AI - REAL-TIME FRAUD MONITORING DASHBOARD
# ============================================================

import streamlit as st
import pandas as pd
import requests


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="FraudGuard AI",
    page_icon="💳",
    layout="wide"
)


# ============================================================
# API CONFIGURATION
# ============================================================

API_BASE_URL = "http://127.0.0.1:8000"


# ============================================================
# DASHBOARD HEADER
# ============================================================

st.title("Credit Card Fraud Detection")

st.subheader(
    "Real-Time Credit Card Fraud Monitoring System"
)

st.caption(
    "SMOTE + LightGBM Fraud Detection • "
    "Isolation Forest Anomaly Monitoring • "
    "Explainable AI • Smart Risk Decision Engine • "
    "Human-in-the-Loop Analyst Review"
)


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def format_reason_codes(reason_codes):

    if not isinstance(reason_codes, list):
        return "—"

    if not reason_codes:
        return "—"

    features = []

    for reason in reason_codes:

        if isinstance(reason, dict):

            feature = reason.get("feature")

            if feature:
                features.append(feature)

    if not features:
        return "—"

    return ", ".join(features)


def format_review_required(value):

    if value is None:
        return "—"

    try:

        if pd.isna(value):
            return "—"

    except Exception:
        pass

    return "Yes" if bool(value) else "No"


# ============================================================
# LIVE DASHBOARD
# Automatically refreshes every 2 seconds
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
            "anomalous_transactions": 0,
            "approved_transactions": 0,
            "manual_review_transactions": 0,
            "blocked_transactions": 0,
            "open_review_cases": 0,
            "confirmed_fraud_cases": 0,
            "false_positive_cases": 0
        }

        api_online = False


    # ========================================================
    # LIVE MONITORING KPIs
    # ========================================================

    st.subheader("Live Monitoring")

    col1, col2, col3 = st.columns(3)

    with col1:

        st.metric(
            "Total Transactions",
            stats.get(
                "total_transactions",
                0
            )
        )

    with col2:

        st.metric(
            "Fraud Alerts",
            stats.get(
                "fraud_transactions",
                0
            )
        )

    with col3:

        st.metric(
            "Anomaly Alerts",
            stats.get(
                "anomalous_transactions",
                0
            )
        )


    # ========================================================
    # SMART DECISION KPIs
    # ========================================================

    decision_col1, decision_col2, decision_col3 = (
        st.columns(3)
    )

    with decision_col1:

        st.metric(
            "✅ Approved",
            stats.get(
                "approved_transactions",
                0
            )
        )

    with decision_col2:

        st.metric(
            "⚠️ Manual Review",
            stats.get(
                "manual_review_transactions",
                0
            )
        )

    with decision_col3:

        st.metric(
            "🚫 Blocked",
            stats.get(
                "blocked_transactions",
                0
            )
        )


    # ========================================================
    # ANALYST CASE KPIs
    # ========================================================

    case_col1, case_col2, case_col3 = st.columns(3)

    with case_col1:

        st.metric(
            "📂 Open Review Cases",
            stats.get(
                "open_review_cases",
                0
            )
        )

    with case_col2:

        st.metric(
            "🔴 Confirmed Fraud",
            stats.get(
                "confirmed_fraud_cases",
                0
            )
        )

    with case_col3:

        st.metric(
            "🟢 False Positives",
            stats.get(
                "false_positive_cases",
                0
            )
        )


    # ========================================================
    # API STATUS
    # ========================================================

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

    genuine_transactions = max(
        stats.get(
            "total_transactions",
            0
        )
        -
        stats.get(
            "fraud_transactions",
            0
        ),
        0
    )

    fraud_transactions = stats.get(
        "fraud_transactions",
        0
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


    # ========================================================
    # SMART DECISION DISTRIBUTION
    # ========================================================

    st.subheader(
        "Smart Decision Distribution"
    )

    decision_distribution_df = pd.DataFrame(
        {
            "Decision": [
                "APPROVE",
                "MANUAL REVIEW",
                "BLOCK"
            ],

            "Count": [
                stats.get(
                    "approved_transactions",
                    0
                ),

                stats.get(
                    "manual_review_transactions",
                    0
                ),

                stats.get(
                    "blocked_transactions",
                    0
                )
            ]
        }
    )

    st.bar_chart(
        decision_distribution_df.set_index(
            "Decision"
        ),
        width="stretch"
    )

    st.caption(
        "The Smart Risk Decision Engine converts "
        "machine-learning outputs into business actions: "
        "APPROVE, MANUAL REVIEW, or BLOCK."
    )


    st.divider()


    # ========================================================
    # FETCH TRANSACTIONS
    # ========================================================

    try:

        transactions_response = requests.get(
            f"{API_BASE_URL}/transactions",
            params={
                "limit": 50
            },
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
            # FRAUD SCORE -> PERCENTAGE
            # ------------------------------------------------

            transactions_df[
                "fraud_score"
            ] = (
                transactions_df[
                    "fraud_score"
                ]
                * 100
            )


            # ------------------------------------------------
            # WHY FLAGGED
            # ------------------------------------------------

            if (
                "reason_codes"
                in transactions_df.columns
            ):

                transactions_df[
                    "Why Flagged?"
                ] = (
                    transactions_df[
                        "reason_codes"
                    ].apply(
                        format_reason_codes
                    )
                )

            else:

                transactions_df[
                    "Why Flagged?"
                ] = "—"


            # ------------------------------------------------
            # SAFE DEFAULTS FOR OLD RECORDS
            # ------------------------------------------------

            defaults = {
                "decision": "—",
                "priority": "—",
                "review_required": None,
                "decision_reason": None,
                "recommended_action": None,
                "case_status": "—",
                "analyst_verdict": "—",
                "analyst_notes": None,
                "reviewed_at": None
            }


            for column, default_value in defaults.items():

                if column not in transactions_df.columns:

                    transactions_df[
                        column
                    ] = default_value


            transactions_df[
                "decision"
            ] = (
                transactions_df[
                    "decision"
                ].fillna("—")
            )


            transactions_df[
                "priority"
            ] = (
                transactions_df[
                    "priority"
                ].fillna("—")
            )


            transactions_df[
                "case_status"
            ] = (
                transactions_df[
                    "case_status"
                ].fillna("—")
            )


            transactions_df[
                "analyst_verdict"
            ] = (
                transactions_df[
                    "analyst_verdict"
                ].fillna("—")
            )


            # ------------------------------------------------
            # REVIEW REQUIRED
            # ------------------------------------------------

            transactions_df[
                "Review Required"
            ] = (
                transactions_df[
                    "review_required"
                ].apply(
                    format_review_required
                )
            )


            # ------------------------------------------------
            # RENAME COLUMNS
            # ------------------------------------------------

            transactions_df.rename(
                columns={
                    "id":
                        "ID",

                    "amount":
                        "Amount",

                    "label":
                        "Prediction",

                    "fraud_score":
                        "Fraud Score (%)",

                    "anomaly_risk":
                        "Anomaly Risk",

                    "anomaly_status":
                        "Anomaly Status",

                    "created_at":
                        "Timestamp",

                    "decision":
                        "Decision",

                    "priority":
                        "Priority",

                    "case_status":
                        "Case Status",

                    "analyst_verdict":
                        "Analyst Verdict"
                },
                inplace=True
            )


            # =================================================
            # RECENT TRANSACTIONS TABLE
            # =================================================

            st.subheader(
                "Recent Transactions"
            )

            display_df = transactions_df[
                [
                    "ID",
                    "Amount",
                    "Prediction",
                    "Fraud Score (%)",
                    "Anomaly Risk",
                    "Decision",
                    "Priority",
                    "Review Required",
                    "Case Status",
                    "Analyst Verdict",
                    "Why Flagged?",
                    "Timestamp"
                ]
            ].head(20).copy()


            # ------------------------------------------------
            # ROW HIGHLIGHTING
            # ------------------------------------------------

            def highlight_transaction(row):

                decision = row[
                    "Decision"
                ]

                if decision == "BLOCK":

                    return [
                        "background-color: #ffcccc;"
                        "color: #8b0000;"
                        "font-weight: bold;"
                    ] * len(row)


                if decision == "MANUAL_REVIEW":

                    return [
                        "background-color: #fff3cd;"
                        "color: #664d03;"
                        "font-weight: bold;"
                    ] * len(row)


                if decision == "APPROVE":

                    return [
                        "background-color: #d1e7dd;"
                        "color: #0f5132;"
                    ] * len(row)


                if row[
                    "Prediction"
                ] == "Fraud":

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
                    highlight_transaction,
                    axis=1
                )
            )


            st.dataframe(
                styled_df,
                width="stretch"
            )


            st.caption(
                "Green = Approved • "
                "Yellow = Manual Review • "
                "Red = Blocked / Fraud Alert."
            )


            st.divider()


            # =================================================
            # ANALYST REVIEW QUEUE PREVIEW
            # =================================================

            st.subheader(
                "🧑‍💻 Analyst Review Queue"
            )


            review_queue = (
                transactions_df[
                    (
                        transactions_df[
                            "Review Required"
                        ] == "Yes"
                    )
                    &
                    (
                        transactions_df[
                            "Case Status"
                        ] != "CLOSED"
                    )
                ].copy()
            )


            if not review_queue.empty:

                review_queue_display = (
                    review_queue[
                        [
                            "ID",
                            "Amount",
                            "Prediction",
                            "Fraud Score (%)",
                            "Anomaly Risk",
                            "Decision",
                            "Priority",
                            "Case Status",
                            "Why Flagged?",
                            "Timestamp"
                        ]
                    ].copy()
                )


                priority_order = {
                    "CRITICAL": 1,
                    "HIGH": 2,
                    "MEDIUM": 3,
                    "LOW": 4,
                    "—": 5
                }


                review_queue_display[
                    "_priority_order"
                ] = (
                    review_queue_display[
                        "Priority"
                    ].map(
                        priority_order
                    ).fillna(5)
                )


                review_queue_display = (
                    review_queue_display
                    .sort_values(
                        by=[
                            "_priority_order",
                            "ID"
                        ],
                        ascending=[
                            True,
                            False
                        ]
                    )
                    .drop(
                        columns=[
                            "_priority_order"
                        ]
                    )
                )


                st.dataframe(
                    review_queue_display,
                    width="stretch",
                    hide_index=True
                )


                st.caption(
                    "Use the Analyst Case Management "
                    "section below to investigate and "
                    "close these cases."
                )


            else:

                st.success(
                    "No open transactions currently "
                    "require analyst review."
                )


            st.divider()


            # =================================================
            # LATEST FRAUD ALERT DETAILS
            # =================================================

            st.subheader(
                "🚨 Latest Fraud Alert Details"
            )


            fraud_rows = (
                transactions_df[
                    transactions_df[
                        "Prediction"
                    ] == "Fraud"
                ]
            )


            if not fraud_rows.empty:

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
                            latest_fraud[
                                "ID"
                            ]
                        )
                    )


                with detail_col2:

                    st.metric(
                        "Fraud Score",
                        (
                            f"{latest_fraud['Fraud Score (%)']:.2f}%"
                        )
                    )


                with detail_col3:

                    st.metric(
                        "Decision",
                        latest_fraud.get(
                            "Decision",
                            "—"
                        )
                    )


                with detail_col4:

                    st.metric(
                        "Priority",
                        latest_fraud.get(
                            "Priority",
                            "—"
                        )
                    )


                alert_col1, alert_col2 = (
                    st.columns(2)
                )


                with alert_col1:

                    st.write(
                        "**Amount:**",
                        f"{latest_fraud['Amount']:.2f}"
                    )

                    st.write(
                        "**Anomaly Risk:**",
                        f"{latest_fraud['Anomaly Risk']:.2f}"
                    )

                    st.write(
                        "**Case Status:**",
                        latest_fraud.get(
                            "Case Status",
                            "—"
                        )
                    )


                with alert_col2:

                    st.write(
                        "**Review Required:**",
                        latest_fraud[
                            "Review Required"
                        ]
                    )

                    st.write(
                        "**Analyst Verdict:**",
                        latest_fraud.get(
                            "Analyst Verdict",
                            "—"
                        )
                    )

                    st.write(
                        "**Detected At:**",
                        latest_fraud[
                            "Timestamp"
                        ]
                    )


                # --------------------------------------------
                # DECISION DETAILS
                # --------------------------------------------

                decision_reason = (
                    latest_fraud.get(
                        "decision_reason"
                    )
                )


                recommended_action = (
                    latest_fraud.get(
                        "recommended_action"
                    )
                )


                if decision_reason:

                    st.warning(
                        "Decision Reason: "
                        f"{decision_reason}"
                    )


                if recommended_action:

                    st.error(
                        "Recommended Action: "
                        f"{recommended_action}"
                    )


                # --------------------------------------------
                # EXPLAINABILITY
                # --------------------------------------------

                reason_codes = (
                    latest_fraud.get(
                        "reason_codes",
                        []
                    )
                )


                if (
                    isinstance(
                        reason_codes,
                        list
                    )
                    and reason_codes
                ):

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


                    explanation_df = (
                        pd.DataFrame(
                            explanation_rows
                        )
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
                        "They are not probability percentages."
                    )


                else:

                    st.info(
                        "Reason codes are not available "
                        "for this transaction."
                    )


            else:

                st.info(
                    "No fraud transaction is present "
                    "in the recent transaction window."
                )


            st.divider()


            # =================================================
            # ANOMALY RISK TREND
            # =================================================

            st.subheader(
                "Anomaly Risk Trend"
            )


            st.caption(
                "Isolation Forest anomaly risk for recent "
                "transactions. Risk >= 90 triggers an "
                "anomaly alert."
            )


            anomaly_chart_df = (
                transactions_df[
                    [
                        "ID",
                        "Anomaly Risk"
                    ]
                ]
                .head(20)
                .copy()
            )


            anomaly_chart_df = (
                anomaly_chart_df
                .sort_values(
                    "ID"
                )
            )


            anomaly_chart_df[
                "Alert Threshold"
            ] = 90.0


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


# ============================================================
# ANALYST CASE MANAGEMENT
# Not auto-refreshed while analyst is typing notes
# ============================================================

def analyst_case_management():

    st.divider()

    st.subheader(
        "🧑‍💼 Analyst Case Management"
    )

    st.caption(
        "Human-in-the-loop investigation workflow: "
        "NEW → UNDER_REVIEW → CONFIRMED_FRAUD / "
        "FALSE_POSITIVE → CLOSED"
    )


    # --------------------------------------------------------
    # DISPLAY ACTION RESULT MESSAGE
    # --------------------------------------------------------

    if "case_action_message" in st.session_state:

        st.success(
            st.session_state.pop(
                "case_action_message"
            )
        )


    try:

        response = requests.get(
            f"{API_BASE_URL}/review-cases",
            params={
                "limit": 100
            },
            timeout=5
        )

        response.raise_for_status()

        review_cases = (
            response.json()[
                "review_cases"
            ]
        )


    except requests.RequestException:

        st.warning(
            "Unable to load analyst review cases."
        )

        return


    if not review_cases:

        st.success(
            "No analyst review cases available."
        )

        return


    # --------------------------------------------------------
    # OPEN / CLOSED CASES
    # --------------------------------------------------------

    open_cases = [
        case
        for case in review_cases
        if case.get(
            "case_status"
        ) != "CLOSED"
    ]


    closed_cases = [
        case
        for case in review_cases
        if case.get(
            "case_status"
        ) == "CLOSED"
    ]


    # --------------------------------------------------------
    # OPEN CASE SELECTION
    # --------------------------------------------------------

    if open_cases:

        cases_by_id = {
            int(case["id"]): case
            for case in open_cases
        }


        selected_id = st.selectbox(
            "Select a case to investigate",
            options=list(
                cases_by_id.keys()
            ),
            format_func=lambda case_id: (
                f"Transaction #{case_id} | "
                f"{cases_by_id[case_id].get('decision', '—')} | "
                f"{cases_by_id[case_id].get('priority', '—')} | "
                f"{cases_by_id[case_id].get('case_status', '—')}"
            ),
            key="analyst_case_selector"
        )


        selected_case = (
            cases_by_id[
                selected_id
            ]
        )


        # ----------------------------------------------------
        # CASE SUMMARY
        # ----------------------------------------------------

        case_col1, case_col2, case_col3, case_col4 = (
            st.columns(4)
        )


        with case_col1:

            st.metric(
                "Transaction ID",
                selected_case[
                    "id"
                ]
            )


        with case_col2:

            st.metric(
                "Decision",
                selected_case.get(
                    "decision",
                    "—"
                )
            )


        with case_col3:

            st.metric(
                "Priority",
                selected_case.get(
                    "priority",
                    "—"
                )
            )


        with case_col4:

            st.metric(
                "Case Status",
                selected_case.get(
                    "case_status",
                    "—"
                )
            )


        detail_col1, detail_col2 = (
            st.columns(2)
        )


        with detail_col1:

            st.write(
                "**Prediction:**",
                selected_case.get(
                    "label",
                    "—"
                )
            )

            st.write(
                "**Amount:**",
                selected_case.get(
                    "amount",
                    0
                )
            )

            fraud_score_percent = (
                float(
                    selected_case.get(
                        "fraud_score",
                        0
                    )
                )
                * 100
            )

            st.write(
                "**Fraud Score:**",
                f"{fraud_score_percent:.2f}%"
            )


        with detail_col2:

            st.write(
                "**Anomaly Risk:**",
                f"{float(selected_case.get('anomaly_risk', 0)):.2f}"
            )

            st.write(
                "**Why Flagged?:**",
                format_reason_codes(
                    selected_case.get(
                        "reason_codes",
                        []
                    )
                )
            )

            st.write(
                "**Detected At:**",
                selected_case.get(
                    "created_at",
                    "—"
                )
            )


        decision_reason = (
            selected_case.get(
                "decision_reason"
            )
        )


        recommended_action = (
            selected_case.get(
                "recommended_action"
            )
        )


        if decision_reason:

            st.warning(
                f"Decision Reason: "
                f"{decision_reason}"
            )


        if recommended_action:

            st.info(
                f"Recommended Action: "
                f"{recommended_action}"
            )


        # ----------------------------------------------------
        # ANALYST NOTES
        # ----------------------------------------------------

        notes = st.text_area(
            "Analyst Notes",
            value=(
                selected_case.get(
                    "analyst_notes"
                )
                or ""
            ),
            placeholder=(
                "Enter investigation notes..."
            ),
            key=(
                f"analyst_notes_"
                f"{selected_id}"
            )
        )


        # ----------------------------------------------------
        # HELPER FOR PATCH ACTION
        # ----------------------------------------------------

        def submit_case_action(
            case_status,
            verdict=None
        ):

            payload = {
                "case_status":
                    case_status,

                "analyst_verdict":
                    verdict,

                "analyst_notes":
                    notes
            }


            try:

                action_response = requests.patch(
                    (
                        f"{API_BASE_URL}/"
                        f"review-cases/"
                        f"{selected_id}"
                    ),
                    json=payload,
                    timeout=5
                )

                action_response.raise_for_status()


                st.session_state[
                    "case_action_message"
                ] = (
                    f"Transaction #{selected_id} "
                    f"updated successfully."
                )


                st.rerun()


            except requests.RequestException as error:

                st.error(
                    "Unable to update case: "
                    f"{error}"
                )


        # ----------------------------------------------------
        # CASE ACTION BUTTONS
        # ----------------------------------------------------

        action_col1, action_col2, action_col3 = (
            st.columns(3)
        )


        with action_col1:

            if st.button(
                "🔎 Start Review",
                width="stretch",
                key=(
                    f"start_review_"
                    f"{selected_id}"
                )
            ):

                submit_case_action(
                    "UNDER_REVIEW",
                    None
                )


        with action_col2:

            if st.button(
                "🚨 Confirm Fraud",
                width="stretch",
                key=(
                    f"confirm_fraud_"
                    f"{selected_id}"
                )
            ):

                submit_case_action(
                    "CLOSED",
                    "CONFIRMED_FRAUD"
                )


        with action_col3:

            if st.button(
                "✅ Mark False Positive",
                width="stretch",
                key=(
                    f"false_positive_"
                    f"{selected_id}"
                )
            ):

                submit_case_action(
                    "CLOSED",
                    "FALSE_POSITIVE"
                )


    else:

        st.success(
            "No open analyst cases. "
            "All review cases have been resolved."
        )


    # --------------------------------------------------------
    # CLOSED CASE HISTORY
    # --------------------------------------------------------

    if closed_cases:

        with st.expander(
            "📚 Closed Case History"
        ):

            closed_rows = []


            for case in closed_cases:

                closed_rows.append(
                    {
                        "Transaction ID":
                            case.get(
                                "id"
                            ),

                        "Prediction":
                            case.get(
                                "label"
                            ),

                        "Decision":
                            case.get(
                                "decision"
                            ),

                        "Priority":
                            case.get(
                                "priority"
                            ),

                        "Verdict":
                            case.get(
                                "analyst_verdict"
                            ),

                        "Notes":
                            case.get(
                                "analyst_notes"
                            ),

                        "Reviewed At":
                            case.get(
                                "reviewed_at"
                            )
                    }
                )


            closed_df = pd.DataFrame(
                closed_rows
            )


            st.dataframe(
                closed_df,
                width="stretch",
                hide_index=True
            )


# ============================================================
# RUN DASHBOARD
# ============================================================

live_dashboard()

analyst_case_management()


# ============================================================
# SYSTEM INFORMATION
# ============================================================

st.divider()

st.subheader(
    "System Information"
)


info_col1, info_col2, info_col3, info_col4 = (
    st.columns(4)
)


with info_col1:

    st.write(
        "**Primary Model**"
    )

    st.write(
        "SMOTE + LightGBM"
    )


with info_col2:

    st.write(
        "**Anomaly Detector**"
    )

    st.write(
        "Isolation Forest"
    )


with info_col3:

    st.write(
        "**Decision Engine**"
    )

    st.write(
        "Smart Risk Engine"
    )


with info_col4:

    st.write(
        "**Test ROC-AUC**"
    )

    st.write(
        "0.9911"
    )