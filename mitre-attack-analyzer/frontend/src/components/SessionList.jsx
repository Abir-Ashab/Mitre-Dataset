import { useState, useEffect } from "react";
import {
  FolderOpen,
  ChevronRight,
  Trash2,
  Loader2,
  RefreshCw,
  ChevronLeft,
} from "lucide-react";
import { chunkCache } from "../services/chunkCache";
import { sessionService } from "../services/api";

export default function SessionList({ onSelectSession }) {
  const [sessions, setSessions] = useState([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [deleting, setDeleting] = useState(null);

  const ITEMS_PER_PAGE = 10;
  const totalPages = Math.ceil(total / ITEMS_PER_PAGE);

  useEffect(() => {
    fetchSessions();
  }, [page]);

  const fetchSessions = async (forceRefresh = false) => {
    try {
      setLoading(true);
      const startTime = performance.now();

      
      if (!forceRefresh) {
        try {
          const cached = localStorage.getItem("sessions_cache");
          const cacheTimestamp = localStorage.getItem(
            "sessions_cache_timestamp",
          );

          if (cached && cacheTimestamp) {
            const cacheAge = Date.now() - parseInt(cacheTimestamp);
            const CACHE_DURATION = 5 * 60 * 1000; 

            
            if (cacheAge < CACHE_DURATION) {
              const cachedData = JSON.parse(cached);
              console.log(
                `[Sessions] ✅ Loaded from cache (${(cacheAge / 1000).toFixed(0)}s old, ${cachedData.length} sessions)`,
              );

              const skip = (page - 1) * ITEMS_PER_PAGE;
              const paginatedSessions = cachedData.slice(
                skip,
                skip + ITEMS_PER_PAGE,
              );

              setSessions(paginatedSessions);
              setTotal(cachedData.length);
              setError(null);
              setLoading(false);
              return;
            } else {
              console.log(
                `[Sessions] Cache expired (${(cacheAge / 1000).toFixed(0)}s old), fetching fresh data...`,
              );
            }
          }
        } catch (cacheError) {
          console.log("[Sessions] Cache miss or error, fetching from DB");
        }
      } else {
        console.log("[Sessions] Force refresh requested, clearing cache...");
        localStorage.removeItem("sessions_cache");
        localStorage.removeItem("sessions_cache_timestamp");
      }

      
      console.log("[Sessions] Fetching from MongoDB...");
      const mongoStart = performance.now();
      const mongoDBResponse = await sessionService.getAllSessions(0, 100); 
      const mongoTime = performance.now() - mongoStart;
      console.log(
        `[Sessions] ✅ MongoDB fetch completed in ${mongoTime.toFixed(2)}ms`,
      );

      const mongoDBSessions = (mongoDBResponse.sessions || []).map((s) => ({
        ...s,
        source: "mongodb",
      }));

      
      try {
        localStorage.setItem("sessions_cache", JSON.stringify(mongoDBSessions));
        localStorage.setItem("sessions_cache_timestamp", Date.now().toString());
        console.log(
          `[Sessions] ✅ Cached ${mongoDBSessions.length} sessions in localStorage`,
        );
      } catch (storageError) {
        console.warn("[Sessions] Failed to cache sessions:", storageError);
      }

      
      const skip = (page - 1) * ITEMS_PER_PAGE;
      const paginatedSessions = mongoDBSessions.slice(
        skip,
        skip + ITEMS_PER_PAGE,
      );

      const totalTime = performance.now() - startTime;
      console.log(
        `[Sessions] ✅ Total time: ${totalTime.toFixed(2)}ms (${mongoDBSessions.length} sessions loaded, ${mongoDBResponse.total} total)`,
      );

      setSessions(paginatedSessions);
      setTotal(mongoDBResponse.total || mongoDBSessions.length); 
      setError(null);
    } catch (err) {
      setError("Failed to load sessions");
      console.error("Sessions error:", err);
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (sessionId, e) => {
    e.stopPropagation();

    if (!confirm(`Delete session "${sessionId}" and all its chunks?`)) {
      return;
    }

    try {
      setDeleting(sessionId);

      
      await sessionService.deleteSession(sessionId);

      
      localStorage.removeItem("sessions_cache");
      localStorage.removeItem("sessions_cache_timestamp");
      console.log("[Sessions] Cache cleared after deletion");

      await fetchSessions(true); 
    } catch (err) {
      console.error("Delete error:", err);
      alert("Failed to delete session");
    } finally {
      setDeleting(null);
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
        <p className="text-danger-600 dark:text-danger-400 text-sm">{error}</p>
      </div>
    );
  }

  return (
    <div className="card">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-bold text-gray-900 dark:text-white flex items-center gap-2">
          <FolderOpen className="w-5 h-5 text-primary-600 dark:text-primary-400" />
          Uploaded Sessions
        </h3>
        <button
          onClick={() => fetchSessions(true)}
          className="btn btn-secondary text-xs py-1 px-3"
          title="Refresh from database"
        >
          <RefreshCw className="w-3 h-3" />
          Refresh
        </button>
      </div>

      {sessions.length === 0 ? (
        <div className="text-center py-12">
          <FolderOpen className="w-16 h-16 text-gray-300 dark:text-gray-600 mx-auto mb-4" />
          <p className="text-gray-500 dark:text-gray-400 text-sm">
            No sessions uploaded yet
          </p>
          <p className="text-gray-400 dark:text-gray-500 text-xs mt-1">
            Upload a session log file to get started
          </p>
        </div>
      ) : (
        <div className="space-y-2">
          {sessions.map((session) => (
            <div
              key={session.session_id}
              onClick={() =>
                onSelectSession && onSelectSession(session.session_id)
              }
              className="flex items-center justify-between p-3 bg-gray-50 dark:bg-gray-800/50 hover:bg-gray-100 dark:hover:bg-gray-700/50 rounded-lg border border-gray-200 dark:border-gray-700 cursor-pointer transition-colors group"
            >
              <div className="flex-1">
                <div className="flex items-center gap-2">
                  <h4 className="text-sm font-semibold text-gray-900 dark:text-white">
                    {session.session_name || session.session_id}
                  </h4>
                  <span className="text-xs text-gray-500 dark:text-gray-400 font-mono">
                    {session.session_id}
                  </span>
                </div>
                <div className="flex items-center gap-4 mt-1 text-xs text-gray-600 dark:text-gray-400">
                  <span>{session.total_chunks} chunks</span>
                  {(session.created_at || session.uploaded_at) && (
                    <span className="text-gray-500 dark:text-gray-500">
                      {new Date(
                        session.created_at || session.uploaded_at,
                      ).toLocaleString()}
                    </span>
                  )}
                </div>
              </div>
              <div className="flex items-center gap-2">
                <button
                  onClick={(e) => handleDelete(session.session_id, e)}
                  disabled={deleting === session.session_id}
                  className="p-2 text-red-600 dark:text-red-400 hover:bg-red-50 dark:hover:bg-red-900/20 rounded-lg transition-colors"
                  title="Delete session"
                >
                  {deleting === session.session_id ? (
                    <Loader2 className="w-4 h-4 animate-spin" />
                  ) : (
                    <Trash2 className="w-4 h-4" />
                  )}
                </button>
                <ChevronRight className="w-5 h-5 text-gray-400 dark:text-gray-500 group-hover:text-primary-600 dark:group-hover:text-primary-400" />
              </div>
            </div>
          ))}
        </div>
      )}

      {totalPages > 1 && (
        <div className="flex items-center justify-between mt-4 pt-4 border-t border-gray-200 dark:border-gray-700">
          <div className="text-sm text-gray-600 dark:text-gray-400">
            Showing {(page - 1) * ITEMS_PER_PAGE + 1} to{" "}
            {Math.min(page * ITEMS_PER_PAGE, total)} of {total} sessions
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
                  
                  return p === 1 || p === totalPages || Math.abs(p - page) <= 1;
                })
                .map((p, idx, arr) => {
                  
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
  );
}
