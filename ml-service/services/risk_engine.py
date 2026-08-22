# services/risk_engine.py

# ============================================================
# HELPERS
# ============================================================

def clamp(value, minimum=0.0, maximum=100.0):
    """
    Keep a numeric value inside a fixed range.
    """
    try:
        value = float(value)
    except (TypeError, ValueError):
        value = minimum

    return min(
        max(value, minimum),
        maximum
    )


def safe_float(value, default=0.0):
    """
    Safely convert a value to float.
    """
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


# ============================================================
# PAGE AVERAGE
# ============================================================

def calculate_page_average(
    page_results,
    score_key
):
    """
    Calculate the average value of a score across pages.

    Expected structure:

        [
            {
                "page": 1,
                "analysis": {
                    "anomaly_score": 30
                }
            }
        ]
    """

    if not isinstance(page_results, list):
        return 0.0

    scores = []

    for page in page_results:

        if not isinstance(page, dict):
            continue

        analysis = page.get(
            "analysis",
            {}
        )

        if not isinstance(analysis, dict):
            continue

        score = analysis.get(
            score_key
        )

        if isinstance(score, (int, float)):
            scores.append(
                float(score)
            )

    if not scores:
        return 0.0

    return sum(scores) / len(scores)


# ============================================================
# IMAGE QUALITY RISK
# ============================================================

def calculate_image_quality_risk(
    image_analysis
):
    """
    Estimate image-quality risk.

    IMPORTANT:
    This is NOT a fake-document probability.

    Poor image quality can make other analysis
    less reliable, so this is treated as a
    supporting risk signal.

    Current image analyzer uses:

        blur_score = Laplacian variance

    Higher blur_score generally means sharper
    image content.

    Therefore:

        low blur_score  -> higher quality risk
        high blur_score -> lower quality risk
    """

    if not isinstance(image_analysis, dict):
        return 0.0

    pages = image_analysis.get(
        "pages",
        []
    )

    if not isinstance(pages, list) or not pages:
        return 50.0

    page_risks = []

    for page in pages:

        if not isinstance(page, dict):
            continue

        analysis = page.get(
            "analysis",
            {}
        )

        if not isinstance(analysis, dict):
            continue

        blur_score = safe_float(
            analysis.get(
                "blur_score",
                0
            )
        )

        contrast = safe_float(
            analysis.get(
                "contrast",
                0
            )
        )

        brightness = safe_float(
            analysis.get(
                "brightness",
                0
            )
        )

        noise_level = safe_float(
            analysis.get(
                "noise_level",
                0
            )
        )

        # ----------------------------------------------------
        # BLUR RISK
        # ----------------------------------------------------
        #
        # These are deliberately broad because Laplacian
        # variance can vary substantially depending on
        # document resolution and rendering.
        #
        # Very low = likely blurry
        # High = likely sharp
        #

        if blur_score < 20:
            blur_risk = 80

        elif blur_score < 50:
            blur_risk = 60

        elif blur_score < 100:
            blur_risk = 40

        elif blur_score < 300:
            blur_risk = 20

        else:
            blur_risk = 0

        # ----------------------------------------------------
        # CONTRAST RISK
        # ----------------------------------------------------

        if contrast < 10:
            contrast_risk = 70

        elif contrast < 20:
            contrast_risk = 45

        elif contrast < 30:
            contrast_risk = 20

        else:
            contrast_risk = 0

        # ----------------------------------------------------
        # BRIGHTNESS RISK
        # ----------------------------------------------------

        if brightness < 40:
            brightness_risk = 70

        elif brightness < 70:
            brightness_risk = 35

        elif brightness > 250:
            brightness_risk = 70

        elif brightness > 240:
            brightness_risk = 30

        else:
            brightness_risk = 0

        # ----------------------------------------------------
        # NOISE RISK
        # ----------------------------------------------------

        if noise_level > 35:
            noise_risk = 70

        elif noise_level > 25:
            noise_risk = 45

        elif noise_level > 15:
            noise_risk = 20

        else:
            noise_risk = 0

        # ----------------------------------------------------
        # PAGE IMAGE QUALITY RISK
        # ----------------------------------------------------

        page_risk = (
            blur_risk * 0.45
            + contrast_risk * 0.25
            + brightness_risk * 0.15
            + noise_risk * 0.15
        )

        page_risks.append(
            clamp(page_risk)
        )

    if not page_risks:
        return 50.0

    return round(
        sum(page_risks) / len(page_risks),
        2
    )


# ============================================================
# FINAL WEIGHTED RISK SCORE
# ============================================================

def calculate_risk_score(
    metadata_score,
    text_score,
    image_score,
    tampering_score
):
    """
    Calculate final rule-based document risk.

    Weights:

        Metadata   = 20%
        Text       = 25%
        Image      = 15%
        Tampering  = 40%

    All values are expected to be 0-100.
    """

    metadata_score = clamp(
        metadata_score
    )

    text_score = clamp(
        text_score
    )

    image_score = clamp(
        image_score
    )

    tampering_score = clamp(
        tampering_score
    )

    score = (
        metadata_score * 0.20
        + text_score * 0.25
        + image_score * 0.15
        + tampering_score * 0.40
    )

    return round(
        clamp(score),
        2
    )


# ============================================================
# RISK CLASSIFICATION
# ============================================================

def classify_risk(score):
    """
    Convert risk score into a risk level.
    """

    score = clamp(score)

    if score < 30:
        return "LOW"

    elif score < 60:
        return "MEDIUM"

    return "HIGH"


# ============================================================
# TAMPERING SCORE
# ============================================================

def calculate_tampering_score(
    tampering_analysis
):
    """
    Calculate average tampering anomaly score
    across all pages.
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

    return round(
        calculate_page_average(
            pages,
            "anomaly_score"
        ),
        2
    )


# ============================================================
# ANALYSIS CONFIDENCE
# ============================================================

def calculate_analysis_confidence(
    text_analysis,
    ocr_analysis,
    image_analysis
):
    """
    Estimate reliability of the available analysis.

    This is NOT fake-document probability.
    """

    confidence = 100.0

    # --------------------------------------------------------
    # Text quality
    # --------------------------------------------------------

    if not isinstance(
        text_analysis,
        dict
    ):
        confidence -= 25

    else:

        document_type = text_analysis.get(
            "document_type",
            "unknown"
        )

        if document_type == "unknown":
            confidence -= 20

        text_length = safe_float(
            text_analysis.get(
                "text_length",
                0
            )
        )

        if text_length < 20:
            confidence -= 20

        elif text_length < 100:
            confidence -= 10

    # --------------------------------------------------------
    # OCR quality
    # --------------------------------------------------------

    if ocr_analysis:

        if isinstance(
            ocr_analysis,
            dict
        ):

            ocr_confidence = safe_float(
                ocr_analysis.get(
                    "confidence",
                    0
                )
            )

            if ocr_confidence < 50:
                confidence -= 30

            elif ocr_confidence < 70:
                confidence -= 15

    # --------------------------------------------------------
    # Image availability
    # --------------------------------------------------------

    if not isinstance(
        image_analysis,
        dict
    ):

        confidence -= 20

    else:

        image_pages = image_analysis.get(
            "pages",
            []
        )

        if not image_pages:
            confidence -= 20

    return round(
        clamp(confidence),
        2
    )


# ============================================================
# FINDINGS
# ============================================================

def generate_findings(
    metadata_analysis,
    text_analysis,
    image_analysis,
    tampering_analysis
):
    """
    Generate human-readable explanations
    for detected risk indicators.
    """

    findings = []

    # ========================================================
    # METADATA FINDINGS
    # ========================================================

    metadata_findings = metadata_analysis.get(
        "findings",
        []
    )

    if isinstance(
        metadata_findings,
        list
    ):

        for finding in metadata_findings:

            findings.append({
                "category": "metadata",
                "severity": "medium",
                "message": str(finding)
            })

    # ========================================================
    # TEXT FINDINGS
    # ========================================================

    text_findings = text_analysis.get(
        "findings",
        []
    )

    if isinstance(
        text_findings,
        list
    ):

        for finding in text_findings:

            findings.append({
                "category": "text",
                "severity": "medium",
                "message": str(finding)
            })

    # ========================================================
    # MISSING FIELDS
    # ========================================================

    missing_fields = text_analysis.get(
        "missing_fields",
        []
    )

    if isinstance(
        missing_fields,
        list
    ) and missing_fields:

        findings.append({
            "category": "text",
            "severity": "medium",
            "message":
                f"{len(missing_fields)} expected "
                "field(s) are missing."
        })

    # ========================================================
    # REPEATED TEXT
    # ========================================================

    repeated_text = text_analysis.get(
        "repeated_text",
        []
    )

    if isinstance(
        repeated_text,
        list
    ) and repeated_text:

        findings.append({
            "category": "text",
            "severity": "low",
            "message":
                f"{len(repeated_text)} repeated "
                "text pattern(s) detected."
        })

    # ========================================================
    # TAMPERING FINDINGS
    # ========================================================

    tampering_pages = tampering_analysis.get(
        "pages",
        []
    )

    if isinstance(
        tampering_pages,
        list
    ):

        for page in tampering_pages:

            if not isinstance(
                page,
                dict
            ):
                continue

            page_number = page.get(
                "page",
                "unknown"
            )

            analysis = page.get(
                "analysis",
                {}
            )

            if not isinstance(
                analysis,
                dict
            ):
                continue

            anomaly_score = safe_float(
                analysis.get(
                    "anomaly_score",
                    0
                )
            )

            if anomaly_score >= 60:

                findings.append({
                    "category": "tampering",
                    "severity": "high",
                    "message":
                        "Strong visual anomaly "
                        f"detected on page {page_number}."
                })

            elif anomaly_score >= 30:

                findings.append({
                    "category": "tampering",
                    "severity": "medium",
                    "message":
                        "Moderate visual anomaly "
                        f"detected on page {page_number}."
                })

    # ========================================================
    # IMAGE QUALITY FINDINGS
    # ========================================================

    image_pages = image_analysis.get(
        "pages",
        []
    )

    if isinstance(
        image_pages,
        list
    ):

        for page in image_pages:

            if not isinstance(
                page,
                dict
            ):
                continue

            page_number = page.get(
                "page",
                "unknown"
            )

            analysis = page.get(
                "analysis",
                {}
            )

            if not isinstance(
                analysis,
                dict
            ):
                continue

            blur_score = safe_float(
                analysis.get(
                    "blur_score",
                    0
                )
            )

            contrast = safe_float(
                analysis.get(
                    "contrast",
                    0
                )
            )

            brightness = safe_float(
                analysis.get(
                    "brightness",
                    0
                )
            )

            # Very blurry
            if blur_score < 20:

                findings.append({
                    "category": "image_quality",
                    "severity": "high",
                    "message":
                        "Very low image sharpness "
                        f"detected on page {page_number}. "
                        "This may reduce analysis reliability."
                })

            elif blur_score < 50:

                findings.append({
                    "category": "image_quality",
                    "severity": "medium",
                    "message":
                        "Low image sharpness "
                        f"detected on page {page_number}. "
                        "This may reduce analysis reliability."
                })

            # Low contrast
            if contrast < 20:

                findings.append({
                    "category": "image_quality",
                    "severity": "medium",
                    "message":
                        "Low image contrast "
                        f"detected on page {page_number}."
                })

            # Extremely bright/dark
            if brightness < 40 or brightness > 250:

                findings.append({
                    "category": "image_quality",
                    "severity": "medium",
                    "message":
                        "Unusual image brightness "
                        f"detected on page {page_number}."
                })

    return findings


# ============================================================
# MAIN DOCUMENT RISK FUNCTION
# ============================================================

def calculate_document_risk(
    metadata_analysis,
    text_analysis,
    image_analysis,
    tampering_analysis,
    ocr_analysis=None
):
    """
    Main rule-based document risk engine.

    Returns:

        risk_score
        risk_level
        analysis_confidence
        component_scores
        findings
    """

    # ========================================================
    # SAFETY
    # ========================================================

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

    if ocr_analysis is not None:

        if not isinstance(
            ocr_analysis,
            dict
        ):
            ocr_analysis = {}

    # ========================================================
    # METADATA
    # ========================================================

    metadata_score = clamp(
        metadata_analysis.get(
            "score",
            0
        )
    )

    # ========================================================
    # TEXT
    # ========================================================

    text_score = clamp(
        text_analysis.get(
            "score",
            0
        )
    )

    # ========================================================
    # IMAGE
    # ========================================================

    image_score = calculate_image_quality_risk(
        image_analysis
    )

    # ========================================================
    # TAMPERING
    # ========================================================

    tampering_score = calculate_tampering_score(
        tampering_analysis
    )

    # ========================================================
    # FINAL RISK
    # ========================================================

    risk_score = calculate_risk_score(
        metadata_score=metadata_score,
        text_score=text_score,
        image_score=image_score,
        tampering_score=tampering_score
    )

    # ========================================================
    # RISK LEVEL
    # ========================================================

    risk_level = classify_risk(
        risk_score
    )

    # ========================================================
    # CONFIDENCE
    # ========================================================

    analysis_confidence = calculate_analysis_confidence(
        text_analysis=text_analysis,
        ocr_analysis=ocr_analysis,
        image_analysis=image_analysis
    )

    # ========================================================
    # FINDINGS
    # ========================================================

    findings = generate_findings(
        metadata_analysis=metadata_analysis,
        text_analysis=text_analysis,
        image_analysis=image_analysis,
        tampering_analysis=tampering_analysis
    )

    # ========================================================
    # FINAL RESULT
    # ========================================================

    return {

        "risk_score":
            risk_score,

        "risk_level":
            risk_level,

        "analysis_confidence":
            analysis_confidence,

        "component_scores": {

            "metadata":
                round(
                    metadata_score,
                    2
                ),

            "text":
                round(
                    text_score,
                    2
                ),

            "image":
                round(
                    image_score,
                    2
                ),

            "tampering":
                round(
                    tampering_score,
                    2
                )
        },

        "findings":
            findings
    }