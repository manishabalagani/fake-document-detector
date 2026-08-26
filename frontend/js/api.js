// Backend base URL
const API_BASE_URL = "https://fake-document-detector-2.onrender.com/";

// Send document to backend
async function analyzeDocument(file) {

    const formData = new FormData();

    formData.append("file", file);

    const response = await fetch(
        `${API_BASE_URL}/analyze`,
        {
            method: "POST",
            body: formData
        }
    );

    if (!response.ok) {
        throw new Error("Document analysis failed");
    }

    return await response.json();
}