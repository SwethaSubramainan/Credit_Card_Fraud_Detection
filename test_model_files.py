# ============================================================
# VERIFY SAVED MODEL FILES
# ============================================================

import os
import json

# Path to model folder
model_folder = "models"

# Required files
required_files = [
    "lightgbm_fraud_model.pkl",
    "scaler.pkl",
    "model_metadata.json"
]

# Check whether all files exist
for file_name in required_files:
    file_path = os.path.join(model_folder, file_name)

    if os.path.exists(file_path):
        print(f"{file_name} -> FOUND")
    else:
        print(f"{file_name} -> NOT FOUND")


# Read model metadata
metadata_path = os.path.join(
    model_folder,
    "model_metadata.json"
)

with open(metadata_path, "r") as file:
    metadata = json.load(file)

print("\nModel Name:", metadata["model_name"])
print("Threshold:", metadata["threshold"])
print("Number of Features:", len(metadata["features"]))
print("Test Precision:", metadata["test_precision"])
print("Test Recall:", metadata["test_recall"])
print("Test F1 Score:", metadata["test_f1_score"])
print("Test Average Precision:", metadata["test_average_precision"])
print("Test ROC-AUC:", metadata["test_roc_auc"])