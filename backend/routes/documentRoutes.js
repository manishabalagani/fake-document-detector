const express = require("express");

const authMiddleware = require("../middleware/authMiddleware");
const upload = require("../middleware/uploadMiddleware");

const {
    uploadDocument,
    getMyDocuments
} = require("../controllers/documentController");

const router = express.Router();

router.post(
    "/upload",
    authMiddleware,
    upload.single("document"),
    uploadDocument
);

router.get(
    "/my-documents",
    authMiddleware,
    getMyDocuments
);

module.exports = router;