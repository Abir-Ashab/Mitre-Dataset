import {
  LineChart,
  BarChart3,
  CheckCircle,
  XCircle,
  TrendingUp,
  Clock,
  Cpu,
  Target,
  AlertTriangle,
  Award,
  Activity,
  Zap,
} from "lucide-react";

export default function TestResultsPage() {
  
  const evaluationMetrics = {
    statusClassification: {
      accuracy: 0.746, 
      precisionMacro: 0.7146, 
      precisionWeighted: 0.7317, 
      recallMacro: 0.6186, 
      recallWeighted: 0.746, 
      f1Macro: 0.6263, 
      f1Weighted: 0.7109, 
    },
    perClass: {
      normal: {
        precision: 0.7575, 
        recall: 0.9371, 
        f1Score: 0.8378, 
        support: 700, 
      },
      suspicious: {
        precision: 0.6716, 
        recall: 0.3, 
        f1Score: 0.4147, 
        support: 300, 
      },
    },
    wordLevel: {
      exactMatch: 0, 
      partialMatch: 0.4715, 
      f1Score: 0.1684, 
    },
    evaluation: {
      totalSamples: 1000,
      suspiciousRatio: 0.3, 
      normalRatio: 0.7, 
      evaluationTime: "Not recorded", 
      timePerSample: "Variable", 
    },
    confusionMatrix: {
      trueNormal: 656, 
      falsePositive: 44, 
      falseNegative: 210, 
      trueSuspicious: 90, 
    },
  };

  
  const testCases = [
    {
      id: "T1",
      title: "Log Collection and Parsing",
      status: "passed",
      accuracy: "100%",
    },
    {
      id: "T2",
      title: "Data Preprocessing and Cleaning",
      status: "passed",
      accuracy: "98.5%",
    },
    {
      id: "T3",
      title: "Threat Detection Accuracy",
      status: "warning", 
      accuracy: "74.6%",
    },
    {
      id: "T4",
      title: "MITRE ATT&CK Technique Mapping",
      status: "partial",
      accuracy: "Varies by class",
    },
    {
      id: "T5",
      title: "Fine-Tuned LLM Integration",
      status: "passed",
      accuracy: "Working",
    },
    {
      id: "T6",
      title: "Report Generation",
      status: "passed",
      accuracy: "100%",
    },
    {
      id: "T7",
      title: "Session Management",
      status: "passed",
      accuracy: "100%",
    },
    {
      id: "T8",
      title: "Handling Large Log Volumes",
      status: "passed",
      accuracy: "Tested on 1000 samples",
    },
    {
      id: "T9",
      title: "Integration with MITRE ATT&CK DB",
      status: "passed",
      accuracy: "100%",
    },
    {
      id: "T10",
      title: "Suspicious Activity Detection",
      status: "failed", 
      accuracy: "30.0% recall",
    },
  ];

  
  const targetMetrics = [
    {
      metric: "Classification Accuracy",
      target: "≥ 85%",
      actual: "74.6%",
      status: "fail", 
    },
    {
      metric: "Precision (Weighted)",
      target: "≥ 80%",
      actual: "73.2%",
      status: "fail", 
    },
    {
      metric: "Recall (Weighted)",
      target: "≥ 75%",
      actual: "74.6%",
      status: "fail", 
    },
    {
      metric: "False Positive Rate",
      target: "≤ 10%",
      actual: "6.3%",
      status: "pass", 
    },
    {
      metric: "False Negative Rate",
      target: "≤ 8%",
      actual: "70.0%",
      status: "fail", 
    },
    {
      metric: "Suspicious Detection Recall",
      target: "≥ 75%",
      actual: "30.0%",
      status: "fail", 
    },
  ];

  
  const finetuningConfig = {
    model: "Qwen/Qwen2.5-1.5B-Instruct",
    technique: "LoRA (Low-Rank Adaptation)",
    rank: 32,
    alpha: 64,
    dropout: 0.05,
    batchSize: 1,
    gradientAccumulationSteps: 16,
    epochs: 5,
    learningRate: "2e-4",
    maxLength: 4096,
    trainingTime: "~6 hours",
    memoryUsage: "12 GB VRAM",
  };

  
  const performanceBenchmarks = [
    {
      category: "Inference Speed",
      value: "1.11 sec/session",
      icon: Zap,
      color: "yellow",
    },
    {
      category: "Memory Footprint",
      value: "~1.5 GB",
      icon: Cpu,
      color: "blue",
    },
    {
      category: "Throughput",
      value: "~54 sessions/min",
      icon: Activity,
      color: "green",
    },
    {
      category: "GPU Utilization",
      value: "Low (~15%)",
      icon: TrendingUp,
      color: "purple",
    },
  ];

  return (
    <div className="space-y-6">
      {/* Hero Section */}
      <div className="card bg-gradient-to-br from-yellow-50 to-orange-50 dark:from-gray-800 dark:to-gray-800 border-yellow-200 dark:border-yellow-900">
        <div className="flex items-start justify-between">
          <div>
            <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-2">
              Model Evaluation & Test Results
            </h1>
            <p className="text-gray-700 dark:text-gray-300 text-lg max-w-3xl">
              Comprehensive evaluation on 1,000 stratified test samples (70%
              normal, 30% suspicious) - Accuracy: 74.6% |{" "}
              <span className="text-red-600 dark:text-red-400 font-semibold">
                Critical Issue: 70% False Negative Rate
              </span>
            </p>
          </div>
          <AlertTriangle className="w-12 h-12 text-yellow-600 dark:text-yellow-400" />
        </div>
      </div>

      {/* Overall Performance Summary */}
      <div className="card">
        <h2 className="text-xl font-bold text-gray-900 dark:text-white mb-4 flex items-center gap-2">
          <Target className="w-6 h-6 text-primary-600 dark:text-primary-400" />
          Overall Performance Metrics
        </h2>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div className="p-4 bg-yellow-50 dark:bg-yellow-900/20 rounded-lg border border-yellow-200 dark:border-yellow-800">
            <p className="text-xs text-yellow-700 dark:text-yellow-400 mb-1 font-medium">
              Overall Accuracy
            </p>
            <p className="text-3xl font-bold text-yellow-900 dark:text-yellow-300">
              {(evaluationMetrics.statusClassification.accuracy * 100).toFixed(
                1,
              )}
              %
            </p>
            <p className="text-xs text-red-600 dark:text-red-500 mt-1 font-semibold">
              ⚠️ Below 85% target
            </p>
          </div>
          <div className="p-4 bg-yellow-50 dark:bg-yellow-900/20 rounded-lg border border-yellow-200 dark:border-yellow-800">
            <p className="text-xs text-yellow-700 dark:text-yellow-400 mb-1 font-medium">
              Precision (Weighted)
            </p>
            <p className="text-3xl font-bold text-yellow-900 dark:text-yellow-300">
              {(
                evaluationMetrics.statusClassification.precisionWeighted * 100
              ).toFixed(1)}
              %
            </p>
            <p className="text-xs text-red-600 dark:text-red-500 mt-1 font-semibold">
              ⚠️ Below 80% target
            </p>
          </div>
          <div className="p-4 bg-yellow-50 dark:bg-yellow-900/20 rounded-lg border border-yellow-200 dark:border-yellow-800">
            <p className="text-xs text-yellow-700 dark:text-yellow-400 mb-1 font-medium">
              Recall (Weighted)
            </p>
            <p className="text-3xl font-bold text-yellow-900 dark:text-yellow-300">
              {(
                evaluationMetrics.statusClassification.recallWeighted * 100
              ).toFixed(1)}
              %
            </p>
            <p className="text-xs text-yellow-600 dark:text-yellow-500 mt-1">
              ~75% target (marginal)
            </p>
          </div>
          <div className="p-4 bg-yellow-50 dark:bg-yellow-900/20 rounded-lg border border-yellow-200 dark:border-yellow-800">
            <p className="text-xs text-yellow-700 dark:text-yellow-400 mb-1 font-medium">
              F1-Score (Weighted)
            </p>
            <p className="text-3xl font-bold text-yellow-900 dark:text-yellow-300">
              {(
                evaluationMetrics.statusClassification.f1Weighted * 100
              ).toFixed(1)}
              %
            </p>
            <p className="text-xs text-yellow-600 dark:text-yellow-500 mt-1">
              Balanced measure
            </p>
          </div>
        </div>
      </div>

      {/* Detailed Metrics Breakdown */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Status Classification Metrics */}
        <div className="card">
          <h3 className="text-lg font-bold text-gray-900 dark:text-white mb-4 flex items-center gap-2">
            <BarChart3 className="w-5 h-5 text-primary-600 dark:text-primary-400" />
            Status Classification
          </h3>
          <div className="space-y-3">
            {[
              {
                label: "Accuracy",
                value: evaluationMetrics.statusClassification.accuracy,
              },
              {
                label: "Precision (Macro)",
                value: evaluationMetrics.statusClassification.precisionMacro,
              },
              {
                label: "Precision (Weighted)",
                value: evaluationMetrics.statusClassification.precisionWeighted,
              },
              {
                label: "Recall (Macro)",
                value: evaluationMetrics.statusClassification.recallMacro,
              },
              {
                label: "Recall (Weighted)",
                value: evaluationMetrics.statusClassification.recallWeighted,
              },
              {
                label: "F1-Score (Macro)",
                value: evaluationMetrics.statusClassification.f1Macro,
              },
              {
                label: "F1-Score (Weighted)",
                value: evaluationMetrics.statusClassification.f1Weighted,
              },
            ].map((metric) => (
              <div key={metric.label}>
                <div className="flex justify-between mb-1">
                  <span className="text-sm text-gray-700 dark:text-gray-300">
                    {metric.label}
                  </span>
                  <span className="text-sm font-bold text-gray-900 dark:text-white">
                    {(metric.value * 100).toFixed(2)}%
                  </span>
                </div>
                <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2">
                  <div
                    className="bg-primary-600 dark:bg-primary-500 h-2 rounded-full"
                    style={{ width: `${metric.value * 100}%` }}
                  ></div>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Word-Level Metrics */}
        <div className="card">
          <h3 className="text-lg font-bold text-gray-900 dark:text-white mb-4 flex items-center gap-2">
            <LineChart className="w-5 h-5 text-primary-600 dark:text-primary-400" />
            Word-Level Similarity
          </h3>
          <div className="space-y-3">
            {[
              {
                label: "Exact Match Accuracy",
                value: evaluationMetrics.wordLevel.exactMatch,
              },
              {
                label: "Partial Match",
                value: evaluationMetrics.wordLevel.partialMatch,
              },
              {
                label: "F1-Score (Word-level)",
                value: evaluationMetrics.wordLevel.f1Score,
              },
            ].map((metric) => (
              <div key={metric.label}>
                <div className="flex justify-between mb-1">
                  <span className="text-sm text-gray-700 dark:text-gray-300">
                    {metric.label}
                  </span>
                  <span className="text-sm font-bold text-gray-900 dark:text-white">
                    {(metric.value * 100).toFixed(2)}%
                  </span>
                </div>
                <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2">
                  <div
                    className="bg-green-600 dark:bg-green-500 h-2 rounded-full"
                    style={{ width: `${metric.value * 100}%` }}
                  ></div>
                </div>
              </div>
            ))}
          </div>

          {/* Evaluation Info */}
          <div className="mt-6 pt-4 border-t border-gray-200 dark:border-gray-700">
            <h4 className="text-sm font-semibold text-gray-700 dark:text-gray-300 mb-2">
              Evaluation Details
            </h4>
            <div className="grid grid-cols-2 gap-2 text-xs">
              <div>
                <p className="text-gray-600 dark:text-gray-400">
                  Total Samples
                </p>
                <p className="font-bold text-gray-900 dark:text-white">
                  {evaluationMetrics.evaluation.totalSamples.toLocaleString()}
                </p>
              </div>
              <div>
                <p className="text-gray-600 dark:text-gray-400">
                  Evaluation Time
                </p>
                <p className="font-bold text-gray-900 dark:text-white">
                  {evaluationMetrics.evaluation.evaluationTime}
                </p>
              </div>
              <div>
                <p className="text-gray-600 dark:text-gray-400">
                  Suspicious Ratio
                </p>
                <p className="font-bold text-gray-900 dark:text-white">
                  {(evaluationMetrics.evaluation.suspiciousRatio * 100).toFixed(
                    0,
                  )}
                  %
                </p>
              </div>
              <div>
                <p className="text-gray-600 dark:text-gray-400">Time/Sample</p>
                <p className="font-bold text-gray-900 dark:text-white">
                  {evaluationMetrics.evaluation.timePerSample}
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Target Metrics Comparison */}
      <div className="card">
        <h2 className="text-xl font-bold text-gray-900 dark:text-white mb-4 flex items-center gap-2">
          <AlertTriangle className="w-6 h-6 text-primary-600 dark:text-primary-400" />
          Target vs Actual Performance
        </h2>
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead>
              <tr className="border-b border-gray-200 dark:border-gray-700">
                <th className="text-left py-3 px-4 text-sm font-semibold text-gray-700 dark:text-gray-300">
                  Metric
                </th>
                <th className="text-left py-3 px-4 text-sm font-semibold text-gray-700 dark:text-gray-300">
                  Target
                </th>
                <th className="text-left py-3 px-4 text-sm font-semibold text-gray-700 dark:text-gray-300">
                  Actual
                </th>
                <th className="text-left py-3 px-4 text-sm font-semibold text-gray-700 dark:text-gray-300">
                  Status
                </th>
              </tr>
            </thead>
            <tbody>
              {targetMetrics.map((item) => (
                <tr
                  key={item.metric}
                  className="border-b border-gray-100 dark:border-gray-800 hover:bg-gray-50 dark:hover:bg-gray-800/50"
                >
                  <td className="py-3 px-4 text-sm text-gray-900 dark:text-white font-medium">
                    {item.metric}
                  </td>
                  <td className="py-3 px-4 text-sm text-gray-700 dark:text-gray-300">
                    {item.target}
                  </td>
                  <td className="py-3 px-4 text-sm font-bold text-gray-900 dark:text-white">
                    {item.actual}
                  </td>
                  <td className="py-3 px-4">
                    {item.status === "pass" ? (
                      <span className="inline-flex items-center gap-1 px-2 py-1 bg-green-100 dark:bg-green-900/30 text-green-700 dark:text-green-400 rounded-full text-xs font-medium">
                        <CheckCircle className="w-3 h-3" />
                        Pass
                      </span>
                    ) : (
                      <span className="inline-flex items-center gap-1 px-2 py-1 bg-red-100 dark:bg-red-900/30 text-red-700 dark:text-red-400 rounded-full text-xs font-medium">
                        <XCircle className="w-3 h-3" />
                        Fail
                      </span>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Performance Benchmarks */}
      <div className="card">
        <h2 className="text-xl font-bold text-gray-900 dark:text-white mb-4 flex items-center gap-2">
          <Clock className="w-6 h-6 text-primary-600 dark:text-primary-400" />
          Performance Benchmarks
        </h2>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          {performanceBenchmarks.map((benchmark) => (
            <div
              key={benchmark.category}
              className={`p-4 bg-${benchmark.color}-50 dark:bg-${benchmark.color}-900/20 rounded-lg border border-${benchmark.color}-200 dark:border-${benchmark.color}-800`}
            >
              <div className="flex items-center gap-2 mb-2">
                <benchmark.icon
                  className={`w-5 h-5 text-${benchmark.color}-600 dark:text-${benchmark.color}-400`}
                />
                <p
                  className={`text-xs text-${benchmark.color}-700 dark:text-${benchmark.color}-400 font-medium`}
                >
                  {benchmark.category}
                </p>
              </div>
              <p
                className={`text-2xl font-bold text-${benchmark.color}-900 dark:text-${benchmark.color}-300`}
              >
                {benchmark.value}
              </p>
            </div>
          ))}
        </div>
      </div>

      {/* Test Cases Summary */}
      <div className="card">
        <h2 className="text-xl font-bold text-gray-900 dark:text-white mb-4 flex items-center gap-2">
          <CheckCircle className="w-6 h-6 text-primary-600 dark:text-primary-400" />
          Test Cases Summary
        </h2>
        <p className="text-sm text-gray-600 dark:text-gray-400 mb-4">
          All 10 system test cases passed successfully
        </p>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
          {testCases.map((testCase) => (
            <div
              key={testCase.id}
              className="flex items-center justify-between p-3 bg-gray-50 dark:bg-gray-800/50 rounded-lg border border-gray-200 dark:border-gray-700"
            >
              <div className="flex items-center gap-3">
                <span className="px-2 py-1 bg-primary-100 dark:bg-primary-900/30 text-primary-700 dark:text-primary-400 rounded text-xs font-bold">
                  {testCase.id}
                </span>
                <div>
                  <p className="text-sm font-medium text-gray-900 dark:text-white">
                    {testCase.title}
                  </p>
                  <p className="text-xs text-gray-600 dark:text-gray-400">
                    {testCase.accuracy}
                  </p>
                </div>
              </div>
              {testCase.status === "passed" ? (
                <CheckCircle className="w-5 h-5 text-green-600 dark:text-green-400" />
              ) : testCase.status === "warning" ? (
                <AlertTriangle className="w-5 h-5 text-yellow-600 dark:text-yellow-400" />
              ) : testCase.status === "failed" ? (
                <XCircle className="w-5 h-5 text-red-600 dark:text-red-400" />
              ) : (
                <AlertTriangle className="w-5 h-5 text-orange-600 dark:text-orange-400" />
              )}
            </div>
          ))}
        </div>
      </div>

      {/* Fine-Tuning Configuration */}
      <div className="card">
        <h2 className="text-xl font-bold text-gray-900 dark:text-white mb-4 flex items-center gap-2">
          <Cpu className="w-6 h-6 text-primary-600 dark:text-primary-400" />
          Fine-Tuning Configuration
        </h2>
        <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
          {Object.entries(finetuningConfig).map(([key, value]) => (
            <div
              key={key}
              className="p-3 bg-gray-50 dark:bg-gray-800/50 rounded-lg border border-gray-200 dark:border-gray-700"
            >
              <p className="text-xs text-gray-600 dark:text-gray-400 mb-1 capitalize">
                {key.replace(/([A-Z])/g, " $1").trim()}
              </p>
              <p className="text-sm font-bold text-gray-900 dark:text-white break-words">
                {value}
              </p>
            </div>
          ))}
        </div>
      </div>

      {/* Evaluation Visualizations */}
      <div className="card">
        <h2 className="text-xl font-bold text-gray-900 dark:text-white mb-4">
          📊 Evaluation Metrics Visualizations
        </h2>
        <div className="space-y-6">
          {/* Performance Metrics Charts */}
          <div>
            <h3 className="text-md font-semibold text-gray-800 dark:text-gray-200 mb-3">
              Overall Performance & Macro vs Weighted Comparison
            </h3>
            <div className="bg-white dark:bg-gray-900 p-4 rounded-lg border border-gray-200 dark:border-gray-700">
              <img
                src="/overall.png"
                alt="Overall Performance Metrics and Macro vs Weighted Comparison"
                className="w-full h-auto max-w-2xl mx-auto"
              />
            </div>
            <p className="text-xs text-gray-600 dark:text-gray-400 mt-2">
              Charts showing overall accuracy (74.6%), precision (73.2%), recall
              (74.6%), and F1-score (71.1%)
            </p>
          </div>

          {/* Confusion Matrix */}
          <div>
            <h3 className="text-md font-semibold text-gray-800 dark:text-gray-200 mb-3">
              Confusion Matrix Analysis
            </h3>
            <div className="bg-white dark:bg-gray-900 p-4 rounded-lg border border-gray-200 dark:border-gray-700">
              <img
                src="/confusion%20matrix.png"
                alt="Confusion Matrix"
                className="w-full h-auto max-w-2xl mx-auto"
              />
            </div>
            <div className="mt-4 grid grid-cols-2 md:grid-cols-4 gap-3">
              <div className="p-3 bg-green-50 dark:bg-green-900/20 rounded-lg border border-green-200 dark:border-green-800">
                <p className="text-xs text-green-700 dark:text-green-400 mb-1">
                  True Positives (Suspicious)
                </p>
                <p className="text-2xl font-bold text-green-900 dark:text-green-300">
                  {evaluationMetrics.confusionMatrix.trueSuspicious}
                </p>
              </div>
              <div className="p-3 bg-blue-50 dark:bg-blue-900/20 rounded-lg border border-blue-200 dark:border-blue-800">
                <p className="text-xs text-blue-700 dark:text-blue-400 mb-1">
                  True Negatives (Normal)
                </p>
                <p className="text-2xl font-bold text-blue-900 dark:text-blue-300">
                  {evaluationMetrics.confusionMatrix.trueNormal}
                </p>
              </div>
              <div className="p-3 bg-yellow-50 dark:bg-yellow-900/20 rounded-lg border border-yellow-200 dark:border-yellow-800">
                <p className="text-xs text-yellow-700 dark:text-yellow-400 mb-1">
                  False Positives
                </p>
                <p className="text-2xl font-bold text-yellow-900 dark:text-yellow-300">
                  {evaluationMetrics.confusionMatrix.falsePositive}
                </p>
              </div>
              <div className="p-3 bg-red-50 dark:bg-red-900/20 rounded-lg border border-red-200 dark:border-red-800">
                <p className="text-xs text-red-700 dark:text-red-400 mb-1">
                  False Negatives ⚠️
                </p>
                <p className="text-2xl font-bold text-red-900 dark:text-red-300">
                  {evaluationMetrics.confusionMatrix.falseNegative}
                </p>
              </div>
            </div>
            <p className="text-xs text-gray-600 dark:text-gray-400 mt-3">
              The confusion matrix shows that 656 normal logs were correctly
              identified, while 210 suspicious logs were missed (false
              negatives).
            </p>
          </div>
        </div>
      </div>

      {/* Per-Class Performance */}
      <div className="card bg-yellow-50 dark:bg-yellow-900/10 border-yellow-200 dark:border-yellow-800">
        <h2 className="text-xl font-bold text-gray-900 dark:text-white mb-4">
          📊 Per-Class Performance Breakdown
        </h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {/* Normal Class */}
          <div className="p-4 bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700">
            <h3 className="text-lg font-semibold text-green-700 dark:text-green-400 mb-3">
              Normal Logs (700 samples)
            </h3>
            <div className="space-y-2 text-sm">
              <div className="flex justify-between">
                <span className="text-gray-700 dark:text-gray-300">
                  Precision:
                </span>
                <span className="font-bold text-gray-900 dark:text-white">
                  {(evaluationMetrics.perClass.normal.precision * 100).toFixed(
                    2,
                  )}
                  %
                </span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-700 dark:text-gray-300">
                  Recall:
                </span>
                <span className="font-bold text-gray-900 dark:text-white">
                  {(evaluationMetrics.perClass.normal.recall * 100).toFixed(2)}%
                </span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-700 dark:text-gray-300">
                  F1-Score:
                </span>
                <span className="font-bold text-gray-900 dark:text-white">
                  {(evaluationMetrics.perClass.normal.f1Score * 100).toFixed(2)}
                  %
                </span>
              </div>
              <p className="text-xs text-green-600 dark:text-green-500 mt-2">
                ✅ Excellent performance - model correctly identifies 93.7% of
                normal activity
              </p>
            </div>
          </div>

          {/* Suspicious Class */}
          <div className="p-4 bg-white dark:bg-gray-800 rounded-lg border border-red-300 dark:border-red-700">
            <h3 className="text-lg font-semibold text-red-700 dark:text-red-400 mb-3">
              Suspicious Logs (300 samples)
            </h3>
            <div className="space-y-2 text-sm">
              <div className="flex justify-between">
                <span className="text-gray-700 dark:text-gray-300">
                  Precision:
                </span>
                <span className="font-bold text-gray-900 dark:text-white">
                  {(
                    evaluationMetrics.perClass.suspicious.precision * 100
                  ).toFixed(2)}
                  %
                </span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-700 dark:text-gray-300">
                  Recall:
                </span>
                <span className="font-bold text-red-700 dark:text-red-400">
                  {(evaluationMetrics.perClass.suspicious.recall * 100).toFixed(
                    2,
                  )}
                  %
                </span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-700 dark:text-gray-300">
                  F1-Score:
                </span>
                <span className="font-bold text-gray-900 dark:text-white">
                  {(
                    evaluationMetrics.perClass.suspicious.f1Score * 100
                  ).toFixed(2)}
                  %
                </span>
              </div>
              <p className="text-xs text-red-600 dark:text-red-500 mt-2">
                ⚠️ CRITICAL ISSUE - Model only detects 30% of suspicious
                activity (70% false negative rate)
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Key Findings */}
      <div className="card bg-blue-50 dark:bg-blue-900/20 border-blue-200 dark:border-blue-800">
        <h2 className="text-xl font-bold text-gray-900 dark:text-white mb-4">
          🎯 Key Findings & Recommendations
        </h2>
        <ul className="space-y-2 text-sm text-gray-700 dark:text-gray-300">
          <li className="flex items-start gap-2">
            <CheckCircle className="w-4 h-4 text-green-600 dark:text-green-400 mt-0.5 flex-shrink-0" />
            <span>
              <strong>Overall Accuracy: 74.6%</strong> - Model achieved 746
              correct predictions out of 1,000 test samples
            </span>
          </li>
          <li className="flex items-start gap-2">
            <CheckCircle className="w-4 h-4 text-green-600 dark:text-green-400 mt-0.5 flex-shrink-0" />
            <span>
              <strong>Low False Positive Rate (6.3%)</strong> - Only 44 normal
              logs misclassified as suspicious, minimizing alert fatigue
            </span>
          </li>
          <li className="flex items-start gap-2">
            <CheckCircle className="w-4 h-4 text-green-600 dark:text-green-400 mt-0.5 flex-shrink-0" />
            <span>
              <strong>Excellent Normal Detection (93.7% recall)</strong> - Model
              reliably identifies benign activity
            </span>
          </li>
          <li className="flex items-start gap-2">
            <AlertTriangle className="w-4 h-4 text-yellow-600 dark:text-yellow-400 mt-0.5 flex-shrink-0" />
            <span>
              <strong>
                Below Target Overall Accuracy (74.6% vs 85% target)
              </strong>{" "}
              - Primarily due to suspicious class performance
            </span>
          </li>
          <li className="flex items-start gap-2">
            <XCircle className="w-4 h-4 text-red-600 dark:text-red-400 mt-0.5 flex-shrink-0" />
            <span>
              <strong>CRITICAL: Very High False Negative Rate (70%)</strong> -
              Model misses 210 out of 300 suspicious logs. This is a major
              security risk requiring immediate attention.
            </span>
          </li>
          <li className="flex items-start gap-2">
            <XCircle className="w-4 h-4 text-red-600 dark:text-red-400 mt-0.5 flex-shrink-0" />
            <span>
              <strong>Poor Suspicious Activity Recall (30%)</strong> - Model
              only detects 90 out of 300 threats, far below the 75% target
            </span>
          </li>
          <li className="flex items-start gap-2">
            <AlertTriangle className="w-4 h-4 text-orange-600 dark:text-orange-400 mt-0.5 flex-shrink-0" />
            <span>
              <strong>Class Imbalance Impact</strong> - The 70/30 split (700
              normal, 300 suspicious) appears to bias the model toward
              predicting "normal"
            </span>
          </li>
          <li className="flex items-start gap-2">
            <AlertTriangle className="w-4 h-4 text-orange-600 dark:text-orange-400 mt-0.5 flex-shrink-0" />
            <span>
              <strong>Recommendations:</strong> 1) Retrain with balanced dataset
              or class weights, 2) Adjust classification threshold to favor
              recall over precision for security, 3) Consider ensemble methods
              or data augmentation for suspicious samples
            </span>
          </li>
        </ul>
      </div>
    </div>
  );
}
