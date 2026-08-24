def extract_features(analysis_result):
    """
    Convert document analysis results into
    numerical ML features.
    """

    metadata = analysis_result.get(
        "metadata_analysis",
        {}
    )

    text = analysis_result.get(
        "text_analysis",
        {}
    )

    image = analysis_result.get(
        "image_analysis",
        {}
    )

    tampering = analysis_result.get(
        "tampering_analysis",
        {}
    )

    # --------------------------------------------------
    # Metadata
    # --------------------------------------------------

    metadata_score = metadata.get(
        "score",
        0
    )

    # --------------------------------------------------
    # Text
    # --------------------------------------------------

    text_score = text.get(
        "score",
        0
    )

    missing_fields = len(
        text.get(
            "missing_fields",
            []
        )
    )

    repeated_text = len(
        text.get(
            "repeated_text",
            []
        )
    )

    text_length = text.get(
        "text_length",
        0
    )

    # --------------------------------------------------
    # Image
    # --------------------------------------------------

    image_pages = image.get(
        "pages",
        []
    )

    blur_scores = []
    contrast_scores = []
    brightness_scores = []

    for page in image_pages:

        analysis = page.get(
            "analysis",
            {}
        )

        blur_scores.append(
            float(
                analysis.get(
                    "blur_score",
                    0
                )
            )
        )

        contrast_scores.append(
            float(
                analysis.get(
                    "contrast",
                    0
                )
            )
        )

        brightness_scores.append(
            float(
                analysis.get(
                    "brightness",
                    0
                )
            )
        )

    if blur_scores:
        average_blur = (
            sum(blur_scores)
            / len(blur_scores)
        )
    else:
        average_blur = 0

    if contrast_scores:
        average_contrast = (
            sum(contrast_scores)
            / len(contrast_scores)
        )
    else:
        average_contrast = 0

    if brightness_scores:
        average_brightness = (
            sum(brightness_scores)
            / len(brightness_scores)
        )
    else:
        average_brightness = 0

    # --------------------------------------------------
    # Tampering
    # --------------------------------------------------

    tampering_pages = tampering.get(
        "pages",
        []
    )

    tampering_scores = []

    for page in tampering_pages:

        analysis = page.get(
            "analysis",
            {}
        )

        tampering_scores.append(
            float(
                analysis.get(
                    "anomaly_score",
                    0
                )
            )
        )

    if tampering_scores:
        average_tampering = (
            sum(tampering_scores)
            / len(tampering_scores)
        )
    else:
        average_tampering = 0

    # --------------------------------------------------
    # Final feature vector
    # --------------------------------------------------

    return {
        "metadata_score": metadata_score,

        "text_score": text_score,

        "missing_field_count":
            missing_fields,

        "repeated_text_count":
            repeated_text,

        "text_length":
            text_length,

        "average_blur":
            average_blur,

        "average_contrast":
            average_contrast,

        "average_brightness":
            average_brightness,

        "tampering_score":
            average_tampering
    }