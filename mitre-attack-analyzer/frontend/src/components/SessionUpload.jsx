import { useState } from "react";
import {
  Upload,
  FileJson,
  Loader2,
  CheckCircle,
  AlertCircle,
} from "lucide-react";
import { chunkCache } from "../services/chunkCache";
import { chunkSessionLogs, generateSessionId } from "../utils/chunking";

export default function SessionUpload({ onUploadComplete }) {
  const [file, setFile] = useState(null);
  const [sessionName, setSessionName] = useState("");
  const [uploading, setUploading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);

  const handleFileChange = (e) => {
    const selectedFile = e.target.files[0];
    if (selectedFile) {
      if (
        selectedFile.type === "application/json" ||
        selectedFile.name.endsWith(".json")
      ) {
        setFile(selectedFile);
        setError(null);
      } else {
        setError("Please select a valid JSON file");
        setFile(null);
      }
    }
  };

  const handleUpload = async () => {
    if (!file) {
      setError("Please select a file first");
      return;
    }

    setUploading(true);
    setError(null);
    setResult(null);

    try {
      // Read file content
      const fileContent = await file.text();

      // Generate session ID from filename
      const sessionId = generateSessionId(file.name);

      // Parse and chunk logs locally
      const { chunks, total_logs, total_chunks } =
        chunkSessionLogs(fileContent);

      // Store chunks in IndexedDB
      await chunkCache.storeSession(sessionId, chunks, {
        session_name: sessionName || file.name,
        filename: file.name,
        file_size: file.size,
        upload_time: new Date().toISOString(),
      });

      setResult({
        session_id: sessionId,
        session_name: sessionName || file.name,
        total_logs,
        total_chunks,
        message: "Session cached locally and ready for analysis",
      });

      setFile(null);
      setSessionName("");

      // Reset file input
      document.getElementById("file-input").value = "";

      // Notify parent component
      if (onUploadComplete) {
        onUploadComplete();
      }
    } catch (err) {
      console.error("Upload error:", err);
      setError(err.message || "Failed to process session");
    } finally {
      setUploading(false);
    }
  };

  const handleDrop = (e) => {
    e.preventDefault();
    const droppedFile = e.dataTransfer.files[0];
    if (droppedFile) {
      if (
        droppedFile.type === "application/json" ||
        droppedFile.name.endsWith(".json")
      ) {
        setFile(droppedFile);
        setError(null);
      } else {
        setError("Please drop a valid JSON file");
      }
    }
  };

  const handleDragOver = (e) => {
    e.preventDefault();
  };

  return (
    <div className="card">
      <h3 className="text-lg font-bold text-gray-900 dark:text-white mb-4 flex items-center gap-2">
        <Upload className="w-5 h-5 text-primary-600 dark:text-primary-400" />
        Upload Full Session
      </h3>

      {/* File Drop Zone */}
      <div
        onDrop={handleDrop}
        onDragOver={handleDragOver}
        className="border-2 border-dashed border-gray-300 dark:border-gray-600 rounded-lg p-8 text-center hover:border-primary-500 dark:hover:border-primary-400 transition-colors cursor-pointer"
      >
        <input
          id="file-input"
          type="file"
          accept=".json"
          onChange={handleFileChange}
          className="hidden"
        />
        <label htmlFor="file-input" className="cursor-pointer">
          <FileJson className="w-12 h-12 mx-auto text-gray-400 dark:text-gray-500 mb-4" />
          <p className="text-sm text-gray-600 dark:text-gray-400 mb-2">
            Click to upload or drag and drop
          </p>
          <p className="text-xs text-gray-500 dark:text-gray-500">
            JSON files only
          </p>
        </label>
      </div>

      {/* Selected File Info */}
      {file && (
        <div className="mt-4 p-3 bg-primary-50 dark:bg-primary-900/20 rounded-lg border border-primary-200 dark:border-primary-800">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <FileJson className="w-5 h-5 text-primary-600 dark:text-primary-400" />
              <div>
                <p className="text-sm font-medium text-primary-900 dark:text-primary-300">
                  {file.name}
                </p>
                <p className="text-xs text-primary-700 dark:text-primary-400">
                  {(file.size / 1024).toFixed(2)} KB
                </p>
              </div>
            </div>
            <button
              onClick={() => {
                setFile(null);
                document.getElementById("file-input").value = "";
              }}
              className="text-xs text-primary-600 dark:text-primary-400 hover:underline"
            >
              Remove
            </button>
          </div>
        </div>
      )}

      {/* Session Name Input */}
      <div className="mt-4">
        <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
          Session Name (Optional)
        </label>
        <input
          type="text"
          value={sessionName}
          onChange={(e) => setSessionName(e.target.value)}
          placeholder="e.g., Credential Harvesting Attack"
          className="w-full px-3 py-2 bg-white dark:bg-gray-700 border border-gray-300 dark:border-gray-600 rounded-lg text-gray-900 dark:text-white placeholder-gray-500 dark:placeholder-gray-400 focus:ring-2 focus:ring-primary-500 dark:focus:ring-primary-400 focus:border-transparent"
        />
      </div>

      {/* Upload Button */}
      <button
        onClick={handleUpload}
        disabled={!file || uploading}
        className="btn btn-primary w-full mt-4"
      >
        {uploading ? (
          <>
            <Loader2 className="w-4 h-4 animate-spin" />
            Processing...
          </>
        ) : (
          <>
            <Upload className="w-4 h-4" />
            Upload & Chunk Session
          </>
        )}
      </button>

      {/* Success Message */}
      {result && (
        <div className="mt-4 p-4 bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-800 rounded-lg">
          <div className="flex items-start gap-3">
            <CheckCircle className="w-5 h-5 text-green-600 dark:text-green-400 flex-shrink-0 mt-0.5" />
            <div className="flex-1">
              <h4 className="text-sm font-semibold text-green-900 dark:text-green-300 mb-2">
                Session Uploaded Successfully!
              </h4>
              <div className="text-xs text-green-800 dark:text-green-400 space-y-1">
                <p>
                  Session ID:{" "}
                  <span className="font-mono">{result.session_id}</span>
                </p>
                <p>
                  Total Logs:{" "}
                  <span className="font-semibold">{result.total_logs}</span>
                </p>
                <p>
                  Chunks Created:{" "}
                  <span className="font-semibold">{result.total_chunks}</span>
                </p>
                <p className="mt-2 italic">{result.message}</p>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Error Message */}
      {error && (
        <div className="mt-4 p-4 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg">
          <div className="flex items-start gap-3">
            <AlertCircle className="w-5 h-5 text-red-600 dark:text-red-400 flex-shrink-0 mt-0.5" />
            <div className="flex-1">
              <h4 className="text-sm font-semibold text-red-900 dark:text-red-300 mb-1">
                Upload Failed
              </h4>
              <p className="text-xs text-red-800 dark:text-red-400">{error}</p>
            </div>
          </div>
        </div>
      )}

      {/* Info Box */}
      <div className="mt-4 p-3 bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-lg">
        <p className="text-xs text-blue-900 dark:text-blue-300">
          <strong>Fast Local Storage:</strong> Sessions are chunked and stored
          locally in your browser using IndexedDB. This provides instant access
          without database overhead. Only analysis results are sent to the
          server.
        </p>
      </div>
    </div>
  );
}
