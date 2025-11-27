const express = require("express");
const mongoose = require("mongoose");
const cors = require("cors");
require("dotenv").config();

const app = express();
const PORT = process.env.PORT || 5000;

const connectDB = async () => {
  try {
    await mongoose.connect(process.env.MONGODB_URI, {
      useNewUrlParser: true,
      useUnifiedTopology: true,
    });
    console.log("MongoDB connected successfully");
  } catch (err) {
    console.error("MongoDB connection error:", err);
    throw err;
  }
};

const setupMiddleware = (app) => {
  app.use(cors());
  app.use(express.json());
};
const setupRoutes = (app) => {
  const scenarioRoutes = require("./routes/scenarios");
  app.use("/api/scenarios", scenarioRoutes);

  app.get("/api/health", (req, res) => {
    res.json({
      status: "OK",
      message: "Attack Scenarios Backend is running",
      timestamp: new Date().toISOString(),
    });
  });
};

const setupErrorHandling = (app) => {
  app.use((err, req, res, next) => {
    console.error(err.stack);
    res.status(500).json({
      error: "Something went wrong!",
      message:
        process.env.NODE_ENV === "development"
          ? err.message
          : "Internal server error",
    });
  });

  app.use("*", (req, res) => {
    res.status(404).json({ error: "Route not found" });
  });
};

const startServer = async () => {
  try {
    await connectDB();
    setupMiddleware(app);
    setupRoutes(app);
    setupErrorHandling(app);
    app.listen(PORT, () => {
      console.log(`Server running on port ${PORT}`);
      console.log(`Environment: ${process.env.NODE_ENV || "development"}`);
    });
  } catch (err) {
    console.error("Failed to start server:", err);
    process.exit(1);
  }
};

startServer();
