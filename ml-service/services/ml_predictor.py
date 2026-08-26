from pathlib import Path
from typing import Any, Dict

import joblib
import pandas as pd


# ============================================================
# MODEL CONFIGURATION
# ============================================================

# Current file:
#
# ml-service/
# └── services/
#     └── ml_predictor.py
#
# parent       -> services
# parent.parent -> ml-service
#
# Therefore the model is:
#
# ml-service/
# └── models/
#     └── trained/
#         └── document_detector.joblib

BASE_DIR = Path(__file__).resolve().parent.parent

MODEL_PATH = (
    BASE_DIR
    / "models"
    / "trained"
    / "document_detector.joblib"
)


# ============================================================
# FEATURE ORDER
# ============================================================

# IMPORTANT:
# This order MUST match the feature order used during training.

FEATURE_ORDER = [
    "metadata_score",
    "text_score",
    "missing_field_count",
    "repeated_text_count",
    "text_length",
    "average_blur",
    "average_contrast",
    "average_brightness",
    "tampering_score",
]


# ============================================================
# FEATURE DEFAULTS
# ============================================================

FEATURE_DEFAULTS = {
    "metadata_score": 0.0,
    "text_score": 0.0,
    "missing_field_count": 0.0,
    "repeated_text_count": 0.0,
    "text_length": 0.0,
    "average_blur": 0.0,
    "average_contrast": 0.0,
    "average_brightness": 0.0,
    "tampering_score": 0.0,
}


# ============================================================
# MODEL CACHE
# ============================================================

_MODEL = None


# ============================================================
# SAFE NUMBER CONVERSION
# ============================================================

def safe_float(
    value: Any,
    default: float = 0.0
) -> float:
    """
    Safely convert a value to float.

    Invalid, missing, NaN and infinite values
    are replaced with the supplied default.
    """

    try:
        number = float(value)

    except (
        TypeError,
        ValueError
    ):
        return default

    if pd.isna(number):
        return default

    if number == float("inf"):
        return default

    if number == float("-inf"):
        return default

    return number


# ============================================================
# LOAD MODEL
# ============================================================

def load_model():
    """
    Load the trained document detection model.

    The model is cached after the first successful load
    so that every request does not reload the .joblib file.
    """

    global _MODEL

    # --------------------------------------------------------
    # Return cached model
    # --------------------------------------------------------

    if _MODEL is not None:
        return _MODEL

    # --------------------------------------------------------
    # Check model path
    # --------------------------------------------------------

    if not MODEL_PATH.exists():

        raise FileNotFoundError(
            "Trained model not found: "
            f"{MODEL_PATH}"
        )

    if not MODEL_PATH.is_file():

        raise FileNotFoundError(
            "Model path is not a file: "
            f"{MODEL_PATH}"
        )

    # --------------------------------------------------------
    # Load model
    # --------------------------------------------------------

    try:

        _MODEL = joblib.load(
            MODEL_PATH
        )

    except Exception as exc:

        raise RuntimeError(
            "Failed to load trained document "
            f"detection model: {exc}"
        ) from exc

    return _MODEL


# ============================================================
# VALIDATE MODEL
# ============================================================

def validate_model(model):
    """
    Validate that the loaded object looks like a
    classification model.

    The predictor requires:

        predict()

    and preferably:

        predict_proba()
        classes_
    """

    if not hasattr(
        model,
        "predict"
    ):

        raise TypeError(
            "Loaded model does not provide "
            "a predict() method."
        )

    if not hasattr(
        model,
        "predict_proba"
    ):

        raise TypeError(
            "Loaded model does not provide "
            "predict_proba(). Probability "
            "output is required."
        )

    if not hasattr(
        model,
        "classes_"
    ):

        raise TypeError(
            "Loaded model does not provide "
            "classes_."
        )


# ============================================================
# BUILD FEATURE VECTOR
# ============================================================

def build_feature_vector(
    features: Dict[str, Any]
):
    """
    Convert the feature dictionary into the exact
    feature vector expected by the trained model.
    """

    if not isinstance(
        features,
        dict
    ):

        features = {}

    feature_values = []

    for feature_name in FEATURE_ORDER:

        value = features.get(
            feature_name,
            FEATURE_DEFAULTS.get(
                feature_name,
                0.0
            )
        )

        value = safe_float(
            value
        )

        feature_values.append(
            value
        )

    return feature_values


# ============================================================
# BUILD DATAFRAME
# ============================================================

def build_feature_dataframe(
    features: Dict[str, Any]
):
    """
    Create a one-row DataFrame using the exact
    training feature order.
    """

    feature_values = build_feature_vector(
        features
    )

    return pd.DataFrame(
        [feature_values],
        columns=FEATURE_ORDER
    )


# ============================================================
# GET CLASS PROBABILITIES
# ============================================================

def get_class_probabilities(
    model,
    probabilities
):
    """
    Convert model probability output into:

        genuine_probability
        suspicious_probability

    Expected class convention:

        0 = GENUINE
        1 = SUSPICIOUS

    """

    genuine_probability = 0.0
    suspicious_probability = 0.0

    classes = list(
        model.classes_
    )

    for class_value, probability in zip(
        classes,
        probabilities
    ):

        probability = safe_float(
            probability
        )

        # ----------------------------------------------------
        # Numeric class labels
        # ----------------------------------------------------

        try:

            numeric_class = int(
                class_value
            )

            if numeric_class == 0:

                genuine_probability = probability

            elif numeric_class == 1:

                suspicious_probability = probability

            continue

        except (
            TypeError,
            ValueError
        ):

            pass

        # ----------------------------------------------------
        # String class labels
        # ----------------------------------------------------

        class_text = str(
            class_value
        ).strip().lower()

        if class_text in {
            "0",
            "genuine",
            "real",
            "authentic"
        }:

            genuine_probability = probability

        elif class_text in {
            "1",
            "suspicious",
            "fake",
            "forged",
            "fraud"
        }:

            suspicious_probability = probability

    return (
        genuine_probability,
        suspicious_probability
    )


# ============================================================
# PREDICT DOCUMENT
# ============================================================

def predict_document(
    features: Dict[str, Any]
):
    """
    Predict whether a document is genuine or suspicious.

    Returns:

        {
            "prediction": "GENUINE" | "SUSPICIOUS",
            "genuine_probability": float,
            "suspicious_probability": float
        }
    """

    # --------------------------------------------------------
    # Load model
    # --------------------------------------------------------

    model = load_model()

    # --------------------------------------------------------
    # Validate model
    # --------------------------------------------------------

    validate_model(
        model
    )

    # --------------------------------------------------------
    # Build feature DataFrame
    # --------------------------------------------------------

    X = build_feature_dataframe(
        features
    )

    # --------------------------------------------------------
    # Prediction
    # --------------------------------------------------------

    try:

        raw_prediction = model.predict(
            X
        )[0]

    except Exception as exc:

        raise RuntimeError(
            "Model prediction failed: "
            f"{exc}"
        ) from exc

    # --------------------------------------------------------
    # Probability
    # --------------------------------------------------------

    try:

        probabilities = model.predict_proba(
            X
        )[0]

    except Exception as exc:

        raise RuntimeError(
            "Model probability prediction failed: "
            f"{exc}"
        ) from exc

    # --------------------------------------------------------
    # Extract probabilities
    # --------------------------------------------------------

    (
        genuine_probability,
        suspicious_probability
    ) = get_class_probabilities(
        model,
        probabilities
    )

    # --------------------------------------------------------
    # Determine label
    # --------------------------------------------------------

    try:

        numeric_prediction = int(
            raw_prediction
        )

        if numeric_prediction == 1:

            label = "SUSPICIOUS"

        elif numeric_prediction == 0:

            label = "GENUINE"

        else:

            label = str(
                raw_prediction
            ).upper()

    except (
        TypeError,
        ValueError
    ):

        prediction_text = str(
            raw_prediction
        ).strip().lower()

        if prediction_text in {
            "suspicious",
            "fake",
            "forged",
            "fraud",
            "1"
        }:

            label = "SUSPICIOUS"

        else:

            label = "GENUINE"

    # --------------------------------------------------------
    # Normalize probabilities
    # --------------------------------------------------------

    genuine_probability = max(
        0.0,
        min(
            genuine_probability,
            1.0
        )
    )

    suspicious_probability = max(
        0.0,
        min(
            suspicious_probability,
            1.0
        )
    )

    # --------------------------------------------------------
    # Return
    # --------------------------------------------------------

    return {
        "prediction": label,

        "genuine_probability": round(
            genuine_probability,
            4
        ),

        "suspicious_probability": round(
            suspicious_probability,
            4
        )
    }


# ============================================================
# MODEL INFORMATION
# ============================================================

def get_model_info():
    """
    Return useful information about the loaded model.
    """

    model = load_model()

    validate_model(
        model
    )

    return {
        "model_path": str(
            MODEL_PATH
        ),

        "model_type": type(
            model
        ).__name__,

        "classes": [
            str(value)
            for value in model.classes_
        ],

        "feature_order": FEATURE_ORDER
    }