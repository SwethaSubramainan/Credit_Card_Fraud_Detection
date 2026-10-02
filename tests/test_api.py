# ============================================================
# AUTOMATED TESTS FOR FRAUD DETECTION FASTAPI
# ============================================================

import unittest

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

        self.assertIn(
            "total_transactions",
            data
        )

        self.assertIn(
            "fraud_transactions",
            data
        )

        self.assertIn(
            "anomalous_transactions",
            data
        )

        # Counts should never be negative
        self.assertGreaterEqual(
            data["total_transactions"],
            0
        )

        self.assertGreaterEqual(
            data["fraud_transactions"],
            0
        )

        self.assertGreaterEqual(
            data["anomalous_transactions"],
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

        # Endpoint must respect requested limit
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


        # Only validate structure when
        # at least one transaction exists
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
                "reason_codes"
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


# ============================================================
# RUN TESTS DIRECTLY
# ============================================================

if __name__ == "__main__":

    unittest.main(
        verbosity=2
    )