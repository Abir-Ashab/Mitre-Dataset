import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import Header from "./components/Header";
import Navbar from "./components/Navbar";
import DatasetOverviewPage from "./pages/DatasetOverviewPage";
import SingleAnalysisPage from "./pages/SingleAnalysisPage";
import SessionsPage from "./pages/SessionsPage";
import TestResultsPage from "./pages/TestResultsPage";
import { ThemeProvider } from "./contexts/ThemeContext";

function App() {
  return (
    <ThemeProvider>
      <Router>
        <div className="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100 dark:from-gray-900 dark:to-gray-800">
          <Header />

          <main className="container mx-auto px-4 py-8 max-w-7xl">
            {/* Navigation */}
            <div className="mb-6">
              <Navbar />
            </div>

            {/* Routes */}
            <Routes>
              <Route path="/" element={<DatasetOverviewPage />} />
              <Route path="/analyze" element={<SingleAnalysisPage />} />
              <Route path="/sessions" element={<SessionsPage />} />
              <Route path="/sessions/:sessionId" element={<SessionsPage />} />
              <Route path="/test-results" element={<TestResultsPage />} />
            </Routes>
          </main>

          <footer className="bg-white dark:bg-gray-800 border-t border-gray-200 dark:border-gray-700 py-6 mt-12">
            <div className="container mx-auto px-4 text-center text-gray-600 dark:text-gray-400">
              <p>
                MITRE ATT&CK Log Analyzer • Built with React + FastAPI + MongoDB
              </p>
            </div>
          </footer>
        </div>
      </Router>
    </ThemeProvider>
  );
}

export default App;
