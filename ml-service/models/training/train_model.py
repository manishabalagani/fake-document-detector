import os

import joblib
import pandas as pd

from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    classification_report
)


# ============================================================
# Paths
# ============================================================

DATASET_PATH = (
    "models/training/dataset.csv"
)

MODEL_PATH = (
    "models/trained/"
    "document_detector.joblib"
)


# ============================================================
# Load dataset
# ============================================================

df = pd.read_csv(
    DATASET_PATH
)

print("\nDataset:")
print(df)


# ============================================================
# Separate features and label
# ============================================================

X = df.drop(
    columns=["label"]
)

y = df["label"]


# ============================================================
# Train / Test split
# ============================================================

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.25,
    random_state=42,
    stratify=y
)


print("\nTraining samples:")
print(len(X_train))

print("\nTesting samples:")
print(len(X_test))


# ============================================================
# Create model
# ============================================================

model = RandomForestClassifier(
    n_estimators=200,
    random_state=42,
    class_weight="balanced"
)


# ============================================================
# Train
# ============================================================

model.fit(
    X_train,
    y_train
)


# ============================================================
# Predict
# ============================================================

predictions = model.predict(
    X_test
)


# ============================================================
# Evaluation
# ============================================================

accuracy = accuracy_score(
    y_test,
    predictions
)

precision = precision_score(
    y_test,
    predictions,
    zero_division=0
)

recall = recall_score(
    y_test,
    predictions,
    zero_division=0
)

f1 = f1_score(
    y_test,
    predictions,
    zero_division=0
)


print("\n==============================")
print("MODEL EVALUATION")
print("==============================")

print(
    f"Accuracy : {accuracy:.4f}"
)

print(
    f"Precision: {precision:.4f}"
)

print(
    f"Recall   : {recall:.4f}"
)

print(
    f"F1 Score : {f1:.4f}"
)

print("\nClassification Report:")

print(
    classification_report(
        y_test,
        predictions,
        zero_division=0
    )
)


# ============================================================
# Feature importance
# ============================================================

importance = pd.DataFrame({
    "feature": X.columns,
    "importance": model.feature_importances_
})

importance = importance.sort_values(
    by="importance",
    ascending=False
)

print("\nFeature Importance:")

print(
    importance
)


# ============================================================
# Save model
# ============================================================

os.makedirs(
    "models/trained",
    exist_ok=True
)

joblib.dump(
    model,
    MODEL_PATH
)

print(
    f"\nModel saved to: {MODEL_PATH}"
)