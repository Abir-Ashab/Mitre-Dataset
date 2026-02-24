import {
  CheckCircle,
  AlertTriangle,
  HelpCircle,
  Clock,
  Hash,
} from "lucide-react";

export default function AnalysisResult({ result }) {
  if (!result) {
    return null;
  }

  const getStatusBadge = (status) => {
    switch ((status || "").toLowerCase()) {
      case "normal":
        return (
          <span className="badge badge-success flex items-center gap-1">
            <CheckCircle className="w-4 h-4" />
            Normal
          </span>
        );
      case "suspicious":
        return (
          <span className="badge badge-danger flex items-center gap-1">
            <AlertTriangle className="w-4 h-4" />
            Suspicious
          </span>
        );
      case "unknown":
        return (
          <span className="badge badge-warning flex items-center gap-1">
            <HelpCircle className="w-4 h-4" />
            Unknown
          </span>
        );
      default:
        return (
          <span className="badge badge-gray flex items-center gap-1">
            {status}
          </span>
        );
    }
  };

  return (
    <div className="card space-y-6">
      <div className="flex items-center justify-between">
        <h3 className="text-xl font-bold text-gray-900 dark:text-white">
          Analysis Results
        </h3>
        {result?.status && getStatusBadge(result.status)}
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div className="bg-gray-50 dark:bg-gray-900 rounded-lg p-4">
          <div className="flex items-center gap-2 text-gray-600 dark:text-gray-400 mb-1">
            <Hash className="w-4 h-4" />
            <span className="text-xs font-medium">Analysis ID</span>
          </div>
          <p className="text-sm font-mono text-gray-900 dark:text-gray-100 break-all">
            {result?.analysis_id || "N/A"}
          </p>
        </div>

        <div className="bg-gray-50 dark:bg-gray-900 rounded-lg p-4">
          <div className="flex items-center gap-2 text-gray-600 dark:text-gray-400 mb-1">
            <Clock className="w-4 h-4" />
            <span className="text-xs font-medium">Processing Time</span>
          </div>
          <p className="text-sm font-semibold text-gray-900 dark:text-gray-100">
            {result?.processing_time_ms
              ? (result.processing_time_ms / 1000).toFixed(2)
              : "0.00"}
            s
          </p>
        </div>
      </div>

      {/* Reason */}
      <div>
        <h4 className="text-sm font-semibold text-gray-700 dark:text-gray-300 mb-2">
          Reason
        </h4>
        <div className="bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-lg p-4">
          <p className="text-gray-900 dark:text-gray-100">
            {result?.reason || "No reason provided"}
          </p>
        </div>
      </div>

      {/* MITRE Techniques */}
      {result?.mitre_techniques && result.mitre_techniques.length > 0 && (
        <div>
          <h4 className="text-sm font-semibold text-gray-700 dark:text-gray-300 mb-2">
            MITRE ATT&CK Techniques
          </h4>
          <div className="flex flex-wrap gap-2">
            {result.mitre_techniques.map((technique, index) => (
              <a
                key={index}
                href={`https://attack.mitre.org/techniques/${technique.replace(".", "/")}/`}
                target="_blank"
                rel="noopener noreferrer"
                className="px-3 py-1.5 bg-danger-100 dark:bg-danger-900/30 text-danger-700 dark:text-danger-400 rounded-lg text-sm font-medium hover:bg-danger-200 dark:hover:bg-danger-900/50 transition-colors"
              >
                {technique}
              </a>
            ))}
          </div>
        </div>
      )}

      {/* Raw Model Output */}
      {result?.raw_output && (
        <details className="group">
          <summary className="cursor-pointer text-sm font-semibold text-gray-700 dark:text-gray-300 hover:text-gray-900 dark:hover:text-gray-100">
            View Raw Model Output
          </summary>
          <div className="mt-2 bg-gray-900 dark:bg-black rounded-lg p-4 overflow-x-auto">
            <pre className="text-xs text-green-400 dark:text-green-500 font-mono whitespace-pre-wrap">
              {result.raw_output}
            </pre>
          </div>
        </details>
      )}

      {/* Timestamp */}
      {result?.analyzed_at && (
        <div className="text-xs text-gray-500 dark:text-gray-400 border-t dark:border-gray-700 pt-3">
          Analyzed at: {new Date(result.analyzed_at).toLocaleString()}
        </div>
      )}
    </div>
  );
}
