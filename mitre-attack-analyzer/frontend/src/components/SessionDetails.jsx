import { useState, useEffect } from "react";
import {
  ArrowLeft,
  Layers,
  PlayCircle,
  CheckCircle,
  Loader2,
  ChevronLeft,
  ChevronRight,
} from "lucide-react";
import { sessionService, logService } from "../services/api";

export default function SessionDetails({ sessionId, onBack }) {
  const [session, setSession] = useState(null);
  const [loading, setLoading] = useState(true);
  const [analyzing, setAnalyzing] = useState(null);
  const [error, setError] = useState(null);
  const [page, setPage] = useState(1);
  const [totalChunks, setTotalChunks] = useState(0);

  const CHUNKS_PER_PAGE = 50;
  const totalPages = Math.ceil(totalChunks / CHUNKS_PER_PAGE);

  useEffect(() => {
    fetchSessionDetails();
  }, [sessionId, page]);

  const fetchSessionDetails = async () => {
    try {
      setLoading(true);
      const skip = (page - 1) * CHUNKS_PER_PAGE;
      const data = await sessionService.getSessionDetails(
        sessionId,
        skip,
        CHUNKS_PER_PAGE,
      );
      setSession(data);
      setTotalChunks(data.total_chunks || 0);
      setError(null);
    } catch (err) {
      setError("Failed to load session details");
      console.error("Session details error:", err);
    } finally {
      setLoading(false);
    }
  };

  const handleAnalyzeChunk = async (chunkIndex) => {
    try {
      setAnalyzing(chunkIndex);

      // Get chunk data
      const chunkData = await sessionService.getChunkData(
        sessionId,
        chunkIndex,
      );

      // Analyze the chunk
      const result = await logService.analyzeLog(
        chunkData.logs_json,
        sessionId,
      );

      console.log("Analysis result:", result);

      // Refresh session to update analyzed status
      await fetchSessionDetails();

      alert(`Chunk ${chunkIndex} analyzed: ${result.status}`);
    } catch (err) {
      console.error("Analysis error:", err);
      alert("Failed to analyze chunk");
    } finally {
      setAnalyzing(null);
    }
  };

  if (loading) {
    return (
      <div className="card flex items-center justify-center h-64">
        <Loader2 className="w-8 h-8 text-primary-600 dark:text-primary-400 animate-spin" />
      </div>
    );
  }

  if (error) {
    return (
      <div className="card">
        <button onClick={onBack} className="btn btn-secondary mb-4">
          <ArrowLeft className="w-4 h-4" />
          Back
        </button>
        <p className="text-danger-600 dark:text-danger-400 text-sm">{error}</p>
      </div>
    );
  }

  if (!session) return null;

  const progress =
    totalChunks > 0 ? (session.analyzed_chunks / totalChunks) * 100 : 0;

  return (
    <div className="space-y-4">
      {/* Header */}
      <div className="card">
        <button onClick={onBack} className="btn btn-secondary mb-4">
          <ArrowLeft className="w-4 h-4" />
          Back to Sessions
        </button>

        <h3 className="text-lg font-bold text-gray-900 dark:text-white mb-2">
          {session.session_name || session.session_id}
        </h3>
        <p className="text-sm text-gray-600 dark:text-gray-400 font-mono mb-4">
          {session.session_id}
        </p>

        {/* Progress Bar */}
        <div className="mb-4">
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm font-medium text-gray-700 dark:text-gray-300">
              Analysis Progress
            </span>
            <span className="text-sm font-semibold text-primary-600 dark:text-primary-400">
              {session.analyzed_chunks} / {totalChunks} ({progress.toFixed(0)}%)
            </span>
          </div>
          <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2.5">
            <div
              className="bg-primary-600 dark:bg-primary-500 h-2.5 rounded-full transition-all duration-300"
              style={{ width: `${progress}%` }}
            ></div>
          </div>
        </div>

        {/* Stats */}
        <div className="grid grid-cols-2 gap-4">
          <div className="p-3 bg-blue-50 dark:bg-blue-900/20 rounded-lg border border-blue-200 dark:border-blue-800">
            <p className="text-xs text-blue-700 dark:text-blue-400 mb-1">
              Total Chunks
            </p>
            <p className="text-2xl font-bold text-blue-900 dark:text-blue-300">
              {totalChunks}
            </p>
          </div>
          <div className="p-3 bg-green-50 dark:bg-green-900/20 rounded-lg border border-green-200 dark:border-green-800">
            <p className="text-xs text-green-700 dark:text-green-400 mb-1">
              Analyzed
            </p>
            <p className="text-2xl font-bold text-green-900 dark:text-green-300">
              {session.analyzed_chunks}
            </p>
          </div>
        </div>
      </div>

      {/* Chunks List */}
      <div className="card">
        <h4 className="text-md font-bold text-gray-900 dark:text-white mb-4 flex items-center gap-2">
          <Layers className="w-5 h-5 text-primary-600 dark:text-primary-400" />
          Chunks
        </h4>

        <div className="space-y-2">
          {session.chunks.map((chunk) => (
            <div
              key={chunk.chunk_id}
              className="flex items-center justify-between p-3 bg-gray-50 dark:bg-gray-800/50 rounded-lg border border-gray-200 dark:border-gray-700"
            >
              <div className="flex-1">
                <div className="flex items-center gap-2 mb-1">
                  <span className="text-sm font-semibold text-gray-900 dark:text-white">
                    Chunk {chunk.chunk_index}
                  </span>
                  {chunk.is_analyzed && (
                    <CheckCircle className="w-4 h-4 text-green-500 dark:text-green-400" />
                  )}
                </div>
                <div className="flex items-center gap-4 text-xs text-gray-600 dark:text-gray-400">
                  <span>{chunk.chunk_size} logs</span>
                  {chunk.start_time && chunk.start_time !== "unknown" && (
                    <span className="text-gray-500 dark:text-gray-500">
                      {new Date(chunk.start_time).toLocaleTimeString()}
                    </span>
                  )}
                </div>
              </div>
              <button
                onClick={() => handleAnalyzeChunk(chunk.chunk_index)}
                disabled={analyzing === chunk.chunk_index}
                className={`btn text-xs py-2 px-3 ${
                  chunk.is_analyzed ? "btn-secondary" : "btn-primary"
                }`}
              >
                {analyzing === chunk.chunk_index ? (
                  <>
                    <Loader2 className="w-3 h-3 animate-spin" />
                    Analyzing...
                  </>
                ) : chunk.is_analyzed ? (
                  <>
                    <PlayCircle className="w-3 h-3" />
                    Re-analyze
                  </>
                ) : (
                  <>
                    <PlayCircle className="w-3 h-3" />
                    Analyze
                  </>
                )}
              </button>
            </div>
          ))}
        </div>

        {/* Pagination Controls */}
        {totalPages > 1 && (
          <div className="flex items-center justify-between mt-4 pt-4 border-t border-gray-200 dark:border-gray-700">
            <div className="text-sm text-gray-600 dark:text-gray-400">
              Showing {(page - 1) * CHUNKS_PER_PAGE + 1} to{" "}
              {Math.min(page * CHUNKS_PER_PAGE, totalChunks)} of {totalChunks}{" "}
              chunks
            </div>
            <div className="flex items-center gap-2">
              <button
                onClick={() => setPage((p) => Math.max(1, p - 1))}
                disabled={page === 1}
                className="btn btn-secondary text-xs py-1 px-3 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                <ChevronLeft className="w-3 h-3" />
                Previous
              </button>

              <div className="flex items-center gap-1">
                {Array.from({ length: totalPages }, (_, i) => i + 1)
                  .filter((p) => {
                    // Show first page, last page, current page and neighbors
                    return (
                      p === 1 || p === totalPages || Math.abs(p - page) <= 1
                    );
                  })
                  .map((p, idx, arr) => {
                    // Add ellipsis if there's a gap
                    const prevPage = arr[idx - 1];
                    const showEllipsis = prevPage && p - prevPage > 1;

                    return (
                      <div key={p} className="flex items-center gap-1">
                        {showEllipsis && (
                          <span className="text-gray-400 dark:text-gray-500 px-1">
                            ...
                          </span>
                        )}
                        <button
                          onClick={() => setPage(p)}
                          className={`w-8 h-8 rounded text-xs font-medium transition-colors ${
                            p === page
                              ? "bg-primary-600 dark:bg-primary-500 text-white"
                              : "bg-gray-100 dark:bg-gray-800 text-gray-700 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-700"
                          }`}
                        >
                          {p}
                        </button>
                      </div>
                    );
                  })}
              </div>

              <button
                onClick={() => setPage((p) => Math.min(totalPages, p + 1))}
                disabled={page === totalPages}
                className="btn btn-secondary text-xs py-1 px-3 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                Next
                <ChevronRight className="w-3 h-3" />
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
