const { Document, Analysis } = require("../models");
const { analyzeDocument } = require("../services/analysisService");

const analyze = async (req, res) => {
    try {
        const { documentId } = req.params;

        const document = await Document.findOne({
            where: {
                id: documentId,
                userId: req.user.id
            }
        });

        if (!document) {
            return res.status(404).json({
                success: false,
                message: "Document not found"
            });
        }

        await document.update({
            status: "processing"
        });

        const result = await analyzeDocument(document);

        const analysis = await Analysis.create({
            documentId: document.id,
            result: result.result,
            confidence: result.confidence,
            reason: result.reason
        });

        await document.update({
            status: "completed"
        });

        res.status(201).json({
            success: true,
            message: "Document analysis completed",
            analysis
        });

    } catch (error) {
        console.error("Analysis error:", error);

        res.status(500).json({
            success: false,
            message: "Document analysis failed"
        });
    }
};


const getAnalysis = async (req, res) => {
    try {
        const { documentId } = req.params;

        const document = await Document.findOne({
            where: {
                id: documentId,
                userId: req.user.id
            }
        });

        if (!document) {
            return res.status(404).json({
                success: false,
                message: "Document not found"
            });
        }

        const analysis = await Analysis.findOne({
            where: {
                documentId
            }
        });

        if (!analysis) {
            return res.status(404).json({
                success: false,
                message: "Analysis not found"
            });
        }

        res.json({
            success: true,
            analysis
        });

    } catch (error) {
        console.error("Get analysis error:", error);

        res.status(500).json({
            success: false,
            message: "Unable to get analysis"
        });
    }
};


module.exports = {
    analyze,
    getAnalysis
};