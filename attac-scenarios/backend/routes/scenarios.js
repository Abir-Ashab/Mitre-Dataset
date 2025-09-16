const express = require("express");
const router = express.Router();
const Scenario = require("../models/Scenario");

// GET all scenarios
router.get("/", async (req, res) => {
  try {
    const scenarios = await Scenario.find().sort({ createdAt: -1 });
    res.json({
      success: true,
      count: scenarios.length,
      data: scenarios,
    });
  } catch (error) {
    console.error("Error fetching scenarios:", error);
    res.status(500).json({
      success: false,
      error: "Failed to fetch scenarios",
    });
  }
});

// GET a specific scenario by ID
router.get("/:id", async (req, res) => {
  try {
    const scenario = await Scenario.findOne({ scenarioId: req.params.id });
    if (!scenario) {
      return res.status(404).json({
        success: false,
        error: "Scenario not found",
      });
    }
    res.json({
      success: true,
      data: scenario,
    });
  } catch (error) {
    console.error("Error fetching scenario:", error);
    res.status(500).json({
      success: false,
      error: "Failed to fetch scenario",
    });
  }
});

// POST create a new scenario
router.post("/", async (req, res) => {
  try {
    const { scenarioId, title, description, attackTechniques } = req.body;

    // Check if scenario already exists
    const existingScenario = await Scenario.findOne({ scenarioId });
    if (existingScenario) {
      return res.status(409).json({
        success: false,
        error: "Scenario with this ID already exists",
      });
    }

    const scenario = new Scenario({
      scenarioId,
      title,
      description,
      attackTechniques,
    });

    await scenario.save();

    res.status(201).json({
      success: true,
      message: "Scenario created successfully",
      data: scenario,
    });
  } catch (error) {
    console.error("Error creating scenario:", error);
    res.status(500).json({
      success: false,
      error: "Failed to create scenario",
    });
  }
});

// PUT mark scenario as completed
router.put("/:id/complete", async (req, res) => {
  try {
    const scenario = await Scenario.findOne({ scenarioId: req.params.id });
    if (!scenario) {
      return res.status(404).json({
        success: false,
        error: "Scenario not found",
      });
    }

    scenario.completed = true;
    scenario.completedAt = new Date();
    await scenario.save();

    res.json({
      success: true,
      message: "Scenario marked as completed",
      data: scenario,
    });
  } catch (error) {
    console.error("Error completing scenario:", error);
    res.status(500).json({
      success: false,
      error: "Failed to mark scenario as completed",
    });
  }
});

// PUT mark scenario as incomplete
router.put("/:id/incomplete", async (req, res) => {
  try {
    const scenario = await Scenario.findOne({ scenarioId: req.params.id });
    if (!scenario) {
      return res.status(404).json({
        success: false,
        error: "Scenario not found",
      });
    }

    scenario.completed = false;
    scenario.completedAt = null;
    await scenario.save();

    res.json({
      success: true,
      message: "Scenario marked as incomplete",
      data: scenario,
    });
  } catch (error) {
    console.error("Error marking scenario as incomplete:", error);
    res.status(500).json({
      success: false,
      error: "Failed to mark scenario as incomplete",
    });
  }
});

// PUT update scenario
router.put("/:id", async (req, res) => {
  try {
    const { title, description, attackTechniques } = req.body;

    const scenario = await Scenario.findOneAndUpdate(
      { scenarioId: req.params.id },
      {
        title,
        description,
        attackTechniques,
        updatedAt: new Date(),
      },
      { new: true, runValidators: true }
    );

    if (!scenario) {
      return res.status(404).json({
        success: false,
        error: "Scenario not found",
      });
    }

    res.json({
      success: true,
      message: "Scenario updated successfully",
      data: scenario,
    });
  } catch (error) {
    console.error("Error updating scenario:", error);
    res.status(500).json({
      success: false,
      error: "Failed to update scenario",
    });
  }
});

// DELETE a scenario
router.delete("/:id", async (req, res) => {
  try {
    const scenario = await Scenario.findOneAndDelete({
      scenarioId: req.params.id,
    });
    if (!scenario) {
      return res.status(404).json({
        success: false,
        error: "Scenario not found",
      });
    }

    res.json({
      success: true,
      message: "Scenario deleted successfully",
    });
  } catch (error) {
    console.error("Error deleting scenario:", error);
    res.status(500).json({
      success: false,
      error: "Failed to delete scenario",
    });
  }
});

// GET completed scenarios
router.get("/status/completed", async (req, res) => {
  try {
    const scenarios = await Scenario.find({ completed: true }).sort({
      completedAt: -1,
    });
    res.json({
      success: true,
      count: scenarios.length,
      data: scenarios,
    });
  } catch (error) {
    console.error("Error fetching completed scenarios:", error);
    res.status(500).json({
      success: false,
      error: "Failed to fetch completed scenarios",
    });
  }
});

// GET incomplete scenarios
router.get("/status/incomplete", async (req, res) => {
  try {
    const scenarios = await Scenario.find({ completed: false }).sort({
      createdAt: -1,
    });
    res.json({
      success: true,
      count: scenarios.length,
      data: scenarios,
    });
  } catch (error) {
    console.error("Error fetching incomplete scenarios:", error);
    res.status(500).json({
      success: false,
      error: "Failed to fetch incomplete scenarios",
    });
  }
});

module.exports = router;
