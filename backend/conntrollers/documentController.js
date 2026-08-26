const { Document } = require("../models");

const uploadDocument = async (req, res) => {
    try {
        if (!req.file) {
            return res.status(400).json({
                success: false,
                message: "Please upload a document"
            });
        }

        const document = await Document.create({
            userId: req.user.id,
            originalName: req.file.originalname,
            fileName: req.file.filename,
            filePath: req.file.path,
            fileType: req.file.mimetype,
            status: "uploaded"
        });

        res.status(201).json({
            success: true,
            message: "Document uploaded successfully",
            document
        });

    } catch (error) {
        console.error("Document upload error:", error);

        res.status(500).json({
            success: false,
            message: "Document upload failed"
        });
    }
};


const getMyDocuments = async (req, res) => {
    try {
        const documents = await Document.findAll({
            where: {
                userId: req.user.id
            },
            order: [
                ["createdAt", "DESC"]
            ]
        });

        res.json({
            success: true,
            documents
        });

    } catch (error) {
        console.error("Get documents error:", error);

        res.status(500).json({
            success: false,
            message: "Unable to fetch documents"
        });
    }
};


module.exports = {
    uploadDocument,
    getMyDocuments
};