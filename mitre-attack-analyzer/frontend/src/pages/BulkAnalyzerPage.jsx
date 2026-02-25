import { useState, useEffect } from "react";
import {
  Shield,
  Loader2,
  CheckCircle,
  AlertTriangle,
  FolderOpen,
  Layers,
  ChevronDown,
  ChevronUp,
} from "lucide-react";
import { chunkCache } from "../services/chunkCache";
import { sessionService } from "../services/api";

export default function BulkAnalyzerPage() {
  const [sessions, setSessions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedSession, setSelectedSession] = useState(null);
  const [sessionChunks, setSessionChunks] = useState([]);
  const [analyzing, setAnalyzing] = useState(false);
  const [progress, setProgress] = useState({ current: 0, total: 0 });
  const [sessionReport, setSessionReport] = useState(null);
  const [expandedChunks, setExpandedChunks] = useState(false);
  const [maxChunks, setMaxChunks] = useState(0);

  useEffect(() => {
    fetchSessions();
  }, []);

  const fetchSessions = async (forceRefresh = false) => {
    try {
      setLoading(true);
      const startTime = performance.now();

      // Try to load from cache first (unless force refresh)
      if (!forceRefresh) {
        try {
          const cached = localStorage.getItem("bulk_sessions_cache");
          const cacheTimestamp = localStorage.getItem(
            "bulk_sessions_cache_timestamp",
          );

          if (cached && cacheTimestamp) {
            const cacheAge = Date.now() - parseInt(cacheTimestamp);
            const CACHE_DURATION = 5 * 60 * 1000; // 5 minutes

            // Use cache if less than 5 minutes old
            if (cacheAge < CACHE_DURATION) {
              const cachedData = JSON.parse(cached);
              console.log(
                `[Bulk Analyzer] ✅ Loaded from cache (${(cacheAge / 1000).toFixed(0)}s old, ${cachedData.length} sessions)`,
              );
              setSessions(cachedData);
              setLoading(false);
              return;
            } else {
              console.log(
                `[Bulk Analyzer] Cache expired (${(cacheAge / 1000).toFixed(0)}s old), fetching fresh data...`,
              );
            }
          }
        } catch (cacheError) {
          console.log("[Bulk Analyzer] Cache miss or error, fetching from DB");
        }
      } else {
        console.log(
          "[Bulk Analyzer] Force refresh requested, clearing cache...",
        );
        localStorage.removeItem("bulk_sessions_cache");
        localStorage.removeItem("bulk_sessions_cache_timestamp");
      }

      // Fetch from MongoDB
      console.log("[Bulk Analyzer] Fetching from MongoDB...");
      const mongoStart = performance.now();
      const mongoDBResponse = await sessionService.getAllSessions(0, 100);
      const mongoTime = performance.now() - mongoStart;
      console.log(
        `[Bulk Analyzer] ✅ MongoDB fetch completed in ${mongoTime.toFixed(2)}ms`,
      );

      const allSessions = (mongoDBResponse.sessions || [])
        .map((s) => ({
          ...s,
          source: "mongodb",
        }))
        .sort(
          (a, b) =>
            new Date(b.created_at || b.uploaded_at || 0) -
            new Date(a.created_at || a.uploaded_at || 0),
        );

      // Store in cache
      try {
        localStorage.setItem(
          "bulk_sessions_cache",
          JSON.stringify(allSessions),
        );
        localStorage.setItem(
          "bulk_sessions_cache_timestamp",
          Date.now().toString(),
        );
        console.log(
          `[Bulk Analyzer] ✅ Cached ${allSessions.length} sessions in localStorage`,
        );
      } catch (storageError) {
        console.warn("[Bulk Analyzer] Failed to cache sessions:", storageError);
      }

      const totalTime = performance.now() - startTime;
      console.log(
        `[Bulk Analyzer] ✅ Total time: ${totalTime.toFixed(2)}ms (${allSessions.length} sessions loaded)`,
      );

      setSessions(allSessions);
    } catch (err) {
      console.error("Failed to load sessions:", err);
    } finally {
      setLoading(false);
    }
  };

  const handleSelectSession = async (session) => {
    setSelectedSession(session);
    setSessionReport(null);
    setExpandedChunks(false);
    setMaxChunks(session.total_chunks);

    try {
      setLoading(true);
      // Fetch chunks with pagination (50 at a time to avoid loading all at once)
      try {
        const data = await sessionService.getSessionDetails(
          session.session_id,
          0,
          50, // Load first 50 chunks initially
        );
        setSessionChunks(data.chunks || []);
      } catch (backendError) {
        if (backendError.response?.status === 404) {
          const data = await chunkCache.getSessionChunks(
            session.session_id,
            0,
            50,
          );
          setSessionChunks(data.chunks || []);
        } else {
          throw backendError;
        }
      }
    } catch (err) {
      console.error("Failed to load session chunks:", err);
    } finally {
      setLoading(false);
    }
  };

  const getChunkLogs = async (sessionId, chunkIndex) => {
    const chunk = sessionChunks.find((c) => c.chunk_index === chunkIndex);
    if (chunk && chunk.logs_json) {
      return chunk.logs_json;
    }
    const indexedDBChunk = await chunkCache.getChunk(sessionId, chunkIndex);
    return indexedDBChunk?.logs_json || indexedDBChunk;
  };

  const handleBulkAnalyze = async () => {
    if (!selectedSession) return;

    const chunksToAnalyze = Math.min(maxChunks, selectedSession.total_chunks);

    if (
      !confirm(
        `Analyze ${chunksToAnalyze} chunks in session "${selectedSession.session_id}"?\n\nThis may take several minutes.`,
      )
    ) {
      return;
    }

    try {
      setAnalyzing(true);
      setProgress({ current: 0, total: chunksToAnalyze });
      setSessionReport(null);

      console.log(
        `[Bulk Analysis] Starting analysis of ${chunksToAnalyze} chunks`,
      );

      const results = [];
      const updatedChunks = [...sessionChunks];

      for (let i = 0; i < chunksToAnalyze; i++) {
        try {
          console.log(
            `[Bulk Analysis] Analyzing chunk ${i} (${i + 1}/${chunksToAnalyze})`,
          );
          setProgress({ current: i + 1, total: chunksToAnalyze });

          const chunkLogs = await getChunkLogs(selectedSession.session_id, i);

          if (!chunkLogs) {
            console.warn(`[Bulk Analysis] Skipping chunk ${i} - no data`);
            continue;
          }

          const result = await sessionService.analyzeChunk(
            selectedSession.session_id,
            i,
            JSON.stringify(chunkLogs),
          );

          results.push(result);

          // Update the chunk in local state
          const chunkIndex = updatedChunks.findIndex(
            (c) => c.chunk_index === i,
          );
          if (chunkIndex !== -1) {
            updatedChunks[chunkIndex] = {
              ...updatedChunks[chunkIndex],
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
            };
          }
        } catch (err) {
          console.error(`[Bulk Analysis] Error analyzing chunk ${i}:`, err);
        }
      }

      setSessionChunks(updatedChunks);

      // Calculate session report
      const normalCount = results.filter(
        (r) => r.status.toLowerCase() === "normal",
      ).length;
      const suspiciousCount = results.filter(
        (r) => r.status.toLowerCase() === "suspicious",
      ).length;
      const totalAnalyzed = results.length;
      const normalPercentage = (normalCount / totalAnalyzed) * 100;

      const sessionStatus = normalPercentage >= 95 ? "Normal" : "Suspicious";

      // Calculate total processing time
      const totalProcessingTime = results.reduce(
        (sum, r) => sum + (r.processing_time_ms || 0),
        0,
      );

      // Extract all MITRE techniques
      const allMitreTechniques = new Set();
      results.forEach((r) => {
        if (r.mitre_techniques) {
          r.mitre_techniques.forEach((t) => allMitreTechniques.add(t));
        }
      });

      setSessionReport({
        status: sessionStatus,
        normalCount,
        suspiciousCount,
        totalAnalyzed,
        normalPercentage: normalPercentage.toFixed(1),
        totalProcessingTime: (totalProcessingTime / 1000).toFixed(2), // Convert to seconds
        mitreTechniques: Array.from(allMitreTechniques),
        analyzedAt: new Date().toISOString(),
      });

      console.log(
        `[Bulk Analysis] Complete: ${normalCount}/${totalAnalyzed} normal (${normalPercentage.toFixed(1)}%) → ${sessionStatus}`,
      );
    } catch (err) {
      console.error("[Bulk Analysis] Fatal error:", err);
      alert(`Bulk analysis failed: ${err.message}`);
    } finally {
      setAnalyzing(false);
      setProgress({ current: 0, total: 0 });
    }
  };

  return (
    <div className="space-y-6">
      <div className="card">
        <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-2 flex items-center gap-2">
          <Shield className="w-7 h-7 text-primary-600 dark:text-primary-400" />
          Bulk Session Analyzer
        </h2>
        <p className="text-sm text-gray-600 dark:text-gray-400">
          Analyze entire sessions at once and generate comprehensive security
          reports
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Session List */}
        <div className="lg:col-span-1">
          <div className="card">
            <h3 className="text-lg font-bold text-gray-900 dark:text-white mb-4 flex items-center gap-2">
              <FolderOpen className="w-5 h-5 text-primary-600 dark:text-primary-400" />
              Select Session
            </h3>

            {loading && !selectedSession ? (
              <div className="flex items-center justify-center py-8">
                <Loader2 className="w-8 h-8 text-primary-600 dark:text-primary-400 animate-spin" />
              </div>
            ) : sessions.length === 0 ? (
              <div className="text-center py-8">
                <FolderOpen className="w-12 h-12 text-gray-300 dark:text-gray-600 mx-auto mb-3" />
                <p className="text-gray-500 dark:text-gray-400 text-sm">
                  No sessions available
                </p>
              </div>
            ) : (
              <div className="space-y-2 max-h-96 overflow-y-auto">
                {sessions.map((session) => (
                  <div
                    key={session.session_id}
                    onClick={() => handleSelectSession(session)}
                    className={`p-3 rounded-lg border cursor-pointer transition-colors ${
                      selectedSession?.session_id === session.session_id
                        ? "bg-blue-100 dark:bg-blue-900/40 border-blue-300 dark:border-blue-600"
                        : "bg-gray-50 dark:bg-gray-800/50 border-gray-200 dark:border-gray-700 hover:bg-gray-100 dark:hover:bg-gray-700/50"
                    }`}
                  >
                    <div className="flex items-start justify-between gap-2 mb-2">
                      <h4 className="text-sm font-semibold text-gray-900 dark:text-white truncate flex-1">
                        {session.session_name || session.session_id}
                      </h4>
                    </div>
                    <div className="flex items-center gap-3 text-xs text-gray-600 dark:text-gray-400">
                      <div className="flex items-center gap-1">
                        <Layers className="w-3 h-3" />
                        <span>{session.total_chunks} chunks</span>
                      </div>
                      {(session.created_at || session.uploaded_at) && (
                        <span className="text-gray-500 dark:text-gray-500">
                          {new Date(
                            session.created_at || session.uploaded_at,
                          ).toLocaleDateString()}
                        </span>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>

        {/* Analysis Panel */}
        <div className="lg:col-span-2">
          {!selectedSession ? (
            <div className="card flex items-center justify-center h-96">
              <div className="text-center">
                <FolderOpen className="w-16 h-16 text-gray-300 dark:text-gray-600 mx-auto mb-4" />
                <p className="text-gray-500 dark:text-gray-400">
                  Select a session to begin bulk analysis
                </p>
              </div>
            </div>
          ) : (
            <div className="space-y-4">
              {/* Session Info & Controls */}
              <div className="card">
                <div className="flex items-start justify-between mb-4">
                  <div>
                    <h3 className="text-lg font-bold text-gray-900 dark:text-white">
                      {selectedSession.metadata?.session_name ||
                        selectedSession.session_id}
                    </h3>
                    <p className="text-sm text-gray-600 dark:text-gray-400 font-mono">
                      {selectedSession.session_id}
                    </p>
                  </div>
                </div>

                {/* Analysis Controls */}
                <div className="space-y-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                      Number of chunks to analyze
                    </label>
                    <div className="flex items-center gap-2">
                      <input
                        type="number"
                        min="1"
                        max={selectedSession.total_chunks}
                        value={maxChunks}
                        onChange={(e) =>
                          setMaxChunks(
                            Math.min(
                              Math.max(1, parseInt(e.target.value) || 1),
                              selectedSession.total_chunks,
                            ),
                          )
                        }
                        disabled={analyzing}
                        className="flex-1 px-3 py-2 bg-white dark:bg-gray-800 border border-gray-300 dark:border-gray-600 rounded-lg text-gray-900 dark:text-white focus:ring-2 focus:ring-primary-500 disabled:opacity-50"
                      />
                      <span className="text-sm text-gray-600 dark:text-gray-400">
                        / {selectedSession.total_chunks} chunks
                      </span>
                    </div>
                  </div>

                  <button
                    onClick={handleBulkAnalyze}
                    disabled={analyzing || loading}
                    className="w-full btn btn-primary py-3 text-base disabled:opacity-50"
                  >
                    {analyzing ? (
                      <>
                        <Loader2 className="w-5 h-5 animate-spin" />
                        Analyzing {progress.current}/{progress.total}...
                      </>
                    ) : (
                      <>
                        <Shield className="w-5 h-5" />
                        Analyze Session
                      </>
                    )}
                  </button>
                </div>

                {/* Progress Bar */}
                {analyzing && (
                  <div className="mt-4 p-4 bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-lg">
                    <div className="flex items-center justify-between mb-2">
                      <span className="text-sm font-medium text-blue-900 dark:text-blue-300">
                        Analyzing chunks...
                      </span>
                      <span className="text-sm text-blue-700 dark:text-blue-400">
                        {progress.current} / {progress.total}
                      </span>
                    </div>
                    <div className="w-full bg-blue-200 dark:bg-blue-900/50 rounded-full h-2">
                      <div
                        className="bg-blue-600 dark:bg-blue-500 h-2 rounded-full transition-all duration-300"
                        style={{
                          width: `${(progress.current / progress.total) * 100}%`,
                        }}
                      />
                    </div>
                  </div>
                )}
              </div>

              {/* Session Report */}
              {sessionReport && (
                <div className="card">
                  <h4 className="text-lg font-bold text-gray-900 dark:text-white mb-4">
                    Analysis Report
                  </h4>

                  {/* Overall Status */}
                  <div
                    className={`p-4 rounded-lg border mb-4 ${
                      sessionReport.status === "Normal"
                        ? "bg-green-50 dark:bg-green-900/20 border-green-200 dark:border-green-800"
                        : "bg-red-50 dark:bg-red-900/20 border-red-200 dark:border-red-800"
                    }`}
                  >
                    <div className="flex items-center gap-3">
                      {sessionReport.status === "Normal" ? (
                        <CheckCircle className="w-8 h-8 text-green-600 dark:text-green-400" />
                      ) : (
                        <AlertTriangle className="w-8 h-8 text-red-600 dark:text-red-400" />
                      )}
                      <div className="flex-1">
                        <p
                          className={`text-xl font-bold ${
                            sessionReport.status === "Normal"
                              ? "text-green-900 dark:text-green-300"
                              : "text-red-900 dark:text-red-300"
                          }`}
                        >
                          Session Status: {sessionReport.status}
                        </p>
                        <p
                          className={`text-sm ${
                            sessionReport.status === "Normal"
                              ? "text-green-700 dark:text-green-400"
                              : "text-red-700 dark:text-red-400"
                          }`}
                        >
                          {sessionReport.normalPercentage}% of chunks are normal
                          ({sessionReport.normalCount}/
                          {sessionReport.totalAnalyzed})
                        </p>
                      </div>
                    </div>
                  </div>

                  {/* Statistics Grid */}
                  <div className="grid grid-cols-2 gap-4 mb-4">
                    <div className="p-3 bg-green-50 dark:bg-green-900/20 rounded-lg border border-green-200 dark:border-green-800">
                      <p className="text-xs text-green-700 dark:text-green-400 mb-1">
                        Normal Chunks
                      </p>
                      <p className="text-2xl font-bold text-green-900 dark:text-green-300">
                        {sessionReport.normalCount}
                      </p>
                    </div>
                    <div className="p-3 bg-red-50 dark:bg-red-900/20 rounded-lg border border-red-200 dark:border-red-800">
                      <p className="text-xs text-red-700 dark:text-red-400 mb-1">
                        Suspicious Chunks
                      </p>
                      <p className="text-2xl font-bold text-red-900 dark:text-red-300">
                        {sessionReport.suspiciousCount}
                      </p>
                    </div>
                    <div className="p-3 bg-blue-50 dark:bg-blue-900/20 rounded-lg border border-blue-200 dark:border-blue-800">
                      <p className="text-xs text-blue-700 dark:text-blue-400 mb-1">
                        Total Analyzed
                      </p>
                      <p className="text-2xl font-bold text-blue-900 dark:text-blue-300">
                        {sessionReport.totalAnalyzed}
                      </p>
                    </div>
                    <div className="p-3 bg-purple-50 dark:bg-purple-900/20 rounded-lg border border-purple-200 dark:border-purple-800">
                      <p className="text-xs text-purple-700 dark:text-purple-400 mb-1">
                        Processing Time
                      </p>
                      <p className="text-2xl font-bold text-purple-900 dark:text-purple-300">
                        {sessionReport.totalProcessingTime}s
                      </p>
                    </div>
                  </div>

                  {/* MITRE Techniques */}
                  {sessionReport.mitreTechniques.length > 0 && (
                    <div className="mb-4">
                      <h5 className="text-sm font-semibold text-gray-900 dark:text-white mb-2">
                        Detected MITRE ATT&CK Techniques
                      </h5>
                      <div className="flex flex-wrap gap-2">
                        {sessionReport.mitreTechniques.map((technique) => (
                          <span
                            key={technique}
                            className="px-2 py-1 text-xs font-mono bg-orange-100 dark:bg-orange-900/30 text-orange-700 dark:text-orange-400 rounded border border-orange-200 dark:border-orange-800"
                          >
                            {technique}
                          </span>
                        ))}
                      </div>
                    </div>
                  )}

                  <p className="text-xs text-gray-500 dark:text-gray-400">
                    Report generated at{" "}
                    {new Date(sessionReport.analyzedAt).toLocaleString()}
                  </p>
                </div>
              )}

              {/* Chunks Details (Read-only) */}
              {sessionChunks.length > 0 && (
                <div className="card">
                  <button
                    onClick={() => setExpandedChunks(!expandedChunks)}
                    className="w-full flex items-center justify-between text-left"
                  >
                    <h4 className="text-md font-bold text-gray-900 dark:text-white flex items-center gap-2">
                      <Layers className="w-5 h-5 text-primary-600 dark:text-primary-400" />
                      Chunk Details ({sessionChunks.length} chunks)
                    </h4>
                    {expandedChunks ? (
                      <ChevronUp className="w-5 h-5 text-gray-500" />
                    ) : (
                      <ChevronDown className="w-5 h-5 text-gray-500" />
                    )}
                  </button>

                  {expandedChunks && (
                    <div className="mt-4 space-y-2 max-h-96 overflow-y-auto">
                      {sessionChunks.map((chunk) => (
                        <div
                          key={chunk.chunk_id || chunk.id}
                          className="p-3 bg-gray-50 dark:bg-gray-800/50 rounded-lg border border-gray-200 dark:border-gray-700"
                        >
                          <div className="flex items-center justify-between">
                            <div className="flex-1">
                              <div className="flex items-center gap-2 mb-1">
                                <span className="text-sm font-semibold text-gray-900 dark:text-white">
                                  Chunk {chunk.chunk_index}
                                </span>
                                {chunk.analysis_status && (
                                  <span
                                    className={`inline-flex items-center gap-1 px-2 py-0.5 text-xs font-medium rounded-full ${
                                      chunk.analysis_status.toLowerCase() ===
                                      "normal"
                                        ? "bg-green-100 dark:bg-green-900/30 text-green-700 dark:text-green-400 border border-green-200 dark:border-green-700"
                                        : "bg-red-100 dark:bg-red-900/30 text-red-700 dark:text-red-400 border border-red-200 dark:border-red-700"
                                    }`}
                                  >
                                    {chunk.analysis_status.toLowerCase() ===
                                    "normal" ? (
                                      <CheckCircle className="w-3 h-3" />
                                    ) : (
                                      <AlertTriangle className="w-3 h-3" />
                                    )}
                                    {chunk.analysis_status}
                                  </span>
                                )}
                              </div>
                              <div className="text-xs text-gray-600 dark:text-gray-400">
                                {chunk.chunk_size ||
                                  chunk.logs_json?.length ||
                                  chunk.metadata?.number_of_events ||
                                  0}{" "}
                                logs
                                {chunk.analysis_result?.reason && (
                                  <span className="ml-2 text-gray-500 dark:text-gray-500">
                                    • {chunk.analysis_result.reason}
                                  </span>
                                )}
                              </div>
                            </div>
                          </div>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
