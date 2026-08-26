import cv2
import numpy as np


def calculate_noise_map(gray):
    """
    Estimate local noise by comparing an image
    with a smoothed version.
    """

    blurred = cv2.GaussianBlur(
        gray,
        (5, 5),
        0
    )

    noise = cv2.absdiff(
        gray,
        blurred
    )

    return noise


def calculate_local_noise_variation(gray):
    """
    Measure how different noise levels are
    across image regions.
    """

    noise_map = calculate_noise_map(gray)

    height, width = gray.shape

    grid_rows = 4
    grid_cols = 4

    region_values = []

    for row in range(grid_rows):

        for col in range(grid_cols):

            y1 = row * height // grid_rows
            y2 = (row + 1) * height // grid_rows

            x1 = col * width // grid_cols
            x2 = (col + 1) * width // grid_cols

            region = noise_map[
                y1:y2,
                x1:x2
            ]

            if region.size == 0:
                continue

            region_values.append(
                float(np.mean(region))
            )

    if not region_values:
        return {
            "mean": 0,
            "variation": 0
        }

    return {
        "mean": float(
            np.mean(region_values)
        ),
        "variation": float(
            np.std(region_values)
        )
    }


def calculate_edge_variation(gray):
    """
    Analyze edge density across image regions.
    """

    edges = cv2.Canny(
        gray,
        100,
        200
    )

    height, width = gray.shape

    grid_rows = 4
    grid_cols = 4

    edge_values = []

    for row in range(grid_rows):

        for col in range(grid_cols):

            y1 = row * height // grid_rows
            y2 = (row + 1) * height // grid_rows

            x1 = col * width // grid_cols
            x2 = (col + 1) * width // grid_cols

            region = edges[
                y1:y2,
                x1:x2
            ]

            if region.size == 0:
                continue

            edge_density = (
                np.count_nonzero(region)
                / region.size
            )

            edge_values.append(
                float(edge_density)
            )

    if not edge_values:
        return {
            "mean": 0,
            "variation": 0
        }

    return {
        "mean": float(
            np.mean(edge_values)
        ),
        "variation": float(
            np.std(edge_values)
        )
    }


def analyze_tampering(image):
    """
    Produce image-forensics indicators.

    These indicators are NOT proof of manipulation.
    """

    if image is None:
        raise ValueError(
            "Invalid image"
        )

    image_array = np.array(image)

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

    noise_result = (
        calculate_local_noise_variation(
            gray
        )
    )

    edge_result = (
        calculate_edge_variation(
            gray
        )
    )

    def calculate_anomaly_score(
        noise_variation,
        edge_variation
    ):
        """
        Convert regional variation into an
        anomaly score.

        This is a heuristic feature, not a
        probability of fraud.
        """

        noise_component = min(
            noise_variation * 20,
            50
        )

        edge_component = min(
            edge_variation * 100,
            50
        )

        score = (
            noise_component
            + edge_component
        )

        return round(
            min(score, 100),
            2
        )

    anomaly_score = calculate_anomaly_score(
        noise_result["variation"],
        edge_result["variation"]
    )

    return {
        "anomaly_score": anomaly_score,

        "noise_analysis": {
            "mean": round(
                noise_result["mean"],
                4
            ),
            "variation": round(
                noise_result["variation"],
                4
            )
        },

        "edge_analysis": {
            "mean": round(
                edge_result["mean"],
                4
            ),
            "variation": round(
                edge_result["variation"],
                4
            )
        }
    }