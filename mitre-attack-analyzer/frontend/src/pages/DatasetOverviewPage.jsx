import {
  Database,
  GitBranch,
  Layers,
  TrendingUp,
  CheckCircle,
  ArrowRight,
  Cpu,
  Zap,
} from "lucide-react";

export default function DatasetOverviewPage() {
  const stats = {
    training: 89693,
    validation: 12427,
    totalLogs: 102120,
    chunkSize: 7,
    normalLogs: "~70%",
    suspiciousLogs: "~30%",
  };

  const pipelineSteps = [
    {
      name: "Extract",
      description: "Separate normal and suspicious logs from sessions",
      icon: Database,
      color: "blue",
    },
    {
      name: "Clean",
      description: "Remove duplicate logs and validate data quality",
      icon: CheckCircle,
      color: "green",
    },
    {
      name: "Chunk",
      description: "Group logs into 7-log chunks for optimal training",
      icon: Layers,
      color: "purple",
    },
    {
      name: "Fine-tune",
      description: "Train Qwen2.5-1.5B with LoRA adapters on chunks",
      icon: Cpu,
      color: "orange",
    },
  ];

  const modelInfo = {
    baseModel: "Qwen/Qwen2.5-1.5B-Instruct",
    technique: "LoRA (Low-Rank Adaptation)",
    quantization: "8-bit",
    parameters: "1.5 Billion",
    trainableParams: "~2.4M (LoRA)",
    memoryUsage: "~1.5 GB",
  };

  return (
    <div className="space-y-6">
      {/* Hero Section */}
      <div className="card bg-gradient-to-br from-primary-50 to-blue-50 dark:from-gray-800 dark:to-gray-800 border-primary-200 dark:border-primary-900">
        <div className="flex items-start justify-between">
          <div>
            <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-2">
              MITRE ATT&CK Log Analyzer
            </h1>
            <p className="text-gray-700 dark:text-gray-300 text-lg max-w-3xl">
              Fine-tuned AI model for detecting cybersecurity threats in system
              logs using MITRE ATT&CK framework
            </p>
          </div>
          <Zap className="w-12 h-12 text-primary-600 dark:text-primary-400" />
        </div>
      </div>

      {/* Dataset Statistics */}
      <div className="card">
        <h2 className="text-xl font-bold text-gray-900 dark:text-white mb-4 flex items-center gap-2">
          <Database className="w-6 h-6 text-primary-600 dark:text-primary-400" />
          Dataset Statistics
        </h2>
        <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
          <div className="p-4 bg-blue-50 dark:bg-blue-900/20 rounded-lg border border-blue-200 dark:border-blue-800">
            <p className="text-xs text-blue-700 dark:text-blue-400 mb-1 font-medium">
              Training Examples
            </p>
            <p className="text-3xl font-bold text-blue-900 dark:text-blue-300">
              {stats.training.toLocaleString()}
            </p>
          </div>
          <div className="p-4 bg-green-50 dark:bg-green-900/20 rounded-lg border border-green-200 dark:border-green-800">
            <p className="text-xs text-green-700 dark:text-green-400 mb-1 font-medium">
              Validation Examples
            </p>
            <p className="text-3xl font-bold text-green-900 dark:text-green-300">
              {stats.validation.toLocaleString()}
            </p>
          </div>
          <div className="p-4 bg-purple-50 dark:bg-purple-900/20 rounded-lg border border-purple-200 dark:border-purple-800">
            <p className="text-xs text-purple-700 dark:text-purple-400 mb-1 font-medium">
              Total Log Chunks
            </p>
            <p className="text-3xl font-bold text-purple-900 dark:text-purple-300">
              {stats.totalLogs.toLocaleString()}
            </p>
          </div>
          <div className="p-4 bg-orange-50 dark:bg-orange-900/20 rounded-lg border border-orange-200 dark:border-orange-800">
            <p className="text-xs text-orange-700 dark:text-orange-400 mb-1 font-medium">
              Chunk Size
            </p>
            <p className="text-3xl font-bold text-orange-900 dark:text-orange-300">
              {stats.chunkSize} logs
            </p>
          </div>
          <div className="p-4 bg-green-50 dark:bg-green-900/20 rounded-lg border border-green-200 dark:border-green-800">
            <p className="text-xs text-green-700 dark:text-green-400 mb-1 font-medium">
              Normal Logs
            </p>
            <p className="text-3xl font-bold text-green-900 dark:text-green-300">
              {stats.normalLogs}
            </p>
          </div>
          <div className="p-4 bg-red-50 dark:bg-red-900/20 rounded-lg border border-red-200 dark:border-red-800">
            <p className="text-xs text-red-700 dark:text-red-400 mb-1 font-medium">
              Suspicious Logs
            </p>
            <p className="text-3xl font-bold text-red-900 dark:text-red-300">
              {stats.suspiciousLogs}
            </p>
          </div>
        </div>
      </div>

      {/* Data Pipeline */}
      <div className="card">
        <h2 className="text-xl font-bold text-gray-900 dark:text-white mb-4 flex items-center gap-2">
          <GitBranch className="w-6 h-6 text-primary-600 dark:text-primary-400" />
          Data Preparation Pipeline
        </h2>
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          {pipelineSteps.map((step, index) => (
            <div key={step.name} className="relative">
              <div
                className={`p-4 bg-${step.color}-50 dark:bg-${step.color}-900/20 rounded-lg border border-${step.color}-200 dark:border-${step.color}-800 h-full`}
              >
                <div className="flex items-center gap-2 mb-2">
                  <step.icon
                    className={`w-5 h-5 text-${step.color}-600 dark:text-${step.color}-400`}
                  />
                  <h3
                    className={`font-bold text-${step.color}-900 dark:text-${step.color}-300`}
                  >
                    {index + 1}. {step.name}
                  </h3>
                </div>
                <p
                  className={`text-xs text-${step.color}-800 dark:text-${step.color}-400`}
                >
                  {step.description}
                </p>
              </div>
              {index < pipelineSteps.length - 1 && (
                <ArrowRight className="hidden md:block absolute top-1/2 -right-6 transform -translate-y-1/2 w-4 h-4 text-gray-400 dark:text-gray-600" />
              )}
            </div>
          ))}
        </div>
      </div>

      {/* Model Information */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="card">
          <h2 className="text-xl font-bold text-gray-900 dark:text-white mb-4 flex items-center gap-2">
            <Cpu className="w-6 h-6 text-primary-600 dark:text-primary-400" />
            Model Architecture
          </h2>
          <div className="space-y-3">
            <div className="flex justify-between items-center p-3 bg-gray-50 dark:bg-gray-800/50 rounded-lg">
              <span className="text-sm text-gray-700 dark:text-gray-300 font-medium">
                Base Model
              </span>
              <span className="text-sm text-gray-900 dark:text-white font-mono">
                {modelInfo.baseModel}
              </span>
            </div>
            <div className="flex justify-between items-center p-3 bg-gray-50 dark:bg-gray-800/50 rounded-lg">
              <span className="text-sm text-gray-700 dark:text-gray-300 font-medium">
                Fine-tuning Technique
              </span>
              <span className="text-sm text-gray-900 dark:text-white font-semibold">
                {modelInfo.technique}
              </span>
            </div>
            <div className="flex justify-between items-center p-3 bg-gray-50 dark:bg-gray-800/50 rounded-lg">
              <span className="text-sm text-gray-700 dark:text-gray-300 font-medium">
                Quantization
              </span>
              <span className="text-sm text-gray-900 dark:text-white">
                {modelInfo.quantization}
              </span>
            </div>
            <div className="flex justify-between items-center p-3 bg-gray-50 dark:bg-gray-800/50 rounded-lg">
              <span className="text-sm text-gray-700 dark:text-gray-300 font-medium">
                Total Parameters
              </span>
              <span className="text-sm text-gray-900 dark:text-white">
                {modelInfo.parameters}
              </span>
            </div>
            <div className="flex justify-between items-center p-3 bg-gray-50 dark:bg-gray-800/50 rounded-lg">
              <span className="text-sm text-gray-700 dark:text-gray-300 font-medium">
                Trainable Parameters
              </span>
              <span className="text-sm text-primary-600 dark:text-primary-400 font-semibold">
                {modelInfo.trainableParams}
              </span>
            </div>
            <div className="flex justify-between items-center p-3 bg-gray-50 dark:bg-gray-800/50 rounded-lg">
              <span className="text-sm text-gray-700 dark:text-gray-300 font-medium">
                Memory Usage
              </span>
              <span className="text-sm text-green-600 dark:text-green-400 font-semibold">
                {modelInfo.memoryUsage}
              </span>
            </div>
          </div>
        </div>

        <div className="card">
          <h2 className="text-xl font-bold text-gray-900 dark:text-white mb-4 flex items-center gap-2">
            <TrendingUp className="w-6 h-6 text-primary-600 dark:text-primary-400" />
            Key Features
          </h2>
          <div className="space-y-4">
            <div className="flex items-start gap-3">
              <CheckCircle className="w-5 h-5 text-green-600 dark:text-green-400 flex-shrink-0 mt-0.5" />
              <div>
                <h3 className="font-semibold text-gray-900 dark:text-white text-sm mb-1">
                  MITRE ATT&CK Detection
                </h3>
                <p className="text-xs text-gray-600 dark:text-gray-400">
                  Automatically identifies attack techniques using the MITRE
                  ATT&CK framework taxonomy
                </p>
              </div>
            </div>
            <div className="flex items-start gap-3">
              <CheckCircle className="w-5 h-5 text-green-600 dark:text-green-400 flex-shrink-0 mt-0.5" />
              <div>
                <h3 className="font-semibold text-gray-900 dark:text-white text-sm mb-1">
                  Efficient Chunking
                </h3>
                <p className="text-xs text-gray-600 dark:text-gray-400">
                  7-log chunks optimized for ~2,200 tokens, staying within model
                  limits while maximizing context
                </p>
              </div>
            </div>
            <div className="flex items-start gap-3">
              <CheckCircle className="w-5 h-5 text-green-600 dark:text-green-400 flex-shrink-0 mt-0.5" />
              <div>
                <h3 className="font-semibold text-gray-900 dark:text-white text-sm mb-1">
                  Low Memory Footprint
                </h3>
                <p className="text-xs text-gray-600 dark:text-gray-400">
                  8-bit quantization reduces memory from 3GB to 1.5GB, enabling
                  deployment on consumer hardware
                </p>
              </div>
            </div>
            <div className="flex items-start gap-3">
              <CheckCircle className="w-5 h-5 text-green-600 dark:text-green-400 flex-shrink-0 mt-0.5" />
              <div>
                <h3 className="font-semibold text-gray-900 dark:text-white text-sm mb-1">
                  Real-time Analysis
                </h3>
                <p className="text-xs text-gray-600 dark:text-gray-400">
                  Fast inference with cached sessions stored locally using
                  IndexedDB
                </p>
              </div>
            </div>
            <div className="flex items-start gap-3">
              <CheckCircle className="w-5 h-5 text-green-600 dark:text-green-400 flex-shrink-0 mt-0.5" />
              <div>
                <h3 className="font-semibold text-gray-900 dark:text-white text-sm mb-1">
                  Balanced Dataset
                </h3>
                <p className="text-xs text-gray-600 dark:text-gray-400">
                  70% normal logs ensure the model doesn't generate false
                  positives
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Technical Details */}
      <div className="card bg-gray-50 dark:bg-gray-800/50">
        <h2 className="text-xl font-bold text-gray-900 dark:text-white mb-3">
          How It Works
        </h2>
        <div className="space-y-3 text-sm text-gray-700 dark:text-gray-300">
          <p>
            <strong className="text-gray-900 dark:text-white">
              Data Collection:
            </strong>{" "}
            System logs are collected from both normal operations and simulated
            attack scenarios covering various MITRE ATT&CK techniques.
          </p>
          <p>
            <strong className="text-gray-900 dark:text-white">
              Preprocessing:
            </strong>{" "}
            Logs are extracted, deduplicated, and chunked into 7-log segments.
            Each chunk is timestamped and labeled (Normal or Suspicious with
            MITRE techniques).
          </p>
          <p>
            <strong className="text-gray-900 dark:text-white">
              Fine-tuning:
            </strong>{" "}
            The Qwen2.5-1.5B-Instruct model is fine-tuned using LoRA (Low-Rank
            Adaptation) on 89,693 training examples, with 8-bit quantization for
            efficiency.
          </p>
          <p>
            <strong className="text-gray-900 dark:text-white">
              Inference:
            </strong>{" "}
            The model analyzes log chunks and outputs: Status
            (Normal/Suspicious), MITRE ATT&CK techniques if detected, and
            reasoning for the classification.
          </p>
        </div>
      </div>
    </div>
  );
}
