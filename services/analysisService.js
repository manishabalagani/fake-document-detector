const analyzeDocument = async (document) => {

    // Temporary result.
    // Later this will be replaced with the
    // actual fake-document detection model.

    return {
        result: "suspicious",
        confidence: 50,
        reason: "Document analysis module is not connected yet."
    };
};

module.exports = {
    analyzeDocument
};