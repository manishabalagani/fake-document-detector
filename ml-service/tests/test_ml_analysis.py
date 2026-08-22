from services.ml_analysis import (
    run_ml_analysis
)


analysis_result = {

    "metadata_analysis": {
        "score": 60,
        "findings": []
    },

    "text_analysis": {
        "score": 50,
        "document_type": "certificate",
        "missing_fields": [
            "certificate_number",
            "date"
        ],
        "repeated_text": [],
        "text_length": 600,
        "findings": []
    },

    "image_analysis": {
        "pages": [
            {
                "page": 1,
                "analysis": {
                    "blur_score": 50,
                    "contrast": 35,
                    "brightness": 240
                }
            }
        ]
    },

    "tampering_analysis": {
        "pages": [
            {
                "page": 1,
                "analysis": {
                    "anomaly_score": 75
                }
            }
        ]
    }
}


result = run_ml_analysis(
    analysis_result
)


print("\n==============================")
print("ML ANALYSIS")
print("==============================")


print("\nFEATURES:")

for key, value in result[
    "features"
].items():

    print(
        f"{key}: {value}"
    )


print("\nPREDICTION:")

for key, value in result[
    "prediction"
].items():

    print(
        f"{key}: {value}"
    )