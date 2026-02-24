import { useState, useEffect } from "react";
import { BarChart3, TrendingUp, Activity, Loader2 } from "lucide-react";
import { logService } from "../services/api";

export default function Stats() {
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchStats();
  }, []);

  const fetchStats = async () => {
    try {
      setLoading(true);
      const data = await logService.getStats();
      setStats(data);
    } catch (err) {
      setError("Failed to load statistics");
      console.error("Stats error:", err);
    } finally {
      setLoading(false);
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
    <div className="space-y-4">
      <div className="card">
        <h3 className="text-lg font-bold text-gray-900 dark:text-white mb-4 flex items-center gap-2">
          <BarChart3 className="w-5 h-5 text-primary-600 dark:text-primary-400" />
          Statistics
        </h3>

        <div className="space-y-4">
          {/* Total Analyses */}
          <div className="bg-gradient-to-br from-primary-500 to-primary-600 dark:from-primary-600 dark:to-primary-700 rounded-xl p-4 shadow-lg">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-primary-100 dark:text-primary-200 font-medium">
                  Total Analyses
                </p>
                <p className="text-4xl font-bold text-white mt-1">
                  {stats.total_analyses}
                </p>
              </div>
              <Activity className="w-12 h-12 text-white opacity-30" />
            </div>
          </div>

          {/* Status Breakdown */}
          <div className="bg-gray-50 dark:bg-gray-800/50 rounded-lg p-3 space-y-3">
            <div className="flex items-center justify-between py-2 px-3 bg-white dark:bg-gray-700/50 rounded-lg border border-gray-200 dark:border-gray-600">
              <span className="text-sm text-gray-700 dark:text-gray-200 font-medium flex items-center gap-2">
                <span className="w-3 h-3 bg-green-500 dark:bg-green-400 rounded-full shadow-sm shadow-green-500/50"></span>
                Normal
              </span>
              <span className="text-sm font-bold text-gray-900 dark:text-white bg-gray-100 dark:bg-gray-600 px-3 py-1 rounded-full">
                {stats.by_status.normal || 0}
              </span>
            </div>

            <div className="flex items-center justify-between py-2 px-3 bg-white dark:bg-gray-700/50 rounded-lg border border-gray-200 dark:border-gray-600">
              <span className="text-sm text-gray-700 dark:text-gray-200 font-medium flex items-center gap-2">
                <span className="w-3 h-3 bg-red-500 dark:bg-red-400 rounded-full shadow-sm shadow-red-500/50"></span>
                Suspicious
              </span>
              <span className="text-sm font-bold text-gray-900 dark:text-white bg-gray-100 dark:bg-gray-600 px-3 py-1 rounded-full">
                {stats.by_status.suspicious || 0}
              </span>
            </div>

            <div className="flex items-center justify-between py-2 px-3 bg-white dark:bg-gray-700/50 rounded-lg border border-gray-200 dark:border-gray-600">
              <span className="text-sm text-gray-700 dark:text-gray-200 font-medium flex items-center gap-2">
                <span className="w-3 h-3 bg-yellow-500 dark:bg-yellow-400 rounded-full shadow-sm shadow-yellow-500/50"></span>
                Unknown
              </span>
              <span className="text-sm font-bold text-gray-900 dark:text-white bg-gray-100 dark:bg-gray-600 px-3 py-1 rounded-full">
                {stats.by_status.unknown || 0}
              </span>
            </div>

            <div className="flex items-center justify-between py-2 px-3 bg-white dark:bg-gray-700/50 rounded-lg border border-gray-200 dark:border-gray-600">
              <span className="text-sm text-gray-700 dark:text-gray-200 font-medium flex items-center gap-2">
                <span className="w-3 h-3 bg-gray-500 dark:bg-gray-400 rounded-full shadow-sm shadow-gray-500/50"></span>
                Error
              </span>
              <span className="text-sm font-bold text-gray-900 dark:text-white bg-gray-100 dark:bg-gray-600 px-3 py-1 rounded-full">
                {stats.by_status.error || 0}
              </span>
            </div>
          </div>

          {/* Suspicious Rate */}
          {stats.total_analyses > 0 && (
            <div className="bg-gradient-to-br from-orange-500 to-red-500 dark:from-orange-600 dark:to-red-600 rounded-xl p-4 shadow-lg border border-orange-300 dark:border-orange-700">
              <div className="flex items-center gap-2 mb-1">
                <TrendingUp className="w-5 h-5 text-white" />
                <span className="text-sm font-semibold text-white">
                  Suspicious Rate
                </span>
              </div>
              <p className="text-3xl font-bold text-white">
                {(
                  ((stats.by_status.suspicious || 0) / stats.total_analyses) *
                  100
                ).toFixed(1)}
                %
              </p>
            </div>
          )}
        </div>

        <button
          onClick={fetchStats}
          className="btn btn-secondary w-full mt-4 text-sm"
        >
          Refresh Stats
        </button>
      </div>
    </div>
  );
}
