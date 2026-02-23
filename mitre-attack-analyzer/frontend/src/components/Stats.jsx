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
        <Loader2 className="w-8 h-8 text-primary-600 animate-spin" />
      </div>
    );
  }

  if (error) {
    return (
      <div className="card">
        <p className="text-danger-600 text-sm">{error}</p>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      <div className="card">
        <h3 className="text-lg font-bold text-gray-900 mb-4 flex items-center gap-2">
          <BarChart3 className="w-5 h-5 text-primary-600" />
          Statistics
        </h3>

        <div className="space-y-4">
          {/* Total Analyses */}
          <div className="bg-gradient-to-br from-primary-50 to-primary-100 rounded-lg p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-primary-700 font-medium">
                  Total Analyses
                </p>
                <p className="text-3xl font-bold text-primary-900 mt-1">
                  {stats.total_analyses}
                </p>
              </div>
              <Activity className="w-10 h-10 text-primary-600 opacity-50" />
            </div>
          </div>

          {/* Status Breakdown */}
          <div className="space-y-2">
            <div className="flex items-center justify-between py-2 border-b border-gray-200">
              <span className="text-sm text-gray-700 flex items-center gap-2">
                <span className="w-3 h-3 bg-success-500 rounded-full"></span>
                Normal
              </span>
              <span className="text-sm font-bold text-gray-900">
                {stats.by_status.normal || 0}
              </span>
            </div>

            <div className="flex items-center justify-between py-2 border-b border-gray-200">
              <span className="text-sm text-gray-700 flex items-center gap-2">
                <span className="w-3 h-3 bg-danger-500 rounded-full"></span>
                Suspicious
              </span>
              <span className="text-sm font-bold text-gray-900">
                {stats.by_status.suspicious || 0}
              </span>
            </div>

            <div className="flex items-center justify-between py-2 border-b border-gray-200">
              <span className="text-sm text-gray-700 flex items-center gap-2">
                <span className="w-3 h-3 bg-yellow-500 rounded-full"></span>
                Unknown
              </span>
              <span className="text-sm font-bold text-gray-900">
                {stats.by_status.unknown || 0}
              </span>
            </div>

            <div className="flex items-center justify-between py-2">
              <span className="text-sm text-gray-700 flex items-center gap-2">
                <span className="w-3 h-3 bg-gray-500 rounded-full"></span>
                Error
              </span>
              <span className="text-sm font-bold text-gray-900">
                {stats.by_status.error || 0}
              </span>
            </div>
          </div>

          {/* Suspicious Rate */}
          {stats.total_analyses > 0 && (
            <div className="bg-orange-50 border border-orange-200 rounded-lg p-3">
              <div className="flex items-center gap-2 mb-1">
                <TrendingUp className="w-4 h-4 text-orange-600" />
                <span className="text-xs font-medium text-orange-700">
                  Suspicious Rate
                </span>
              </div>
              <p className="text-2xl font-bold text-orange-900">
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
