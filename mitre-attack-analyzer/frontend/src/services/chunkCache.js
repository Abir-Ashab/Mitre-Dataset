/**
 * IndexedDB wrapper for storing session chunks locally
 * This provides fast local caching without database overhead
 */

const DB_NAME = "mitre_analyzer_cache";
const DB_VERSION = 1;
const STORE_NAME = "session_chunks";

class ChunkCacheDB {
  constructor() {
    this.db = null;
  }

  /**
   * Initialize IndexedDB
   */
  async init() {
    return new Promise((resolve, reject) => {
      const request = indexedDB.open(DB_NAME, DB_VERSION);

      request.onerror = () => reject(request.error);
      request.onsuccess = () => {
        this.db = request.result;
        resolve(this.db);
      };

      request.onupgradeneeded = (event) => {
        const db = event.target.result;

        // Create object store if it doesn't exist
        if (!db.objectStoreNames.contains(STORE_NAME)) {
          const objectStore = db.createObjectStore(STORE_NAME, {
            keyPath: "id",
          });

          // Create indexes for efficient querying
          objectStore.createIndex("session_id", "session_id", {
            unique: false,
          });
          objectStore.createIndex("chunk_index", "chunk_index", {
            unique: false,
          });
          objectStore.createIndex("created_at", "created_at", {
            unique: false,
          });
        }
      };
    });
  }

  /**
   * Store an entire session with all chunks
   */
  async storeSession(sessionId, chunks, metadata = {}) {
    await this.init();
    const transaction = this.db.transaction([STORE_NAME], "readwrite");
    const objectStore = transaction.objectStore(STORE_NAME);

    const promises = chunks.map((chunk, index) => {
      return new Promise((resolve, reject) => {
        const request = objectStore.put({
          id: `${sessionId}_${index}`,
          session_id: sessionId,
          chunk_index: index,
          logs_json: chunk.logs_json || chunk,
          metadata: chunk.metadata || metadata,
          created_at: new Date().toISOString(),
        });
        request.onsuccess = () => resolve();
        request.onerror = () => reject(request.error);
      });
    });

    await Promise.all(promises);
    return chunks.length;
  }

  /**
   * Get all chunks for a session
   */
  async getSessionChunks(sessionId, skip = 0, limit = 50) {
    await this.init();
    return new Promise((resolve, reject) => {
      const transaction = this.db.transaction([STORE_NAME], "readonly");
      const objectStore = transaction.objectStore(STORE_NAME);
      const index = objectStore.index("session_id");
      const request = index.getAll(sessionId);

      request.onsuccess = () => {
        const allChunks = request.result;
        // Sort by chunk_index
        allChunks.sort((a, b) => a.chunk_index - b.chunk_index);

        // Apply pagination
        const paginatedChunks = allChunks.slice(skip, skip + limit);

        resolve({
          chunks: paginatedChunks,
          total: allChunks.length,
        });
      };
      request.onerror = () => reject(request.error);
    });
  }

  /**
   * Get a specific chunk
   */
  async getChunk(sessionId, chunkIndex) {
    await this.init();
    return new Promise((resolve, reject) => {
      const transaction = this.db.transaction([STORE_NAME], "readonly");
      const objectStore = transaction.objectStore(STORE_NAME);
      const request = objectStore.get(`${sessionId}_${chunkIndex}`);

      request.onsuccess = () => resolve(request.result);
      request.onerror = () => reject(request.error);
    });
  }

  /**
   * Get all session IDs with chunk counts
   */
  async getAllSessions() {
    await this.init();
    return new Promise((resolve, reject) => {
      const transaction = this.db.transaction([STORE_NAME], "readonly");
      const objectStore = transaction.objectStore(STORE_NAME);
      const request = objectStore.getAll();

      request.onsuccess = () => {
        const allChunks = request.result;

        // Group by session_id
        const sessionMap = {};
        allChunks.forEach((chunk) => {
          if (!sessionMap[chunk.session_id]) {
            sessionMap[chunk.session_id] = {
              session_id: chunk.session_id,
              total_chunks: 0,
              created_at: chunk.created_at,
              metadata: chunk.metadata,
            };
          }
          sessionMap[chunk.session_id].total_chunks++;
        });

        const sessions = Object.values(sessionMap);
        // Sort by created_at desc
        sessions.sort(
          (a, b) => new Date(b.created_at) - new Date(a.created_at),
        );

        resolve(sessions);
      };
      request.onerror = () => reject(request.error);
    });
  }

  /**
   * Delete all chunks for a session
   */
  async deleteSession(sessionId) {
    await this.init();
    const transaction = this.db.transaction([STORE_NAME], "readwrite");
    const objectStore = transaction.objectStore(STORE_NAME);
    const index = objectStore.index("session_id");

    return new Promise((resolve, reject) => {
      const request = index.openCursor(sessionId);

      request.onsuccess = (event) => {
        const cursor = event.target.result;
        if (cursor) {
          cursor.delete();
          cursor.continue();
        } else {
          resolve();
        }
      };
      request.onerror = () => reject(request.error);
    });
  }

  /**
   * Check if a session exists
   */
  async sessionExists(sessionId) {
    await this.init();
    return new Promise((resolve, reject) => {
      const transaction = this.db.transaction([STORE_NAME], "readonly");
      const objectStore = transaction.objectStore(STORE_NAME);
      const index = objectStore.index("session_id");
      const request = index.count(sessionId);

      request.onsuccess = () => resolve(request.result > 0);
      request.onerror = () => reject(request.error);
    });
  }

  /**
   * Get total storage size estimate
   */
  async getStorageEstimate() {
    if (navigator.storage && navigator.storage.estimate) {
      return await navigator.storage.estimate();
    }
    return null;
  }

  /**
   * Clear all data
   */
  async clearAll() {
    await this.init();
    return new Promise((resolve, reject) => {
      const transaction = this.db.transaction([STORE_NAME], "readwrite");
      const objectStore = transaction.objectStore(STORE_NAME);
      const request = objectStore.clear();

      request.onsuccess = () => resolve();
      request.onerror = () => reject(request.error);
    });
  }
}

// Export singleton instance
export const chunkCache = new ChunkCacheDB();
