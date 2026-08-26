const express = require("express");
const cors = require("cors");
const path = require("path");
require("dotenv").config();

const { connectDB, sequelize } = require("./config/db");

// Load models and relationships
require("./models");

const authRoutes = require("./routes/authRoutes");
const documentRoutes = require("./routes/documentRoutes");
const analysisRoutes = require("./routes/analysisRoutes");

const app = express();
app.use(cors());
app.use(express.json());

// -------------------------
// Middleware
// -------------------------

app.use(cors());

app.use(express.json());

app.use(express.urlencoded({
    extended: true
}));


// -------------------------
// Static uploads folder
// -------------------------

app.use(
    "/uploads",
    express.static(path.join(__dirname, "uploads"))
);


// -------------------------
// API Routes
// -------------------------

app.use(
    "/api/auth",
    authRoutes
);

app.use(
    "/api/documents",
    documentRoutes
);

app.use(
    "/api/analysis",
    analysisRoutes
);


// -------------------------
// Home route
// -------------------------

app.get("/", (req, res) => {
    res.json({
        success: true,
        message: "Fake Document Detector Backend is running"
    });
});


// -------------------------
// Start server
// -------------------------

const PORT = process.env.PORT || 3000;

const startServer = async () => {
    try {

        await connectDB();

        // Create/update tables during development.
        await sequelize.sync();

        console.log("PostgreSQL tables synchronized");

        app.listen(PORT, "0.0.0.0", () => {
    console.log(`Server running on port ${PORT}`);
});

    } catch (error) {

        console.error(
            "Server startup failed:",
            error.message
        );

        process.exit(1);
    }
};

startServer();