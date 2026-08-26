from services.document_analyzer import analyze_pdf


pdf_path = "test_documents/sample.pdf"

result = analyze_pdf(pdf_path)

print("\n===== DOCUMENT ANALYSIS =====")

print("File Name:", result["file_name"])
print("File Type:", result["file_type"])
print("File Size:", result["file_size"])
print("Page Count:", result["page_count"])

print("\n===== METADATA =====")

for key, value in result["metadata"].items():
    print(f"{key}: {value}")

print("\n===== TEXT =====")

print(result["text"])