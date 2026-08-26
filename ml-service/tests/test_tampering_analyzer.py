from PIL import Image

from services.tampering_analyzer import (
    analyze_tampering
)


image = Image.open(
    "test_documents/test_ocr.png"
)

result = analyze_tampering(
    image
)

print("\n===== TAMPERING ANALYSIS =====")

print("\nNoise Analysis:")

for key, value in result[
    "noise_analysis"
].items():

    print(f"{key}: {value}")


print("\nEdge Analysis:")

for key, value in result[
    "edge_analysis"
].items():

    print(f"{key}: {value}")