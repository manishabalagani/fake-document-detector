const express = require("express");

const authMiddleware = require("../middleware/authMiddleware");

const {
    analyze,
    getAnalysis
} = require("../controllers/analysisController");

const router = express.Router();

router.post(
    "/:documentId",
    authMiddleware,
    analyze
);

router.get(
    "/:documentId",
    authMiddleware,
    getAnalysis
);

module.exports = router;