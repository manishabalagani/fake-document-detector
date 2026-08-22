from pathlib import Path

from pypdf import PdfReader

from services.metadata_analyzer import (
    analyze_metadata
)

from services.text_analyzer import (
    analyze_text
)

from services.ocr_analyzer import (
    perform_pdf_ocr
)

from services.image_analyzer import (
    analyze_pdf_images
)

from services.pdf_renderer import (
    render_pdf_pages
)

from services.tampering_analyzer import (
    analyze_tampering
)

from services.ml_analysis import (
    run_ml_analysis
)

from services.risk_engine import (
    calculate_document_risk
)


# ============================================================
# SAFE DICTIONARY
# ============================================================

def safe_dict(value):
    """
    Ensure an analyzer result is a dictionary.
    """

    if isinstance(value, dict):
        return value

    return {}


# ============================================================
# MAIN PDF ANALYSIS
# ============================================================

def analyze_pdf(
    file_path: str
):
    """
    Complete PDF document analysis pipeline.

    Pipeline:

        PDF
         ↓
        Metadata
         ↓
        Text extraction
         ↓
        OCR fallback
         ↓
        Text analysis
         ↓
        Image analysis
         ↓
        PDF rendering
         ↓
        Tampering analysis
         ↓
        ML analysis
         ↓
        Risk analysis
         ↓
        Final result
    """

    # ========================================================
    # 1. Validate file
    # ========================================================

    path = Path(
        file_path
    )

    if not path.exists():

        raise FileNotFoundError(
            f"PDF file not found: {path}"
        )

    if not path.is_file():

        raise ValueError(
            "Provided path is not a file"
        )

    if path.suffix.lower() != ".pdf":

        raise ValueError(
            "File must be a PDF"
        )

    # ========================================================
    # 2. Read PDF
    # ========================================================

    reader = PdfReader(
        str(path)
    )

    page_count = len(
        reader.pages
    )

    # ========================================================
    # 3. Extract metadata
    # ========================================================

    metadata = reader.metadata

    # ========================================================
    # 4. Extract normal PDF text
    # ========================================================

    text_parts = []

    for page in reader.pages:

        try:

            page_text = page.extract_text()

        except Exception:

            page_text = ""

        if page_text:

            text_parts.append(
                page_text
            )

    text = "\n".join(
        text_parts
    ).strip()

    # ========================================================
    # 5. OCR fallback
    # ========================================================

    ocr_result = None

    if len(text.strip()) < 20:

        try:

            ocr_result = perform_pdf_ocr(
                str(path)
            )

            ocr_result = safe_dict(
                ocr_result
            )

            ocr_text = ocr_result.get(
                "text",
                ""
            )

            if isinstance(
                ocr_text,
                str
            ) and ocr_text.strip():

                text = ocr_text.strip()

        except Exception as exc:

            ocr_result = {

                "text": "",

                "confidence": 0,

                "error": str(exc)
            }

    # ========================================================
    # 6. Metadata analysis
    # ========================================================

    try:

        metadata_result = analyze_metadata(
            metadata,
            page_count
        )

        metadata_result = safe_dict(
            metadata_result
        )

    except Exception as exc:

        metadata_result = {

            "score": 0,

            "metadata": {},

            "findings": [],

            "error": str(exc)
        }

    # ========================================================
    # 7. Text analysis
    # ========================================================

    try:

        text_result = analyze_text(
            text
        )

        text_result = safe_dict(
            text_result
        )

    except Exception as exc:

        text_result = {

            "score": 100,

            "document_type": "unknown",

            "fields": {},

            "missing_fields": [],

            "repeated_text": [],

            "text_length": len(text),

            "findings": [
                "Text analysis failed"
            ],

            "error": str(exc)
        }

    # ========================================================
    # 8. Image analysis
    # ========================================================

    try:

        image_result = analyze_pdf_images(
            str(path)
        )

        image_result = safe_dict(
            image_result
        )

    except Exception as exc:

        image_result = {

            "pages": [],

            "error": str(exc)
        }

    # ========================================================
    # 9. Render PDF pages
    # ========================================================

    rendered_pages = []

    try:

        rendered_pages = render_pdf_pages(
            str(path)
        )

        if not isinstance(
            rendered_pages,
            list
        ):

            rendered_pages = []

    except Exception as exc:

        print(
            f"PDF rendering failed: {exc}"
        )

        rendered_pages = []

    # ========================================================
    # 10. Tampering analysis
    # ========================================================

    tampering_results = []

    for page_number, page_image in enumerate(
        rendered_pages,
        start=1
    ):

        try:

            result = analyze_tampering(
                page_image
            )

            result = safe_dict(
                result
            )

            tampering_results.append({

                "page": page_number,

                "analysis": result
            })

        except Exception as exc:

            tampering_results.append({

                "page": page_number,

                "analysis": {

                    "anomaly_score": 0,

                    "error": str(exc)
                }
            })

    tampering_result = {

        "pages": tampering_results
    }

    # ========================================================
    # 11. Machine Learning analysis
    # ========================================================

    try:

        ml_result = run_ml_analysis(
    metadata_analysis=metadata_result,
    text_analysis=text_result,
    image_analysis=image_result,
    tampering_analysis=tampering_result
)

        

    except Exception as exc:

        ml_result = {

            "features": {},

            "prediction": {

                "prediction":
                    "UNAVAILABLE",

                "genuine_probability":
                    0.0,

                "suspicious_probability":
                    0.0
            },

            "error": str(exc)
        }

    # ========================================================
    # 12. Rule-based risk analysis
    # ========================================================

    try:

        risk_result = calculate_document_risk(

            metadata_analysis=
                metadata_result,

            text_analysis=
                text_result,

            image_analysis=
                image_result,

            tampering_analysis=
                tampering_result,

            ocr_analysis=
                ocr_result
        )

        risk_result = safe_dict(
            risk_result
        )

    except Exception as exc:

        risk_result = {

            "risk_score": 0,

            "risk_level": "UNKNOWN",

            "analysis_confidence": 0,

            "component_scores": {

                "metadata": 0,

                "text": 0,

                "image": 0,

                "tampering": 0
            },

            "findings": [

                {

                    "category":
                        "system",

                    "severity":
                        "high",

                    "message":
                        "Risk analysis failed."
                }

            ],

            "error": str(exc)
        }

    # ========================================================
    # 13. Final result
    # ========================================================

    return {

        "file_name":
            path.name,

        "file_type":
            "PDF",

        "file_size":
            path.stat().st_size,

        "page_count":
            page_count,

        "metadata_analysis":
            metadata_result,

        "text_analysis":
            text_result,

        "ocr_analysis":
            ocr_result,

        "text":
            text,

        "image_analysis":
            image_result,

        "tampering_analysis":
            tampering_result,

        "ml_analysis":
            ml_result,

        "risk_analysis":
            risk_result
    }