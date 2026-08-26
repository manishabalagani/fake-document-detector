from typing import Any, Dict

from services.ml_predictor import predict_document


# ============================================================
# SAFE NUMBER
# ============================================================

def safe_float(
    value: Any,
    default: float = 0.0
) -> float:

    try:

        value = float(
            value
        )

    except (
        TypeError,
        ValueError
    ):

        return default

    if value != value:  # NaN
        return default

    if value == float("inf"):
        return default

    if value == float("-inf"):
        return default

    return value


# ============================================================
# AVERAGE IMAGE VALUE
# ============================================================

def calculate_average_image_value(
    image_analysis,
    key
):
    """
    Calculate the average value of an image-analysis
    property across all pages.
    """

    if not isinstance(
        image_analysis,
        dict
    ):

        return 0.0

    pages = image_analysis.get(
        "pages",
        []
    )

    if not isinstance(
        pages,
        list
    ):

        return 0.0

    values = []

    for page in pages:

        if not isinstance(
            page,
            dict
        ):

            continue

        analysis = page.get(
            "analysis",
            {}
        )

        if not isinstance(
            analysis,
            dict
        ):

            continue

        value = analysis.get(
            key
        )

        if value is None:
            continue

        value = safe_float(
            value,
            default=None
        )

        if value is not None:

            values.append(
                value
            )

    if not values:

        return 0.0

    return (
        sum(values)
        / len(values)
    )


# ============================================================
# AVERAGE TAMPERING
# ============================================================

def calculate_average_tampering(
    tampering_analysis
):
    """
    Calculate the average anomaly score
    across document pages.
    """

    if not isinstance(
        tampering_analysis,
        dict
    ):

        return 0.0

    pages = tampering_analysis.get(
        "pages",
        []
    )

    if not isinstance(
        pages,
        list
    ):

        return 0.0

    scores = []

    for page in pages:

        if not isinstance(
            page,
            dict
        ):

            continue

        analysis = page.get(
            "analysis",
            {}
        )

        if not isinstance(
            analysis,
            dict
        ):

            continue

        score = analysis.get(
            "anomaly_score"
        )

        if score is None:
            continue

        score = safe_float(
            score,
            default=None
        )

        if score is not None:

            scores.append(
                score
            )

    if not scores:

        return 0.0

    return (
        sum(scores)
        / len(scores)
    )


# ============================================================
# BUILD ML FEATURES
# ============================================================

def build_ml_features(
    metadata_analysis,
    text_analysis,
    image_analysis,
    tampering_analysis
):
    """
    Build the exact feature dictionary expected
    by the ML predictor.
    """

    if not isinstance(
        metadata_analysis,
        dict
    ):

        metadata_analysis = {}

    if not isinstance(
        text_analysis,
        dict
    ):

        text_analysis = {}

    if not isinstance(
        image_analysis,
        dict
    ):

        image_analysis = {}

    if not isinstance(
        tampering_analysis,
        dict
    ):

        tampering_analysis = {}

    # --------------------------------------------------------
    # Metadata
    # --------------------------------------------------------

    metadata_score = safe_float(
        metadata_analysis.get(
            "score",
            0
        )
    )

    # --------------------------------------------------------
    # Text
    # --------------------------------------------------------

    text_score = safe_float(
        text_analysis.get(
            "score",
            0
        )
    )

    missing_fields = text_analysis.get(
        "missing_fields",
        []
    )

    if not isinstance(
        missing_fields,
        list
    ):

        missing_fields = []

    missing_field_count = len(
        missing_fields
    )

    repeated_text = text_analysis.get(
        "repeated_text",
        []
    )

    if not isinstance(
        repeated_text,
        list
    ):

        repeated_text = []

    repeated_text_count = len(
        repeated_text
    )

    text_length = safe_float(
        text_analysis.get(
            "text_length",
            0
        )
    )

    # --------------------------------------------------------
    # Image
    # --------------------------------------------------------

    average_blur = calculate_average_image_value(
        image_analysis,
        "blur_score"
    )

    average_contrast = calculate_average_image_value(
        image_analysis,
        "contrast"
    )

    average_brightness = calculate_average_image_value(
        image_analysis,
        "brightness"
    )

    # --------------------------------------------------------
    # Tampering
    # --------------------------------------------------------

    tampering_score = calculate_average_tampering(
        tampering_analysis
    )

    # --------------------------------------------------------
    # Final feature dictionary
    # --------------------------------------------------------

    return {
        "metadata_score": round(
            metadata_score,
            2
        ),

        "text_score": round(
            text_score,
            2
        ),

        "missing_field_count": int(
            missing_field_count
        ),

        "repeated_text_count": int(
            repeated_text_count
        ),

        "text_length": int(
            text_length
        ),

        "average_blur": round(
            average_blur,
            2
        ),

        "average_contrast": round(
            average_contrast,
            2
        ),

        "average_brightness": round(
            average_brightness,
            2
        ),

        "tampering_score": round(
            tampering_score,
            2
        )
    }


# ============================================================
# RUN ML ANALYSIS
# ============================================================

def run_ml_analysis(
    metadata_analysis,
    text_analysis,
    image_analysis,
    tampering_analysis
):
    """
    Build ML features and run the trained model.
    """

    features = build_ml_features(
        metadata_analysis=metadata_analysis,
        text_analysis=text_analysis,
        image_analysis=image_analysis,
        tampering_analysis=tampering_analysis
    )

    prediction = predict_document(
        features
    )

    return {
        "features": features,
        "prediction": prediction
    }