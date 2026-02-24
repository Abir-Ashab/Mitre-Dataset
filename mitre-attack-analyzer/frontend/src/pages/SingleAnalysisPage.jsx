import { useState } from "react";
import LogAnalyzer from "../components/LogAnalyzer";
import Stats from "../components/Stats";

export default function SingleAnalysisPage() {
  const [refreshKey, setRefreshKey] = useState(0);

  const handleAnalysisComplete = () => {
    setRefreshKey((prev) => prev + 1);
  };

  return (
    <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
      <div className="lg:col-span-2">
        <LogAnalyzer onAnalysisComplete={handleAnalysisComplete} />
      </div>
      <div>
        <Stats key={refreshKey} />
      </div>
    </div>
  );
}
