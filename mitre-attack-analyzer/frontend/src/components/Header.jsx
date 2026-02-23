import { Shield, Activity } from "lucide-react";

export default function Header() {
  return (
    <header className="bg-white shadow-sm border-b border-gray-200">
      <div className="container mx-auto px-4 py-6">
        <div className="flex items-center gap-3">
          <div className="bg-primary-600 p-2 rounded-lg">
            <Shield className="w-8 h-8 text-white" />
          </div>
          <div>
            <h1 className="text-2xl font-bold text-gray-900">
              MITRE ATT&CK Log Analyzer
            </h1>
            <p className="text-sm text-gray-600 flex items-center gap-2 mt-1">
              <Activity className="w-4 h-4" />
              AI-Powered Security Log Analysis
            </p>
          </div>
        </div>
      </div>
    </header>
  );
}
