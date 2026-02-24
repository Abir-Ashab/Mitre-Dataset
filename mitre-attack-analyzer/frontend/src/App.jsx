import {
  BrowserRouter as Router,
  Routes,
  Route,
  NavLink,
} from "react-router-dom";
import Header from "./components/Header";
import SingleAnalysisPage from "./pages/SingleAnalysisPage";
import SessionsPage from "./pages/SessionsPage";
import { ThemeProvider } from "./contexts/ThemeContext";
import { FileText, FolderOpen } from "lucide-react";

function App() {
  return (
    <ThemeProvider>
      <Router>
        <div className="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100 dark:from-gray-900 dark:to-gray-800">
          <Header />

          <main className="container mx-auto px-4 py-8 max-w-7xl">
            {/* Route Navigation */}
            <div className="mb-6">
              <nav className="bg-white dark:bg-gray-800 rounded-lg p-1 inline-flex shadow-sm border border-gray-200 dark:border-gray-700">
                <NavLink
                  to="/"
                  end
                  className={({ isActive }) =>
                    `px-4 py-2 rounded-md text-sm font-medium transition-colors flex items-center gap-2 ${
                      isActive
                        ? "bg-primary-600 text-white"
                        : "text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700"
                    }`
                  }
                >
                  <FileText className="w-4 h-4" />
                  Single Chunk Analysis
                </NavLink>
                <NavLink
                  to="/sessions"
                  className={({ isActive }) =>
                    `px-4 py-2 rounded-md text-sm font-medium transition-colors flex items-center gap-2 ${
                      isActive
                        ? "bg-primary-600 text-white"
                        : "text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700"
                    }`
                  }
                >
                  <FolderOpen className="w-4 h-4" />
                  Session Management
                </NavLink>
              </nav>
            </div>

            {/* Routes */}
            <Routes>
              <Route path="/" element={<SingleAnalysisPage />} />
              <Route path="/sessions" element={<SessionsPage />} />
              <Route path="/sessions/:sessionId" element={<SessionsPage />} />
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
