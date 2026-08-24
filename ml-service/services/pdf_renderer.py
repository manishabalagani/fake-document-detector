from pathlib import Path

from pdf2image import convert_from_path


# =========================================================
# Poppler configuration
# =========================================================

POPPLER_PATH = r"C:\poppler-26.02.0\Library\bin"


# =========================================================
# Render PDF pages
# =========================================================

def render_pdf_pages(
    file_path: str,
    dpi: int = 200
):
    """
    Convert every PDF page into a PIL image.
    """

    pdf_path = Path(file_path).expanduser()

    if not pdf_path.is_absolute():
        pdf_path = Path.cwd() / pdf_path

    pdf_path = pdf_path.resolve()

    # -----------------------------------------------------
    # Validate PDF
    # -----------------------------------------------------

    if not pdf_path.exists():
        raise FileNotFoundError(
            f"PDF file not found: {pdf_path}"
        )

    if not pdf_path.is_file():
        raise ValueError(
            f"Path is not a file: {pdf_path}"
        )

    if pdf_path.suffix.lower() != ".pdf":
        raise ValueError(
            f"Expected PDF file, got: "
            f"{pdf_path.suffix}"
        )

    if pdf_path.stat().st_size == 0:
        raise ValueError(
            f"PDF file is empty: {pdf_path}"
        )

    # -----------------------------------------------------
    # Validate Poppler
    # -----------------------------------------------------

    poppler_path = Path(POPPLER_PATH)

    if not poppler_path.exists():
        raise FileNotFoundError(
            f"Poppler directory not found: "
            f"{POPPLER_PATH}"
        )

    pdfinfo = (
        poppler_path / "pdfinfo.exe"
    )

    pdftoppm = (
        poppler_path / "pdftoppm.exe"
    )

    if not pdfinfo.exists():
        raise FileNotFoundError(
            f"pdfinfo.exe not found: "
            f"{pdfinfo}"
        )

    if not pdftoppm.exists():
        raise FileNotFoundError(
            f"pdftoppm.exe not found: "
            f"{pdftoppm}"
        )

    # -----------------------------------------------------
    # Render
    # -----------------------------------------------------

    try:

        pages = convert_from_path(
            str(pdf_path),
            dpi=dpi,
            fmt="png",
            poppler_path=str(
                poppler_path
            ),
            thread_count=1
        )

    except Exception as exc:

        raise RuntimeError(
            "Failed to render PDF. "
            f"PDF: {pdf_path}. "
            f"Poppler: {POPPLER_PATH}. "
            f"Original error: {exc}"
        ) from exc

    # -----------------------------------------------------
    # Verify result
    # -----------------------------------------------------

    if not pages:
        raise RuntimeError(
            f"No pages were rendered from "
            f"{pdf_path}"
        )

    return pages