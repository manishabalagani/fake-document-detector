from PIL import Image

from services.ocr_analyzer import perform_ocr


image = Image.open(
    "test_documents/test_ocr.png"
)


result = perform_ocr(image)


print("\n===== OCR TEST =====")

print("Confidence:",
      result["confidence"])

print("\nExtracted Text:")

print(result["text"])