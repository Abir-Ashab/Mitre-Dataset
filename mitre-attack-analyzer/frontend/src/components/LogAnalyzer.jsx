import { useState } from "react";
import { Upload, FileJson, X, Loader2, Shield } from "lucide-react";
import { logService } from "../services/api";
import AnalysisResult from "./AnalysisResult";

export default function LogAnalyzer({ onAnalysisComplete }) {
  const [logContent, setLogContent] = useState("");
  const [file, setFile] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [result, setResult] = useState(null);

  const handleFileChange = (e) => {
    const selectedFile = e.target.files?.[0];
    if (selectedFile) {
      setFile(selectedFile);
      const reader = new FileReader();
      reader.onload = (event) => {
        setLogContent(event.target.result);
      };
      reader.readAsText(selectedFile);
    }
  };

  const handleRemoveFile = () => {
    setFile(null);
    setLogContent("");
  };

  const handleAnalyze = async () => {
    if (!logContent.trim()) {
      setError("Please enter or upload log content");
      return;
    }

    setLoading(true);
    setError(null);
    setResult(null);

    try {
      const response = await logService.analyzeLog(logContent);
      setResult(response);
      if (onAnalysisComplete) {
        onAnalysisComplete();
      }
    } catch (err) {
      setError(
        err.response?.data?.detail ||
          "Failed to analyze log. Please try again.",
      );
      console.error("Analysis error:", err);
    } finally {
      setLoading(false);
    }
  };

  const handleClear = () => {
    setLogContent("");
    setFile(null);
    setError(null);
    setResult(null);
  };

  return (
    <div className="space-y-6">
      <div className="card">
        <h2 className="text-xl font-bold text-gray-900 dark:text-white mb-4 flex items-center gap-2">
          <FileJson className="w-6 h-6 text-primary-600 dark:text-primary-400" />
          Analyze Security Log
        </h2>

        <div className="space-y-4">
          {/* File Upload */}
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Upload JSON Log File (Optional)
            </label>
            {!file ? (
              <label className="flex flex-col items-center justify-center w-full h-32 border-2 border-dashed border-gray-300 dark:border-gray-600 rounded-lg cursor-pointer hover:border-primary-500 hover:bg-primary-50 dark:hover:bg-primary-900/20 transition-colors">
                <div className="flex flex-col items-center justify-center pt-5 pb-6">
                  <Upload className="w-8 h-8 text-gray-400 dark:text-gray-500 mb-2" />
                  <p className="text-sm text-gray-600 dark:text-gray-400">
                    Click to upload or drag and drop
                  </p>
                  <p className="text-xs text-gray-500 dark:text-gray-500 mt-1">
                    JSON files only
                  </p>
                </div>
                <input
                  type="file"
                  className="hidden"
                  accept=".json"
                  onChange={handleFileChange}
                />
              </label>
            ) : (
              <div className="flex items-center justify-between p-3 bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-700 rounded-lg">
                <div className="flex items-center gap-2">
                  <FileJson className="w-5 h-5 text-blue-600 dark:text-blue-400" />
                  <span className="text-sm font-medium text-blue-900 dark:text-blue-200">
                    {file.name}
                  </span>
                  <span className="text-xs text-blue-700 dark:text-blue-300">
                    ({(file.size / 1024).toFixed(2)} KB)
                  </span>
                </div>
                <button
                  onClick={handleRemoveFile}
                  className="p-1 hover:bg-blue-100 dark:hover:bg-blue-800/50 rounded transition-colors"
                >
                  <X className="w-4 h-4 text-blue-600 dark:text-blue-400" />
                </button>
              </div>
            )}
          </div>

          {/* Text Area */}
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Log Content (JSON Format)
            </label>
            <textarea
              value={logContent}
              onChange={(e) => setLogContent(e.target.value)}
              placeholder='Paste your JSON log here, e.g., {"event_id": 4624, "timestamp": "..."}'
              className="w-full h-64 p-3 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent font-mono text-sm resize-none bg-white dark:bg-gray-900 text-gray-900 dark:text-gray-100 placeholder-gray-400 dark:placeholder-gray-500"
            />
            <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
              Maximum 6000 characters
            </p>
          </div>

          {/* Error Display */}
          {error && (
            <div className="bg-danger-50 dark:bg-danger-900/20 border border-danger-200 dark:border-danger-800 rounded-lg p-3">
              <p className="text-sm text-danger-700 dark:text-danger-400">
                {error}
              </p>
            </div>
          )}

          {/* Action Buttons */}
          <div className="flex gap-3">
            <button
              onClick={handleAnalyze}
              disabled={loading || !logContent.trim()}
              className="btn btn-primary flex items-center gap-2 flex-1"
            >
              {loading ? (
                <>
                  <Loader2 className="w-4 h-4 animate-spin" />
                  Analyzing...
                </>
              ) : (
                <>
                  <Shield className="w-4 h-4" />
                  Analyze Log
                </>
              )}
            </button>
            <button
              onClick={handleClear}
              disabled={loading}
              className="btn btn-secondary"
            >
              Clear
            </button>
          </div>
        </div>
      </div>

      {/* Results */}
      {result && <AnalysisResult result={result} />}
    </div>
  );
}
