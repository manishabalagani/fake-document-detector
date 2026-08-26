from services.text_analyzer import analyze_text


text = """
CERTIFICATE OF COMPLETION

Name: Test User
Course: Python Programming
Issue Date: 09 August 2026
Certificate Number: TEST-001
"""


result = analyze_text(text)


print("\n===== TEXT ANALYSIS =====")

print("Score:", result["score"])

print("Document Type:", result["document_type"])

print("\nFields:")

for key, value in result["fields"].items():
    print(f"{key}: {value}")

print("\nMissing Fields:")
print(result["missing_fields"])

print("\nFindings:")

for finding in result["findings"]:
    print("-", finding)