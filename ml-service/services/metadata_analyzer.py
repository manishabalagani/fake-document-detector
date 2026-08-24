from datetime import datetime


def analyze_metadata(metadata, page_count):
    """
    Analyze PDF metadata and return structured metadata features.
    """

    if metadata is None:
        metadata = {}

    title = metadata.get("/Title")
    author = metadata.get("/Author")
    creator = metadata.get("/Creator")
    producer = metadata.get("/Producer")
    creation_date = metadata.get("/CreationDate")
    modification_date = metadata.get("/ModDate")

    findings = []
    score = 0

    # Check metadata completeness
    available_fields = [
        title,
        author,
        creator,
        producer,
        creation_date,
        modification_date
    ]

    available_count = sum(
        1 for field in available_fields
        if field
    )

    if available_count == 0:
        findings.append(
            "No useful PDF metadata was found"
        )
        score += 10

    # Check creator/producer information
    if not creator:
        findings.append(
            "PDF creator information is missing"
        )
        score += 5

    if not producer:
        findings.append(
            "PDF producer information is missing"
        )
        score += 5

    # Check page count
    if page_count <= 0:
        findings.append(
            "Invalid page count detected"
        )
        score += 20

    # Parse dates
    creation = parse_pdf_date(creation_date)
    modification = parse_pdf_date(modification_date)

    if creation and modification:

        if modification < creation:
            findings.append(
                "Modification date appears earlier than creation date"
            )
            score += 25

    return {
        "score": min(score, 100),
        "metadata": {
            "title": title,
            "author": author,
            "creator": creator,
            "producer": producer,
            "creation_date": creation_date,
            "modification_date": modification_date,
            "page_count": page_count
        },
        "findings": findings
    }


def parse_pdf_date(value):
    """
    Convert a PDF date string into a Python datetime.
    """

    if not value:
        return None

    if not isinstance(value, str):
        value = str(value)

    value = value.replace("D:", "")

    try:
        return datetime.strptime(
            value[:14],
            "%Y%m%d%H%M%S"
        )

    except ValueError:
        return None