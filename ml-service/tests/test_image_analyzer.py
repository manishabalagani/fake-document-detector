from PIL import Image

from services.image_analyzer import analyze_image


image = Image.open(
    "test_documents/test_ocr.png"
)


result = analyze_image(image)


print("\n===== IMAGE ANALYSIS =====")

for key, value in result.items():

    print(f"{key}: {value}")