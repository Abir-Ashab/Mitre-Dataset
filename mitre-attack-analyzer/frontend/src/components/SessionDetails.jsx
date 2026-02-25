import { useState, useEffect } from "react";
import {
  ArrowLeft,
  Layers,
  PlayCircle,
  CheckCircle,
  Loader2,
  ChevronLeft,
  ChevronRight,
  AlertTriangle,
  X,
  Shield,
} from "lucide-react";
import { chunkCache } from "../services/chunkCache";
import { sessionService } from "../services/api";
import AnalysisResult from "./AnalysisResult";

/**
 * SessionDetails Component
 *
 * Displays session chunks with pagination and allows chunk-level analysis.
 *
 * ANALYSIS PERSISTENCE:
 * - When you analyze a chunk, the result is saved to MongoDB (backend database)
 * - Analysis results include: status, reason, MITRE techniques, raw output, and timestamp
 * - Results persist across page reloads - when you return to this session, previously
 *   analyzed chunks will show their saved results automatically
 * - You can click on the Normal/Suspicious badges to view the full analysis details
 * - Re-analyze button allows updating the analysis if needed
 *
 * DATA SOURCES:
 * - MongoDB (primary): Recently uploaded sessions with analysis persistence
 * - IndexedDB (fallback): Legacy sessions stored locally before MongoDB integration
 */
export default function SessionDetails({ sessionId, onBack }) {
  const [chunks, setChunks] = useState([]);
  const [loading, setLoading] = useState(true);
  const [analyzing, setAnalyzing] = useState(null);
  const [error, setError] = useState(null);
  const [page, setPage] = useState(1);
  const [totalChunks, setTotalChunks] = useState(0);
  const [selectedChunk, setSelectedChunk] = useState(null);
  const [showModal, setShowModal] = useState(false);

  const CHUNKS_PER_PAGE = 50;
  const totalPages = Math.ceil(totalChunks / CHUNKS_PER_PAGE);

  useEffect(() => {
    fetchSessionDetails();
  }, [sessionId, page]);

  useEffect(() => {
    const handleEscape = (e) => {
      if (e.key === "Escape" && showModal) {
        setShowModal(false);
      }
    };

    window.addEventListener("keydown", handleEscape);
    return () => window.removeEventListener("keydown", handleEscape);
  }, [showModal]);

  const fetchSessionDetails = async () => {
    try {
      setLoading(true);
      const skip = (page - 1) * CHUNKS_PER_PAGE;

      try {
        // Try to fetch from backend API (MongoDB) first
        console.log(`[Fetch] Requesting session details for: ${sessionId}`);
        console.log(
          `[Fetch] Pagination: skip=${skip}, limit=${CHUNKS_PER_PAGE}`,
        );

        const data = await sessionService.getSessionDetails(
          sessionId,
          skip,
          CHUNKS_PER_PAGE,
        );

        console.log("[Fetch] ✅ Retrieved chunks from MongoDB");
        console.log("[Fetch] Response data:", {
          session_id: data.session_id,
          session_name: data.session_name,
          total_chunks: data.total_chunks,
          analyzed_chunks: data.analyzed_chunks,
          chunks_count: data.chunks?.length,
        });

        // Log each chunk's analysis status
        data.chunks.forEach((chunk, idx) => {
          if (chunk.analysis_result || chunk.analysis_status) {
            console.log(`[Fetch] Chunk ${chunk.chunk_index} has analysis:`, {
              is_analyzed: chunk.is_analyzed,
              analysis_status: chunk.analysis_status,
              has_analysis_result: !!chunk.analysis_result,
              analysis_result_keys: chunk.analysis_result
                ? Object.keys(chunk.analysis_result)
                : [],
              analyzed_at: chunk.analyzed_at,
            });
          }
        });

        const analyzedCount = data.chunks.filter(
          (c) => c.analysis_result || c.is_analyzed,
        ).length;
        console.log(
          `[Persistence] ✅ ${analyzedCount}/${data.chunks.length} chunks have saved analysis results from database`,
        );

        setChunks(data.chunks || []);
        setTotalChunks(data.total_chunks || data.total || 0);
        setError(null);
      } catch (backendError) {
        // If not found in MongoDB (404), fall back to IndexedDB (old sessions)
        if (backendError.response?.status === 404) {
          console.log("[Fetch] Session not in MongoDB, trying IndexedDB...");
          const data = await chunkCache.getSessionChunks(
            sessionId,
            skip,
            CHUNKS_PER_PAGE,
          );
          console.log("[Fetch] Retrieved chunks from IndexedDB:", data.chunks);
          setChunks(data.chunks || []);
          setTotalChunks(data.total || 0);
          setError(null);
        } else {
          throw backendError;
        }
      }
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
      setError(null);

      console.log(`[Analysis] Starting analysis for chunk ${chunkIndex}`);

      // Try to get chunk data from current chunks array first
      let chunkLogs;
      let chunkData = chunks.find((c) => c.chunk_index === chunkIndex);

      if (chunkData && chunkData.logs_json) {
        // MongoDB chunk has logs_json directly
        chunkLogs = chunkData.logs_json;
      } else {
        // Fall back to IndexedDB for old sessions
        const indexedDBChunk = await chunkCache.getChunk(sessionId, chunkIndex);
        console.log(`[Analysis] Chunk data from IndexedDB:`, indexedDBChunk);
        chunkLogs = indexedDBChunk?.logs_json || indexedDBChunk;
      }

      if (!chunkLogs) {
        throw new Error("No log data found for this chunk");
      }

      // Analyze the chunk using the new endpoint (saves to MongoDB)
      console.log(`[Analysis] Sending analysis request to backend...`);
      const result = await sessionService.analyzeChunk(
        sessionId,
        chunkIndex,
        JSON.stringify(chunkLogs),
      );

      console.log("[Analysis] ✅ Backend response received:", {
        analysis_id: result.analysis_id,
        status: result.status,
        mitre_techniques: result.mitre_techniques,
        has_reason: !!result.reason,
        has_raw_output: !!result.raw_output,
        analyzed_at: result.analyzed_at,
      });
      console.log("[Analysis] Full result object:", result);
      console.log("[Analysis] ✅ Analysis saved to database successfully!");

      // Update the local chunks state immediately with analysis results
      setChunks((prevChunks) =>
        prevChunks.map((chunk) =>
          chunk.chunk_index === chunkIndex
            ? {
                ...chunk,
                is_analyzed: true,
                analysis_id: result.analysis_id,
                analysis_status: result.status,
                analysis_result: {
                  analysis_id: result.analysis_id,
                  status: result.status,
                  reason: result.reason,
                  mitre_techniques: result.mitre_techniques,
                  raw_output: result.raw_output,
                  processing_time_ms: result.processing_time_ms,
                  analyzed_at: result.analyzed_at,
                },
                analyzed_at: result.analyzed_at,
              }
            : chunk,
        ),
      );

      console.log(
        "[Analysis] Chunk state updated. Analysis is now persisted in DB and will be available on page reload.",
      );
      console.log(
        `[Analysis] ✅ Chunk ${chunkIndex} analysis complete! Status: ${result.status}. This result is saved and will persist across page reloads.`,
      );

      console.log(`[Analysis] Chunk ${chunkIndex} analysis complete!`);
    } catch (err) {
      console.error("[Analysis] Error:", err);
      setError(`Failed to analyze chunk ${chunkIndex}: ${err.message}`);
    } finally {
      setAnalyzing(null);
    }
  };

  const handleViewAnalysis = (chunk) => {
    console.log("[Modal] Opening analysis modal for chunk:", chunk.chunk_index);
    console.log("[Modal] Chunk data:", chunk);
    console.log("[Modal] Analysis result:", chunk.analysis_result);
    setSelectedChunk(chunk);
    setShowModal(true);
  };

  const getStatusBadge = (status) => {
    switch ((status || "").toLowerCase()) {
      case "normal":
        return (
          <span className="inline-flex items-center gap-1 px-2 py-0.5 text-xs font-medium rounded-full bg-green-100 dark:bg-green-900/30 text-green-700 dark:text-green-400 border border-green-200 dark:border-green-700 cursor-pointer hover:bg-green-200 dark:hover:bg-green-900/50 transition-colors">
            <CheckCircle className="w-3 h-3" />
            Normal
          </span>
        );
      case "suspicious":
        return (
          <span className="inline-flex items-center gap-1 px-2 py-0.5 text-xs font-medium rounded-full bg-red-100 dark:bg-red-900/30 text-red-700 dark:text-red-400 border border-red-200 dark:border-red-700 cursor-pointer hover:bg-red-200 dark:hover:bg-red-900/50 transition-colors">
            <AlertTriangle className="w-3 h-3" />
            Suspicious
          </span>
        );
      default:
        return null;
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

  return (
    <div className="space-y-4">
      {/* Header */}
      <div className="card">
        <button onClick={onBack} className="btn btn-secondary mb-4">
          <ArrowLeft className="w-4 h-4" />
          Back to Sessions
        </button>

        <h3 className="text-lg font-bold text-gray-900 dark:text-white mb-2">
          {chunks[0]?.session_name ||
            chunks[0]?.metadata?.session_name ||
            sessionId}
        </h3>
        <p className="text-sm text-gray-600 dark:text-gray-400 font-mono mb-4">
          {sessionId}
        </p>

        {/* Error Display */}
        {error && (
          <div className="mb-4 p-3 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg">
            <p className="text-sm text-red-700 dark:text-red-400">{error}</p>
          </div>
        )}

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
              On This Page
            </p>
            <p className="text-2xl font-bold text-green-900 dark:text-green-300">
              {chunks.length}
            </p>
          </div>
        </div>
      </div>

      {/* Chunks List */}
      <div className="card">
        <h4 className="text-md font-bold text-gray-900 dark:text-white mb-4 flex items-center gap-2">
          <Layers className="w-5 h-5 text-primary-600 dark:text-primary-400" />
          Chunks (Page {page} of {totalPages})
        </h4>

        {chunks.length === 0 ? (
          <div className="text-center py-8 text-gray-500 dark:text-gray-400">
            No chunks found for this session
          </div>
        ) : (
          <div className="space-y-2">
            {chunks.map((chunk) => (
              <div
                key={chunk.chunk_id || chunk.id}
                className="flex items-center justify-between p-3 bg-gray-50 dark:bg-gray-800/50 rounded-lg border border-gray-200 dark:border-gray-700"
              >
                <div className="flex-1">
                  <div className="flex items-center gap-2 mb-1">
                    <span className="text-sm font-semibold text-gray-900 dark:text-white">
                      Chunk {chunk.chunk_index}
                    </span>
                    {chunk.analysis_status && (
                      <button
                        onClick={() => handleViewAnalysis(chunk)}
                        className="focus:outline-none focus:ring-2 focus:ring-primary-500 rounded-full"
                        type="button"
                      >
                        {getStatusBadge(chunk.analysis_status)}
                      </button>
                    )}
                  </div>
                  <div className="flex items-center gap-4 text-xs text-gray-600 dark:text-gray-400">
                    <span>
                      {chunk.chunk_size ||
                        chunk.logs_json?.length ||
                        chunk.metadata?.number_of_events ||
                        0}{" "}
                      logs
                    </span>
                    {(chunk.start_time || chunk.metadata?.start_time) &&
                      (chunk.start_time || chunk.metadata?.start_time) !==
                        "unknown" && (
                        <span className="text-gray-500 dark:text-gray-500">
                          {new Date(
                            chunk.start_time || chunk.metadata.start_time,
                          ).toLocaleTimeString()}
                        </span>
                      )}
                    {chunk.analyzed_at && (
                      <span className="text-green-600 dark:text-green-400">
                        Analyzed: {new Date(chunk.analyzed_at).toLocaleString()}
                      </span>
                    )}
                  </div>
                </div>
                <button
                  onClick={() => handleAnalyzeChunk(chunk.chunk_index)}
                  disabled={analyzing === chunk.chunk_index}
                  className="btn btn-primary text-xs py-2 px-3 disabled:opacity-50"
                >
                  {analyzing === chunk.chunk_index ? (
                    <>
                      <Loader2 className="w-3 h-3 animate-spin" />
                      Analyzing...
                    </>
                  ) : chunk.analysis_status ? (
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
        )}

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

      {/* Analysis Details Modal */}
      {showModal && selectedChunk && (
        <div
          className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50"
          onClick={(e) => {
            // Close modal when clicking on backdrop
            if (e.target === e.currentTarget) {
              setShowModal(false);
            }
          }}
        >
          <div className="bg-white dark:bg-gray-800 rounded-lg max-w-4xl w-full max-h-[90vh] overflow-y-auto shadow-xl">
            <div className="sticky top-0 bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700 p-4 flex items-center justify-between z-10">
              <h3 className="text-lg font-bold text-gray-900 dark:text-white flex items-center gap-2">
                <Shield className="w-5 h-5 text-primary-600 dark:text-primary-400" />
                Chunk {selectedChunk.chunk_index} - Analysis Details
              </h3>
              <button
                onClick={() => setShowModal(false)}
                className="p-1 hover:bg-gray-100 dark:hover:bg-gray-700 rounded transition-colors"
                type="button"
              >
                <X className="w-5 h-5 text-gray-600 dark:text-gray-400" />
              </button>
            </div>
            <div className="p-6">
              {selectedChunk.analysis_result ? (
                <AnalysisResult result={selectedChunk.analysis_result} />
              ) : (
                <div className="text-center py-8">
                  <p className="text-gray-500 dark:text-gray-400 mb-2">
                    No analysis result available
                  </p>
                  <pre className="text-xs text-left bg-gray-100 dark:bg-gray-900 p-4 rounded overflow-auto">
                    {JSON.stringify(selectedChunk, null, 2)}
                  </pre>
                </div>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
