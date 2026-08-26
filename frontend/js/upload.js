const documentFile = document.getElementById("documentFile");
const uploadArea = document.getElementById("uploadArea");

const fileInfo = document.getElementById("fileInfo");
const fileName = document.getElementById("fileName");
const fileSize = document.getElementById("fileSize");

const removeFile = document.getElementById("removeFile");
const analyzeButton = document.getElementById("analyzeButton");

const uploadError = document.getElementById("uploadError");

const MAX_FILE_SIZE = 10 * 1024 * 1024;

const allowedTypes = [
    "application/pdf",
    "image/jpeg",
    "image/png"
];


function showError(message) {

    uploadError.textContent = message;

}


function clearError() {

    uploadError.textContent = "";

}


function formatFileSize(bytes) {

    if (bytes === 0) {
        return "0 Bytes";
    }

    if (bytes < 1024) {
        return bytes + " Bytes";
    }

    if (bytes < 1024 * 1024) {
        return (bytes / 1024).toFixed(2) + " KB";
    }

    return (bytes / (1024 * 1024)).toFixed(2) + " MB";
}


function handleFile(file) {

    clearError();

    if (!file) {
        return;
    }
    if (file.size === 0) {

    showError(
        "This file appears to be empty (0 bytes). Please select the actual document file."
    );

    analyzeButton.disabled = true;

    return;
}


    // Check file type
    if (!allowedTypes.includes(file.type)) {

        showError(
            "Unsupported file type. Please upload PDF, JPG, JPEG, or PNG."
        );

        return;
    }


    // Check file size
    if (file.size > MAX_FILE_SIZE) {

        showError(
            "File is too large. Maximum allowed size is 10 MB."
        );

        return;
    }


    // Display file information
    fileName.textContent = file.name;

    fileSize.textContent = formatFileSize(file.size);

    fileInfo.classList.remove("hidden");

    analyzeButton.disabled = false;

    console.log("File selected:", file.name);
}


documentFile.addEventListener("change", function () {

    const file = documentFile.files[0];

    handleFile(file);

});


removeFile.addEventListener("click", function () {

    documentFile.value = "";

    fileInfo.classList.add("hidden");

    analyzeButton.disabled = true;

    clearError();

});


analyzeButton.addEventListener("click", function () {

    clearError();

    if (!documentFile.files[0]) {

        showError("Please select a document first.");

        return;
    }

    const file = documentFile.files[0];

    console.log("Ready to analyze:", file.name);

    // Save selected filename temporarily
    sessionStorage.setItem(
        "selectedDocument",
        file.name
    );

    // Go to result page
    window.location.href = "result.html";

});
analyzeButton.addEventListener("click", async function () {

    try {

        analyzeButton.textContent = "Analyzing...";
        analyzeButton.disabled = true;

        // Call backend
        const result = await analyzeDocument(selectedFile);

        console.log("Backend result:", result);

        // Save result temporarily
        localStorage.setItem(
            "analysisResult",
            JSON.stringify(result)
        );

        // Go to result page
        window.location.href = "result.html";

    } catch (error) {

        console.error(error);

        uploadError.textContent =
            "Unable to analyze the document. Please try again.";

        analyzeButton.textContent =
            "Analyze Document";

        analyzeButton.disabled = false;
    }
});