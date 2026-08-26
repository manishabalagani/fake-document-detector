const fs = require("fs/promises");
const path = require("path");

const analyzeDocument = async (document) => {
    const serviceUrl = process.env.ML_SERVICE_URL;
    if (!serviceUrl) {
        throw new Error("ML_SERVICE_URL is not configured.");
    }
    if (path.extname(document.originalName).toLowerCase() !== ".pdf") {
        throw new Error("ML analysis currently supports PDF documents only.");
    }

    const file = await fs.readFile(document.filePath);
    const form = new FormData();
    form.append(
        "document",
        new Blob([file], { type: document.fileType || "application/pdf" }),
        document.originalName
    );

    const response = await fetch(`${serviceUrl}/analyze`, {
        method: "POST",
        body: form,
        signal: AbortSignal.timeout(120000)
    });
    const payload = await response.json().catch(() => ({}));
    if (!response.ok) {
        throw new Error(payload.detail || "The ML service could not analyze this document.");
    }

    const prediction = payload.ml_analysis?.prediction || {};
    const isSuspicious = prediction.prediction === "SUSPICIOUS";
    const confidence = isSuspicious
        ? prediction.suspicious_probability
        : prediction.genuine_probability;

    return {
        result: isSuspicious ? "suspicious" : "genuine",
        confidence: Math.round(Number(confidence || 0) * 100),
        reason: `ML prediction: ${prediction.prediction || "UNAVAILABLE"}. Risk level: ${payload.risk_analysis?.risk_level || "UNKNOWN"}.`
    };
};

module.exports = {
    analyzeDocument
};
