from services.metadata_analyzer import analyze_metadata


metadata = {
    "/Title": "Test Certificate",
    "/Author": "Test User",
    "/Creator": "Microsoft Word",
    "/Producer": "Microsoft Word",
    "/CreationDate": "D:20250809100000",
    "/ModDate": "D:20250809110000"
}


result = analyze_metadata(
    metadata,
    page_count=1
)


print("\n===== METADATA TEST =====")

print("Score:", result["score"])

print("\nMetadata:")

for key, value in result["metadata"].items():
    print(f"{key}: {value}")

print("\nFindings:")

for finding in result["findings"]:
    print("-", finding)