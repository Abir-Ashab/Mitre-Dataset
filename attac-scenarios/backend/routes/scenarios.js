const express = require("express");
const router = express.Router();
const Scenario = require("../models/Scenario");

const sendSuccess = (res, data, message = null, count = null, status = 200) => {
  const response = { success: true, data };
  if (message) response.message = message;
  if (count !== null) response.count = count;
  res.status(status).json(response);
};

const sendError = (res, status, error) => {
  res.status(status).json({ success: false, error });
};

const findScenarioById = async (id) => {
  return await Scenario.findOne({ scenarioId: id });
};

router.get("/", async (req, res) => {
  try {
    const scenarios = await Scenario.find().sort({ createdAt: -1 });
    sendSuccess(res, scenarios, null, scenarios.length);
  } catch (error) {
    console.error("Error fetching scenarios:", error);
    sendError(res, 500, "Failed to fetch scenarios");
  }
});

router.get("/:id", async (req, res) => {
  try {
    const scenario = await findScenarioById(req.params.id);
    if (!scenario) {
      return sendError(res, 404, "Scenario not found");
    }
    sendSuccess(res, scenario);
  } catch (error) {
    console.error("Error fetching scenario:", error);
    sendError(res, 500, "Failed to fetch scenario");
  }
});

router.post("/", async (req, res) => {
  try {
    const { scenarioId, title, description, attackTechniques } = req.body;

    const existingScenario = await findScenarioById(scenarioId);
    if (existingScenario) {
      return sendError(res, 409, "Scenario with this ID already exists");
    }

    const scenario = new Scenario({
      scenarioId,
      title,
      description,
      attackTechniques,
    });

    await scenario.save();

    sendSuccess(res, scenario, "Scenario created successfully", null, 201);
  } catch (error) {
    console.error("Error creating scenario:", error);
    sendError(res, 500, "Failed to create scenario");
  }
});

router.put("/:id/complete", async (req, res) => {
  try {
    const scenario = await findScenarioById(req.params.id);
    if (!scenario) {
      return sendError(res, 404, "Scenario not found");
    }

    scenario.completed = true;
    scenario.completedAt = new Date();
    await scenario.save();

    sendSuccess(res, scenario, "Scenario marked as completed");
  } catch (error) {
    console.error("Error completing scenario:", error);
    sendError(res, 500, "Failed to mark scenario as completed");
  }
});

router.put("/:id/incomplete", async (req, res) => {
  try {
    const scenario = await findScenarioById(req.params.id);
    if (!scenario) {
      return sendError(res, 404, "Scenario not found");
    }

    scenario.completed = false;
    scenario.completedAt = null;
    await scenario.save();

    sendSuccess(res, scenario, "Scenario marked as incomplete");
  } catch (error) {
    console.error("Error marking scenario as incomplete:", error);
    sendError(res, 500, "Failed to mark scenario as incomplete");
  }
});

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
      return sendError(res, 404, "Scenario not found");
    }

    sendSuccess(res, scenario, "Scenario updated successfully");
  } catch (error) {
    console.error("Error updating scenario:", error);
    sendError(res, 500, "Failed to update scenario");
  }
});

router.delete("/:id", async (req, res) => {
  try {
    const scenario = await Scenario.findOneAndDelete({
      scenarioId: req.params.id,
    });
    if (!scenario) {
      return sendError(res, 404, "Scenario not found");
    }

    sendSuccess(res, null, "Scenario deleted successfully");
  } catch (error) {
    console.error("Error deleting scenario:", error);
    sendError(res, 500, "Failed to delete scenario");
  }
});

router.get("/status/completed", async (req, res) => {
  try {
    const scenarios = await Scenario.find({ completed: true }).sort({
      completedAt: -1,
    });
    sendSuccess(res, scenarios, null, scenarios.length);
  } catch (error) {
    console.error("Error fetching completed scenarios:", error);
    sendError(res, 500, "Failed to fetch completed scenarios");
  }
});

router.get("/status/incomplete", async (req, res) => {
  try {
    const scenarios = await Scenario.find({ completed: false }).sort({
      createdAt: -1,
    });
    sendSuccess(res, scenarios, null, scenarios.length);
  } catch (error) {
    console.error("Error fetching incomplete scenarios:", error);
    sendError(res, 500, "Failed to fetch incomplete scenarios");
  }
});

module.exports = router;
