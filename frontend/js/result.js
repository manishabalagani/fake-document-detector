const resultFileName =
    document.getElementById("resultFileName");

const selectedDocument =
    sessionStorage.getItem("selectedDocument");

if (selectedDocument) {

    resultFileName.textContent = selectedDocument;

} else {

    resultFileName.textContent = "Unknown document";

}

console.log(
    "Result page loaded for:",
    selectedDocument
);
// =========================
// GET BACKEND RESULT
// =========================

const savedResult =
    localStorage.getItem("analysisResult");

if (savedResult) {

    const result = JSON.parse(savedResult);

    console.log(
        "Backend result:",
        result
    );

    // Example:
    // document.getElementById("riskScore").textContent =
    //     result.risk_score + "%";

} else {

    console.log(
        "No backend result found."
    );

}  