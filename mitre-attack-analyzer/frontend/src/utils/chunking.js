/**
 * Client-side log chunking utility
 * Matches the backend chunking logic for consistency
 */

const CHUNK_SIZE = 7;
const MIN_CHUNK_SIZE = 5;

/**
 * Parse timestamp from log entry
 */
function getTimestamp(log) {
  if (log.timestamp) return log.timestamp;
  if (log.TimeCreated?.SystemTime) return log.TimeCreated.SystemTime;
  if (log["@timestamp"]) return log["@timestamp"];
  if (log.time) return log.time;
  return "unknown";
}

/**
 * Parse session log JSON and split into chunks
 */
export function chunkSessionLogs(logsJson) {
  try {
    const data = typeof logsJson === "string" ? JSON.parse(logsJson) : logsJson;

    // Handle array of logs directly
    let logs = Array.isArray(data) ? data : data.logs || data.events || [];

    if (!Array.isArray(logs) || logs.length === 0) {
      throw new Error("No logs found in file. Expected array of log entries.");
    }

    // Sort by timestamp
    logs.sort((a, b) => {
      const timeA = getTimestamp(a);
      const timeB = getTimestamp(b);
      if (timeA === "unknown" || timeB === "unknown") return 0;
      return new Date(timeA) - new Date(timeB);
    });

    // Create chunks
    const chunks = [];
    for (let i = 0; i < logs.length; i += CHUNK_SIZE) {
      const chunkLogs = logs.slice(i, i + CHUNK_SIZE);

      // Skip chunks smaller than minimum size (except last chunk)
      if (chunkLogs.length < MIN_CHUNK_SIZE && i + CHUNK_SIZE < logs.length) {
        continue;
      }

      const startTime = getTimestamp(chunkLogs[0]);
      const endTime = getTimestamp(chunkLogs[chunkLogs.length - 1]);

      chunks.push({
        chunk_index: chunks.length,
        logs_json: chunkLogs,
        metadata: {
          start_time: startTime,
          end_time: endTime,
          number_of_events: chunkLogs.length,
        },
      });
    }

    return {
      chunks,
      total_logs: logs.length,
      total_chunks: chunks.length,
    };
  } catch (error) {
    throw new Error(`Failed to parse and chunk logs: ${error.message}`);
  }
}

/**
 * Generate session ID from filename or timestamp
 */
export function generateSessionId(filename) {
  // Remove extension and clean up
  let sessionId = filename
    .replace(/\.(json|jsonl)$/i, "")
    .replace(/[^a-zA-Z0-9_-]/g, "_");

  // If empty or too short, use timestamp
  if (sessionId.length < 3) {
    const now = new Date();
    sessionId = `session_${now.getFullYear()}${String(now.getMonth() + 1).padStart(2, "0")}${String(now.getDate()).padStart(2, "0")}_${String(now.getHours()).padStart(2, "0")}${String(now.getMinutes()).padStart(2, "0")}${String(now.getSeconds()).padStart(2, "0")}`;
  }

  return sessionId;
}
