from services.ml_predictor import (
    predict_document
)


features = {
    "metadata_score": 60,

    "text_score": 50,

    "missing_field_count": 3,

    "repeated_text_count": 2,

    "text_length": 600,

    "average_blur": 50,

    "average_contrast": 35,

    "average_brightness": 240,

    "tampering_score": 75
}


result = predict_document(
    features
)


print("\n==============================")
print("ML PREDICTION")
print("==============================")

print(
    "Prediction:",
    result["prediction"]
)

print(
    "Suspicious probability:",
    result[
        "suspicious_probability"
    ]
)

print(
    "Genuine probability:",
    result[
        "genuine_probability"
    ]
)