# ============================================================
# AUTOMATED TESTS FOR FRAUDGUARD AI FASTAPI
# ============================================================

import unittest

from unittest.mock import patch

from fastapi.testclient import TestClient

from api.main import app


# ------------------------------------------------------------
# CREATE TEST CLIENT
# ------------------------------------------------------------

client = TestClient(app)


# ============================================================
# API TEST CASES
# ============================================================

class TestFraudDetectionAPI(unittest.TestCase):


    # --------------------------------------------------------
    # TEST HOME ENDPOINT
    # --------------------------------------------------------

    def test_home_endpoint(self):

        response = client.get("/")

        self.assertEqual(
            response.status_code,
            200
        )

        data = response.json()

        self.assertEqual(
            data["status"],
            "running"
        )

        self.assertIn(
            "message",
            data
        )

        self.assertEqual(
            data["version"],
            "3.0.0"
        )


    # --------------------------------------------------------
    # TEST HEALTH ENDPOINT
    # --------------------------------------------------------

    def test_health_endpoint(self):

        response = client.get(
            "/health"
        )

        self.assertEqual(
            response.status_code,
            200
        )

        data = response.json()

        self.assertEqual(
            data["status"],
            "healthy"
        )

        self.assertEqual(
            data["model"],
            "SMOTE + LightGBM"
        )

        self.assertEqual(
            data["anomaly_detector"],
            "Isolation Forest"
        )

        self.assertIn(
            "explainability",
            data
        )

        self.assertIn(
            "risk_engine",
            data
        )

        self.assertIn(
            "case_management",
            data
        )


    # --------------------------------------------------------
    # TEST STATISTICS ENDPOINT
    # --------------------------------------------------------

    def test_statistics_endpoint(self):

        response = client.get(
            "/stats"
        )

        self.assertEqual(
            response.status_code,
            200
        )

        data = response.json()


        expected_fields = [
            "total_transactions",
            "fraud_transactions",
            "anomalous_transactions",
            "approved_transactions",
            "manual_review_transactions",
            "blocked_transactions",
            "open_review_cases",
            "confirmed_fraud_cases",
            "false_positive_cases"
        ]


        for field in expected_fields:

            self.assertIn(
                field,
                data
            )

            self.assertGreaterEqual(
                data[field],
                0
            )


    # --------------------------------------------------------
    # TEST RECENT TRANSACTIONS ENDPOINT
    # --------------------------------------------------------

    def test_transactions_endpoint(self):

        response = client.get(
            "/transactions",
            params={
                "limit": 5
            }
        )

        self.assertEqual(
            response.status_code,
            200
        )

        data = response.json()

        self.assertIn(
            "transactions",
            data
        )

        self.assertIsInstance(
            data["transactions"],
            list
        )

        self.assertLessEqual(
            len(
                data["transactions"]
            ),
            5
        )


    # --------------------------------------------------------
    # VALIDATE TRANSACTION RESPONSE STRUCTURE
    # --------------------------------------------------------

    def test_transaction_structure(self):

        response = client.get(
            "/transactions",
            params={
                "limit": 1
            }
        )

        self.assertEqual(
            response.status_code,
            200
        )

        transactions = (
            response.json()[
                "transactions"
            ]
        )


        if transactions:

            transaction = (
                transactions[0]
            )


            expected_fields = [
                "id",
                "transaction_time",
                "amount",
                "prediction",
                "label",
                "fraud_score",
                "threshold",
                "anomaly_risk",
                "anomaly_status",
                "created_at",
                "reason_codes",
                "decision",
                "priority",
                "review_required",
                "decision_reason",
                "recommended_action",
                "case_status",
                "analyst_verdict",
                "analyst_notes",
                "reviewed_at"
            ]


            for field in expected_fields:

                self.assertIn(
                    field,
                    transaction
                )


            self.assertIsInstance(
                transaction[
                    "reason_codes"
                ],
                list
            )


    # --------------------------------------------------------
    # TEST ANALYST REVIEW QUEUE ENDPOINT
    # --------------------------------------------------------

    def test_review_cases_endpoint(self):

        response = client.get(
            "/review-cases",
            params={
                "limit": 5
            }
        )

        self.assertEqual(
            response.status_code,
            200
        )

        data = response.json()

        self.assertIn(
            "review_cases",
            data
        )

        self.assertIsInstance(
            data["review_cases"],
            list
        )

        self.assertLessEqual(
            len(
                data["review_cases"]
            ),
            5
        )


    # --------------------------------------------------------
    # VALIDATE REVIEW CASE STRUCTURE
    # --------------------------------------------------------

    def test_review_case_structure(self):

        response = client.get(
            "/review-cases",
            params={
                "limit": 1
            }
        )

        self.assertEqual(
            response.status_code,
            200
        )

        review_cases = (
            response.json()[
                "review_cases"
            ]
        )


        if review_cases:

            case = review_cases[0]


            expected_fields = [
                "id",
                "prediction",
                "label",
                "fraud_score",
                "anomaly_risk",
                "decision",
                "priority",
                "review_required",
                "case_status",
                "analyst_verdict",
                "analyst_notes",
                "reviewed_at"
            ]


            for field in expected_fields:

                self.assertIn(
                    field,
                    case
                )


            self.assertTrue(
                case[
                    "review_required"
                ]
            )


    # --------------------------------------------------------
    # CLOSED CASE REQUIRES ANALYST VERDICT
    # --------------------------------------------------------

    def test_closed_case_requires_verdict(self):

        payload = {
            "case_status":
                "CLOSED",

            "analyst_verdict":
                None,

            "analyst_notes":
                "Test validation only."
        }


        response = client.patch(
            "/review-cases/999999999",
            json=payload
        )


        self.assertEqual(
            response.status_code,
            400
        )


        data = response.json()

        self.assertIn(
            "requires an analyst verdict",
            data["detail"]
        )


    # --------------------------------------------------------
    # INVALID ANALYST VERDICT SHOULD FAIL VALIDATION
    # --------------------------------------------------------

    def test_invalid_analyst_verdict(self):

        payload = {
            "case_status":
                "CLOSED",

            "analyst_verdict":
                "UNKNOWN_VERDICT",

            "analyst_notes":
                "Invalid verdict test."
        }


        response = client.patch(
            "/review-cases/999999999",
            json=payload
        )


        self.assertEqual(
            response.status_code,
            422
        )


    # --------------------------------------------------------
    # NONEXISTENT TRANSACTION SHOULD RETURN 404
    # --------------------------------------------------------

    def test_nonexistent_review_case(self):

        payload = {
            "case_status":
                "UNDER_REVIEW",

            "analyst_verdict":
                None,

            "analyst_notes":
                "Testing nonexistent transaction."
        }


        response = client.patch(
            "/review-cases/999999999",
            json=payload
        )


        self.assertEqual(
            response.status_code,
            404
        )
    # --------------------------------------------------------
    # TEST ANALYST NOTES
    # --------------------------------------------------------

    @patch(
        "api.main.update_case_review",
        return_value=True
    )
    def test_analyst_notes(
        self,
        mock_update_case_review
    ):

        analyst_note = (
            "Analyst reviewed the transaction "
            "and checked the anomaly alert."
        )

        payload = {
            "case_status":
                "UNDER_REVIEW",

            "analyst_verdict":
                None,

            "analyst_notes":
                analyst_note
        }


        response = client.patch(
            "/review-cases/123456",
            json=payload
        )


        self.assertEqual(
            response.status_code,
            200
        )


        data = response.json()


        self.assertEqual(
            data["analyst_notes"],
            analyst_note
        )


        mock_update_case_review.assert_called_once_with(
            transaction_id=123456,
            case_status="UNDER_REVIEW",
            analyst_verdict=None,
            analyst_notes=analyst_note
        )


# ============================================================
# RUN TESTS DIRECTLY
# ============================================================

if __name__ == "__main__":

    unittest.main(
        verbosity=2
    )