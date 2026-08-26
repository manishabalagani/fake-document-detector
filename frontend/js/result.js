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