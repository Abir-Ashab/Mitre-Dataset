const mongoose = require("mongoose");

const scenarioSchema = new mongoose.Schema({
  scenarioId: {
    type: String,
    required: true,
    unique: true,
    trim: true,
  },
  title: {
    type: String,
    required: true,
    trim: true,
  },
  description: {
    type: String,
    trim: true,
  },
  attackTechniques: [
    {
      techniqueId: String,
      techniqueName: String,
      tactic: String,
    },
  ],
  completed: {
    type: Boolean,
    default: false,
  },
  completedAt: {
    type: Date,
    default: null,
  },
  createdAt: {
    type: Date,
    default: Date.now,
  },
  updatedAt: {
    type: Date,
    default: Date.now,
  },
});

scenarioSchema.pre("save", function (next) {
  this.updatedAt = new Date();
  if (this.completed && !this.completedAt) {
    this.completedAt = new Date();
  }
  next();
});

module.exports = mongoose.model("Scenario", scenarioSchema);
