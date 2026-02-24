import { useState } from "react";
import LogAnalyzer from "./components/LogAnalyzer";
import Header from "./components/Header";
import Stats from "./components/Stats";
import SessionUpload from "./components/SessionUpload";
import SessionList from "./components/SessionList";
import SessionDetails from "./components/SessionDetails";
import { ThemeProvider } from "./contexts/ThemeContext";
import { FileText, FolderOpen } from "lucide-react";

function App() {
  const [refreshKey, setRefreshKey] = useState(0);
  const [activeTab, setActiveTab] = useState("single"); // 'single' or 'session'
  const [selectedSession, setSelectedSession] = useState(null);

  const handleAnalysisComplete = () => {
    setRefreshKey((prev) => prev + 1);
  };

  const handleSelectSession = (sessionId) => {
    setSelectedSession(sessionId);
  };

  const handleBackToSessions = () => {
    setSelectedSession(null);
  };

  return (
    <ThemeProvider>
      <div className="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100 dark:from-gray-900 dark:to-gray-800">
        <Header />

        <main className="container mx-auto px-4 py-8 max-w-7xl">
          {/* Tab Navigation */}
          <div className="mb-6">
            <div className="bg-white dark:bg-gray-800 rounded-lg p-1 inline-flex shadow-sm border border-gray-200 dark:border-gray-700">
              <button
                onClick={() => {
                  setActiveTab("single");
                  setSelectedSession(null);
                }}
                className={`px-4 py-2 rounded-md text-sm font-medium transition-colors flex items-center gap-2 ${
                  activeTab === "single"
                    ? "bg-primary-600 text-white"
                    : "text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700"
                }`}
              >
                <FileText className="w-4 h-4" />
                Single Chunk Analysis
              </button>
              <button
                onClick={() => setActiveTab("session")}
                className={`px-4 py-2 rounded-md text-sm font-medium transition-colors flex items-center gap-2 ${
                  activeTab === "session"
                    ? "bg-primary-600 text-white"
                    : "text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700"
                }`}
              >
                <FolderOpen className="w-4 h-4" />
                Session Management
              </button>
            </div>
          </div>

          {/* Content */}
          {activeTab === "single" ? (
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
              <div className="lg:col-span-2">
                <LogAnalyzer onAnalysisComplete={handleAnalysisComplete} />
              </div>
              <div>
                <Stats key={refreshKey} />
              </div>
            </div>
          ) : (
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
              <div className="lg:col-span-2">
                {selectedSession ? (
                  <SessionDetails
                    sessionId={selectedSession}
                    onBack={handleBackToSessions}
                  />
                ) : (
                  <SessionList onSelectSession={handleSelectSession} />
                )}
              </div>
              <div className="space-y-6">
                <SessionUpload />
                <Stats key={refreshKey} />
              </div>
            </div>
          )}
        </main>

        <footer className="bg-white dark:bg-gray-800 border-t border-gray-200 dark:border-gray-700 py-6 mt-12">
          <div className="container mx-auto px-4 text-center text-gray-600 dark:text-gray-400">
            <p>
              MITRE ATT&CK Log Analyzer • Built with React + FastAPI + MongoDB
            </p>
          </div>
        </footer>
      </div>
    </ThemeProvider>
  );
}

export default App;
