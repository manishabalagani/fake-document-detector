import cv2
import numpy as np


def analyze_image(image):
    """
    Analyze basic visual characteristics of a document image.
    """

    if image is None:
        raise ValueError("Invalid image")

    # Convert PIL image to NumPy array
    image_array = np.array(image)

    # Handle RGB/RGBA images
    if len(image_array.shape) == 3:

        if image_array.shape[2] == 4:
            image_array = cv2.cvtColor(
                image_array,
                cv2.COLOR_RGBA2RGB
            )

        gray = cv2.cvtColor(
            image_array,
            cv2.COLOR_RGB2GRAY
        )

    else:
        gray = image_array

    height, width = gray.shape

    # -----------------------------
    # Brightness
    # -----------------------------

    brightness = float(
        np.mean(gray)
    )

    # -----------------------------
    # Contrast
    # -----------------------------

    contrast = float(
        np.std(gray)
    )

    # -----------------------------
    # Blur detection
    # -----------------------------

    blur_score = float(
        cv2.Laplacian(
            gray,
            cv2.CV_64F
        ).var()
    )

    # -----------------------------
    # Edge density
    # -----------------------------

    edges = cv2.Canny(
        gray,
        100,
        200
    )

    edge_pixels = np.count_nonzero(edges)

    total_pixels = edges.size

    edge_density = (
        edge_pixels / total_pixels
        if total_pixels > 0
        else 0
    )

    # -----------------------------
    # Noise estimation
    # -----------------------------

    noise = float(
        np.std(
            gray.astype(np.float32)
            - cv2.GaussianBlur(
                gray,
                (5, 5),
                0
            ).astype(np.float32)
        )
    )

    return {
        "width": width,
        "height": height,
        "brightness": round(
            brightness,
            2
        ),
        "contrast": round(
            contrast,
            2
        ),
        "blur_score": round(
            blur_score,
            2
        ),
        "edge_density": round(
            edge_density,
            5
        ),
        "noise_level": round(
            noise,
            2
        )
    }
from services.pdf_renderer import render_pdf_pages


def analyze_pdf_images(
    file_path: str
):

    pages = render_pdf_pages(
        file_path
    )

    results = []

    for page_number, page in enumerate(
        pages,
        start=1
    ):

        analysis = analyze_image(
            page
        )

        results.append({
            "page": page_number,
            "analysis": analysis
        })

    return {
        "pages": results,
        "page_count": len(pages)
    }