import re
from datetime import datetime


# ============================================================
# DOCUMENT RULES
# ============================================================

DOCUMENT_RULES = {
    "certificate": {
        "required_fields": [
            "name",
            "course",
            "issue_date",
            "certificate_number",
        ]
    },

    "invoice": {
        "required_fields": [
            "invoice_number",
            "date",
            "seller",
            "buyer",
            "total",
        ]
    },

    "marksheet": {
        "required_fields": [
            "name",
            "roll_number",
            "institution",
            "total",
        ]
    },

    "allotment_order": {
        "required_fields": [
            "name",
            "hall_ticket_no",
            "college",
            "course",
            "printed_date",
        ]
    },
}


# ============================================================
# DOCUMENT TYPE DETECTION
# ============================================================

def detect_document_type(text: str):

    text_lower = text.lower()

    # --------------------------------------------------------
    # Allotment order
    # --------------------------------------------------------

    allotment_keywords = [
        "provisional allotment order",
        "allotment order",
        "allotment of seat",
        "self-reporting",
        "appolycet",
        "polycet.ap.gov.in",
        "hall ticket no",
        "candidate's name",
    ]

    allotment_matches = sum(
        keyword in text_lower
        for keyword in allotment_keywords
    )

    if allotment_matches >= 2:
        return "allotment_order"

    # --------------------------------------------------------
    # Certificate
    # --------------------------------------------------------

    if (
        "certificate" in text_lower
        and (
            "certify that" in text_lower
            or "certificate no" in text_lower
            or "certificate number" in text_lower
        )
    ):
        return "certificate"

    # --------------------------------------------------------
    # Invoice
    # --------------------------------------------------------

    if (
        "invoice" in text_lower
        or "tax invoice" in text_lower
    ):
        return "invoice"

    # --------------------------------------------------------
    # Marksheet
    # --------------------------------------------------------

    if (
        "marksheet" in text_lower
        or "mark sheet" in text_lower
        or "statement of marks" in text_lower
    ):
        return "marksheet"

    return "unknown"


# ============================================================
# TEXT NORMALIZATION
# ============================================================

def normalize_text(text: str):

    if not text:
        return ""

    # Replace non-breaking spaces
    text = text.replace("\xa0", " ")

    # Normalize unusual whitespace
    text = text.replace("\r\n", "\n")
    text = text.replace("\r", "\n")

    # Normalize tabs
    text = re.sub(r"[ \t]+", " ", text)

    # Fix common PDF extraction problems
    text = re.sub(
        r"(?i)\bWG\s*in\b",
        "WG in",
        text
    )

    # Example:
    # "WGin COMPUTER"
    # becomes:
    # "WG in COMPUTER"

    # Normalize repeated newlines
    text = re.sub(
        r"\n{3,}",
        "\n\n",
        text
    )

    return text.strip()


# ============================================================
# BASIC KEY-VALUE EXTRACTION
# ============================================================

def extract_key_value_fields(text: str):

    fields = {}

    for line in text.splitlines():

        line = line.strip()

        if not line:
            continue

        # Ignore URLs
        if line.lower().startswith("http"):
            continue

        # Ignore obvious footer/browser timestamp lines
        if re.match(
            r"^\d{1,2}/\d{1,2}/\d{2,4}",
            line
        ):
            continue

        match = re.match(
            r"^([^:]{2,80}):\s*(.+)$",
            line
        )

        if not match:
            continue

        key = match.group(1).strip().lower()
        value = match.group(2).strip()

        if not value:
            continue

        # Normalize key
        key = re.sub(
            r"\s+",
            "_",
            key
        )

        fields[key] = value

    return fields


# ============================================================
# ALLOTMENT ORDER FIELD EXTRACTION
# ============================================================

def extract_allotment_fields(text: str):

    fields = {}

    # Normalize first
    text = normalize_text(text)

    # --------------------------------------------------------
    # Candidate name
    #
    # Example:
    #
    # Candidate's Name: GUBBALA ROHAN SRINIVASU
    # Father's Name : GUBBALA SRINIVAS
    # --------------------------------------------------------

    match = re.search(
        r"Candidate['’]s\s+Name\s*:\s*"
        r"(.+?)"
        r"\s+Father['’]s\s+Name",
        text,
        re.IGNORECASE | re.DOTALL,
    )

    if match:

        name = match.group(1).strip()

        # Remove accidental trailing spaces
        name = re.sub(
            r"\s+",
            " ",
            name
        )

        fields["name"] = name

    # --------------------------------------------------------
    # Hall ticket number
    # --------------------------------------------------------

    match = re.search(
        r"Hall\s+Ticket\s+No\s*:\s*"
        r"([A-Za-z0-9/-]+)",
        text,
        re.IGNORECASE,
    )

    if match:
        fields["hall_ticket_no"] = (
            match.group(1).strip()
        )

    # --------------------------------------------------------
    # Rank
    # --------------------------------------------------------

    match = re.search(
        r"\bRank\s*:\s*([0-9]+)",
        text,
        re.IGNORECASE,
    )

    if match:
        fields["rank"] = (
            match.group(1).strip()
        )

    # --------------------------------------------------------
    # Father's name
    # --------------------------------------------------------

    match = re.search(
        r"Father['’]s\s+Name\s*:\s*"
        r"(.+?)"
        r"\s+Gender/Region",
        text,
        re.IGNORECASE | re.DOTALL,
    )

    if match:

        father_name = match.group(1).strip()

        father_name = re.sub(
            r"\s+",
            " ",
            father_name
        )

        fields["father_name"] = father_name

    # --------------------------------------------------------
    # Gender / Region
    # --------------------------------------------------------

    match = re.search(
        r"Gender/Region\s*:\s*"
        r"(.+?)"
        r"\s+Caste/",
        text,
        re.IGNORECASE | re.DOTALL,
    )

    if match:

        fields["gender_region"] = (
            match.group(1).strip()
        )

    # --------------------------------------------------------
    # Caste / Fee reimbursement
    # --------------------------------------------------------

    match = re.search(
        r"Caste/\s*Fee\s+Reimb\s*:\s*"
        r"(.+?)"
        r"(?=\s*P\s*R\s*O\s*V\s*I\s*S\s*I\s*O\s*N\s*A\s*L)",
        text,
        re.IGNORECASE | re.DOTALL,
    )

    if match:

        caste_value = match.group(1).strip()

        caste_value = re.sub(
            r"\s+",
            " ",
            caste_value
        )

        fields["caste_fee_reimbursement"] = (
            caste_value
        )

    # ========================================================
    # COLLEGE + COURSE
    # ========================================================

    # The important sentence is approximately:
    #
    # "is pleased to allot a seat to the above candidate in
    # SMT. B. SEETHA POLYTECHNIC (SSBV), BHIMAVARAM, WG
    # in COMPUTER SCIENCE AND ENGINEERING (CSE),
    # under BC_B_GEN_AU category."
    #
    # PDF extraction may produce:
    #
    # WG in
    #
    # or:
    #
    # WGin
    #
    # or:
    #
    # WG   in
    # ========================================================

    allotment_pattern = re.search(
        r"allot\s+a\s+seat\s+to\s+the\s+above\s+candidate\s+in\s+"
        r"(.+?)"
        r"\s+WG\s*in\s+"
        r"(.+?)"
        r"\s*,?\s*under\s+"
        r"([A-Z0-9_-]+)\s+category",
        text,
        re.IGNORECASE | re.DOTALL,
    )

    if allotment_pattern:

        college = allotment_pattern.group(1).strip()
        course = allotment_pattern.group(2).strip()
        category = allotment_pattern.group(3).strip()

        # Clean college
        college = re.sub(
            r"\s+",
            " ",
            college
        )

        college = college.rstrip(" ,.")

        # Clean course
        course = re.sub(
            r"\s+",
            " ",
            course
        )

        course = course.rstrip(" ,.")

        fields["college"] = college
        fields["course"] = course
        fields["category"] = category

    # ========================================================
    # FALLBACK COLLEGE + COURSE EXTRACTION
    # ========================================================

    if (
        "college" not in fields
        or "course" not in fields
    ):

        fallback_pattern = re.search(
            r"candidate\s+in\s+"
            r"(.+?)"
            r"\s+(?:WG\s*)?in\s+"
            r"(.+?)"
            r"\s*,?\s*under\s+"
            r"([A-Z0-9_-]+)\s+category",
            text,
            re.IGNORECASE | re.DOTALL,
        )

        if fallback_pattern:

            college = fallback_pattern.group(1).strip()
            course = fallback_pattern.group(2).strip()
            category = fallback_pattern.group(3).strip()

            college = re.sub(
                r"\s+",
                " ",
                college
            ).rstrip(" ,.")

            course = re.sub(
                r"\s+",
                " ",
                course
            ).rstrip(" ,.")

            fields["college"] = college
            fields["course"] = course
            fields["category"] = category

    # ========================================================
    # SECOND COURSE FALLBACK
    # ========================================================

    if "course" not in fields:

        match = re.search(
            r"\bin\s+"
            r"([A-Za-z][A-Za-z0-9 &()./-]{3,120}?)"
            r"\s*,?\s*under\s+"
            r"[A-Z0-9_-]+\s+category",
            text,
            re.IGNORECASE | re.DOTALL,
        )

        if match:

            course = match.group(1).strip()

            course = re.sub(
                r"\s+",
                " ",
                course
            )

            course = course.rstrip(" ,.")

            fields["course"] = course

    # ========================================================
    # SECOND COLLEGE FALLBACK
    # ========================================================

    if "college" not in fields and "course" in fields:

        course_position = text.lower().find(
            fields["course"].lower()
        )

        if course_position > 0:

            before_course = text[:course_position]

            marker = re.search(
                r"candidate\s+in\s+(.+?)$",
                before_course,
                re.IGNORECASE | re.DOTALL,
            )

            if marker:

                college = marker.group(1).strip()

                college = re.sub(
                    r"\s+",
                    " ",
                    college
                )

                college = college.rstrip(" ,.")

                if len(college) >= 5:

                    fields["college"] = (
                        college
                    )

    # ========================================================
    # CATEGORY
    # ========================================================

    if "category" not in fields:

        match = re.search(
            r"under\s+"
            r"([A-Z0-9_-]+)"
            r"\s+category",
            text,
            re.IGNORECASE,
        )

        if match:

            fields["category"] = (
                match.group(1).strip()
            )

    # ========================================================
    # TUITION FEE
    # ========================================================

    match = re.search(
        r"Tution\s+Fee\s+fixed"
        r".{0,100}?"
        r"Rs\.?\s*"
        r"([0-9,]+)",
        text,
        re.IGNORECASE | re.DOTALL,
    )

    if not match:

        match = re.search(
            r"Tuition\s+Fee\s+fixed"
            r".{0,100}?"
            r"Rs\.?\s*"
            r"([0-9,]+)",
            text,
            re.IGNORECASE | re.DOTALL,
        )

    if match:

        fields["tuition_fee"] = (
            match.group(1)
            .replace(",", "")
        )

    # ========================================================
    # ACTUAL FEE PAID
    # ========================================================

    match = re.search(
        r"Tuition\s+fee\s+to\s+be\s+paid"
        r".{0,100}?"
        r"Rs\.?\s*"
        r"([0-9,]+)",
        text,
        re.IGNORECASE | re.DOTALL,
    )

    if match:

        fields["tuition_fee_paid"] = (
            match.group(1)
            .replace(",", "")
        )

    # ========================================================
    # PRINTED DATE
    # ========================================================

    match = re.search(
        r"Printed\s+as\s+on\s+Dt\s*:\s*"
        r"(\d{1,2}[-/.]\d{1,2}[-/.]\d{4})",
        text,
        re.IGNORECASE,
    )

    if match:

        fields["printed_date"] = (
            match.group(1)
        )

    # ========================================================
    # REPORTING LAST DATE
    # ========================================================

    match = re.search(
        r"last\s+date\s+for\s+Self-reporting"
        r".{0,500}?"
        r"(\d{1,2}[-/.]\d{1,2}[-/.]\d{4})",
        text,
        re.IGNORECASE | re.DOTALL,
    )

    if match:

        fields["reporting_last_date"] = (
            match.group(1)
        )

    # ========================================================
    # PORTAL
    # ========================================================

    urls = re.findall(
        r"https?://[^\s\"<>]+",
        text,
        re.IGNORECASE,
    )

    if urls:

        # Prefer the main domain
        preferred_url = None

        for url in urls:

            if "polycet.ap.gov.in" in url.lower():

                preferred_url = url
                break

        if preferred_url is None:
            preferred_url = urls[0]

        preferred_url = preferred_url.rstrip(
            ".,);"
        )

        # Remove PDF extraction artifacts
        preferred_url = re.sub(
            r"\.\d+$",
            "",
            preferred_url
        )

        fields["portal"] = preferred_url

    return fields


# ============================================================
# GENERAL FIELD EXTRACTION
# ============================================================

def extract_fields(
    text: str,
    document_type: str
):

    fields = extract_key_value_fields(text)

    if document_type == "allotment_order":

        allotment_fields = (
            extract_allotment_fields(text)
        )

        fields.update(
            allotment_fields
        )

    return fields


# ============================================================
# REQUIRED FIELD CHECK
# ============================================================

def check_required_fields(
    fields,
    document_type
):

    rules = DOCUMENT_RULES.get(
        document_type
    )

    if not rules:

        return {
            "missing_fields": [],
            "score": 0,
        }

    required_fields = rules[
        "required_fields"
    ]

    missing_fields = []

    for field in required_fields:

        value = fields.get(field)

        if (
            value is None
            or str(value).strip() == ""
        ):

            missing_fields.append(
                field
            )

    # Each missing field = 20 points
    score = min(
        len(missing_fields) * 20,
        100
    )

    return {
        "missing_fields": missing_fields,
        "score": score,
    }


# ============================================================
# DATE PARSING
# ============================================================

def parse_date(value: str):

    if not value:
        return None

    value = value.strip()

    formats = [
        "%d-%m-%Y",
        "%d/%m/%Y",
        "%d.%m.%Y",
        "%Y-%m-%d",
        "%d %B %Y",
        "%d %b %Y",
    ]

    for date_format in formats:

        try:

            return datetime.strptime(
                value,
                date_format
            )

        except ValueError:
            continue

    return None


# ============================================================
# DATE VALIDATION
# ============================================================

def check_date_fields(fields):

    findings = []
    score = 0

    date_keys = {
        "date",
        "issue_date",
        "printed_date",
        "creation_date",
        "modification_date",
        "reporting_last_date",
    }

    for key, value in fields.items():

        if key not in date_keys:
            continue

        if not isinstance(
            value,
            str
        ):
            continue

        if not value.strip():
            continue

        parsed_date = parse_date(
            value
        )

        if parsed_date is None:

            findings.append(
                f"Invalid date format in '{key}'"
            )

            score += 10

    return {
        "score": min(score, 100),
        "findings": findings,
    }


# ============================================================
# REPEATED TEXT
# ============================================================

def check_repeated_text(text):

    lines = [
        line.strip().lower()
        for line in text.splitlines()
        if line.strip()
    ]

    # Ignore very long PDF paragraphs
    useful_lines = [
        line
        for line in lines
        if len(line) <= 250
    ]

    counts = {}

    for line in useful_lines:

        counts[line] = (
            counts.get(line, 0) + 1
        )

    repeated_lines = [
        line
        for line, count in counts.items()
        if count > 1
    ]

    score = min(
        len(repeated_lines) * 10,
        50
    )

    return {
        "score": score,
        "repeated_lines": repeated_lines,
    }


# ============================================================
# TEXT QUALITY
# ============================================================

def calculate_text_quality_score(text):

    score = 0

    text_length = len(
        text.strip()
    )

    # --------------------------------------------------------
    # Extremely short text
    # --------------------------------------------------------

    if text_length < 50:

        score += 40

    elif text_length < 200:

        score += 20

    # --------------------------------------------------------
    # Replacement characters
    # --------------------------------------------------------

    replacement_count = text.count(
        "\ufffd"
    )

    if replacement_count > 5:

        score += 20

    # --------------------------------------------------------
    # Non-printable characters
    # --------------------------------------------------------

    printable_count = sum(
        1
        for char in text
        if (
            char.isprintable()
            or char in "\n\r\t"
        )
    )

    if text_length > 0:

        printable_ratio = (
            printable_count
            / text_length
        )

        if printable_ratio < 0.90:

            score += 20

    return min(
        score,
        100
    )


# ============================================================
# ALLOTMENT ORDER QUALITY CHECKS
# ============================================================

def check_allotment_quality(
    fields,
    text
):

    findings = []
    score = 0

    # --------------------------------------------------------
    # Name validation
    # --------------------------------------------------------

    name = fields.get("name")

    if name:

        if len(name) < 3:

            findings.append(
                "Candidate name appears unusually short"
            )

            score += 10

        if re.search(
            r"\d",
            name
        ):

            findings.append(
                "Candidate name contains numeric characters"
            )

            score += 10

    # --------------------------------------------------------
    # Hall ticket validation
    # --------------------------------------------------------

    hall_ticket = fields.get(
        "hall_ticket_no"
    )

    if hall_ticket:

        if not re.match(
            r"^[A-Za-z0-9/-]+$",
            hall_ticket
        ):

            findings.append(
                "Hall ticket number has an unusual format"
            )

            score += 10

    # --------------------------------------------------------
    # College validation
    # --------------------------------------------------------

    college = fields.get(
        "college"
    )

    if college:

        if len(college) < 5:

            findings.append(
                "College name appears unusually short"
            )

            score += 10

    # --------------------------------------------------------
    # Course validation
    # --------------------------------------------------------

    course = fields.get(
        "course"
    )

    if course:

        if len(course) < 3:

            findings.append(
                "Course name appears unusually short"
            )

            score += 10

    # --------------------------------------------------------
    # Printed date
    # --------------------------------------------------------

    if "printed_date" in fields:

        parsed = parse_date(
            fields["printed_date"]
        )

        if parsed:

            # Very old/future dates may deserve review.
            current_year = datetime.now().year

            if (
                parsed.year < 2000
                or parsed.year > current_year + 2
            ):

                findings.append(
                    "Printed date appears unusual"
                )

                score += 15

    return {
        "score": min(score, 100),
        "findings": findings,
    }


# ============================================================
# MAIN TEXT ANALYSIS
# ============================================================

def analyze_text(text: str):

    # --------------------------------------------------------
    # Empty document
    # --------------------------------------------------------

    if not text or not text.strip():

        return {
            "score": 100,
            "document_type": "unknown",
            "fields": {},
            "missing_fields": [],
            "repeated_text": [],
            "text_length": 0,
            "findings": [
                "No readable text was found"
            ],
        }

    # --------------------------------------------------------
    # Normalize
    # --------------------------------------------------------

    text = normalize_text(
        text
    )

    # --------------------------------------------------------
    # Detect document
    # --------------------------------------------------------

    document_type = (
        detect_document_type(text)
    )

    # --------------------------------------------------------
    # Extract fields
    # --------------------------------------------------------

    fields = extract_fields(
        text,
        document_type
    )

    # --------------------------------------------------------
    # Required fields
    # --------------------------------------------------------

    required_result = (
        check_required_fields(
            fields,
            document_type
        )
    )

    # --------------------------------------------------------
    # Date validation
    # --------------------------------------------------------

    date_result = (
        check_date_fields(
            fields
        )
    )

    # --------------------------------------------------------
    # Repeated text
    # --------------------------------------------------------

    repeated_result = (
        check_repeated_text(
            text
        )
    )

    # --------------------------------------------------------
    # Text quality
    # --------------------------------------------------------

    quality_score = (
        calculate_text_quality_score(
            text
        )
    )

    # --------------------------------------------------------
    # Document-specific checks
    # --------------------------------------------------------

    document_quality_score = 0
    document_quality_findings = []

    if document_type == "allotment_order":

        allotment_quality = (
            check_allotment_quality(
                fields,
                text
            )
        )

        document_quality_score = (
            allotment_quality["score"]
        )

        document_quality_findings = (
            allotment_quality["findings"]
        )

    # ========================================================
    # WEIGHTED TEXT SCORE
    # ========================================================
    #
    # Missing fields      = 40%
    # Date problems       = 15%
    # Repeated text       = 10%
    # Text quality        = 15%
    # Document checks     = 20%
    #
    # ========================================================

    total_score = (
        required_result["score"] * 0.40
        + date_result["score"] * 0.15
        + repeated_result["score"] * 0.10
        + quality_score * 0.15
        + document_quality_score * 0.20
    )

    total_score = round(
        min(
            max(
                total_score,
                0
            ),
            100
        )
    )

    # ========================================================
    # FINDINGS
    # ========================================================

    findings = []

    # Date findings
    findings.extend(
        date_result["findings"]
    )

    # Missing fields
    if required_result[
        "missing_fields"
    ]:

        findings.append(
            "Missing expected fields: "
            + ", ".join(
                required_result[
                    "missing_fields"
                ]
            )
        )

    # Repeated text
    if repeated_result[
        "repeated_lines"
    ]:

        findings.append(
            "Repeated text detected"
        )

    # Text quality
    if quality_score >= 40:

        findings.append(
            "Low text extraction quality detected"
        )

    # Document-specific findings
    findings.extend(
        document_quality_findings
    )

    # ========================================================
    # RETURN
    # ========================================================

    return {
        "score": total_score,

        "document_type": document_type,

        "fields": fields,

        "missing_fields": (
            required_result[
                "missing_fields"
            ]
        ),

        "repeated_text": (
            repeated_result[
                "repeated_lines"
            ]
        ),

        "text_length": len(text),

        "findings": findings,
    }