from pathlib import Path

import pytesseract

from services.pdf_renderer import render_pdf_pages


# =========================================================
# Tesseract configuration
# =========================================================

TESSERACT_PATH = Path(
    r"C:\Program Files\Tesseract-OCR\tesseract.exe"
)

if TESSERACT_PATH.exists():
    pytesseract.pytesseract.tesseract_cmd = str(
        TESSERACT_PATH
    )


# =========================================================
# OCR single page
# =========================================================

def perform_ocr(page):
    """
    Run Tesseract OCR on a single PIL image.
    """

    if page is None:
        return {
            "text": "",
            "confidence": 0
        }

    try:

        # OCR text
        text = pytesseract.image_to_string(
            page,
            config="--psm 6"
        )

        text = text.strip()

        # OCR confidence
        data = pytesseract.image_to_data(
            page,
            output_type=pytesseract.Output.DICT,
            config="--psm 6"
        )

        confidences = []

        for confidence in data.get(
            "conf",
            []
        ):

            try:
                value = float(confidence)

                if value >= 0:
                    confidences.append(value)

            except (
                ValueError,
                TypeError
            ):
                continue

        average_confidence = 0

        if confidences:
            average_confidence = (
                sum(confidences)
                / len(confidences)
            )

        return {
            "text": text,
            "confidence": round(
                average_confidence,
                2
            )
        }

    except Exception as exc:

        return {
            "text": "",
            "confidence": 0,
            "error": str(exc)
        }


# =========================================================
# OCR complete PDF
# =========================================================

def perform_pdf_ocr(file_path: str):
    """
    Render all PDF pages and perform OCR.
    """

    pdf_path = Path(file_path)

    if not pdf_path.exists():

        return {
            "text": "",
            "confidence": 0,
            "pages_processed": 0,
            "error": (
                f"PDF file not found: "
                f"{pdf_path.resolve()}"
            )
        }

    if not TESSERACT_PATH.exists():

        return {
            "text": "",
            "confidence": 0,
            "pages_processed": 0,
            "error": (
                "Tesseract executable not found at: "
                f"{TESSERACT_PATH}"
            )
        }

    try:

        pages = render_pdf_pages(
            str(pdf_path.resolve())
        )

    except Exception as exc:

        return {
            "text": "",
            "confidence": 0,
            "pages_processed": 0,
            "error": (
                f"PDF rendering failed: {exc}"
            )
        }

    all_text = []
    all_confidences = []

    for page_number, page in enumerate(
        pages,
        start=1
    ):

        result = perform_ocr(page)

        page_text = result.get(
            "text",
            ""
        )

        page_confidence = result.get(
            "confidence",
            0
        )

        if page_text:

            all_text.append(
                f"[Page {page_number}]\n"
                f"{page_text}"
            )

        if page_confidence > 0:

            all_confidences.append(
                page_confidence
            )

    average_confidence = 0

    if all_confidences:

        average_confidence = (
            sum(all_confidences)
            / len(all_confidences)
        )

    return {
        "text": "\n\n".join(
            all_text
        ),
        "confidence": round(
            average_confidence,
            2
        ),
        "pages_processed": len(pages)
    }