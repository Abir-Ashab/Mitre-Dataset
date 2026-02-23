import { useState } from "react";
import LogAnalyzer from "./components/LogAnalyzer";
import Header from "./components/Header";
import Stats from "./components/Stats";

function App() {
  const [refreshKey, setRefreshKey] = useState(0);

  const handleAnalysisComplete = () => {
    setRefreshKey((prev) => prev + 1);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100">
      <Header />

      <main className="container mx-auto px-4 py-8 max-w-7xl">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-8">
          <div className="lg:col-span-2">
            <LogAnalyzer onAnalysisComplete={handleAnalysisComplete} />
          </div>

          <div>
            <Stats key={refreshKey} />
          </div>
        </div>
      </main>

      <footer className="bg-white border-t border-gray-200 py-6 mt-12">
        <div className="container mx-auto px-4 text-center text-gray-600">
          <p>
            MITRE ATT&CK Log Analyzer • Built with React + FastAPI + MongoDB
          </p>
        </div>
      </footer>
    </div>
  );
}

export default App;
