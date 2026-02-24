import { useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
import SessionUpload from "../components/SessionUpload";
import SessionList from "../components/SessionList";
import SessionDetails from "../components/SessionDetails";
import Stats from "../components/Stats";

export default function SessionsPage() {
  const { sessionId } = useParams();
  const navigate = useNavigate();
  const [refreshKey, setRefreshKey] = useState(0);

  const handleSelectSession = (id) => {
    navigate(`/sessions/${id}`);
  };

  const handleBackToSessions = () => {
    navigate("/sessions");
    setRefreshKey((prev) => prev + 1); // Refresh stats after viewing session
  };

  return (
    <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
      <div className="lg:col-span-2">
        {sessionId ? (
          <SessionDetails sessionId={sessionId} onBack={handleBackToSessions} />
        ) : (
          <SessionList onSelectSession={handleSelectSession} />
        )}
      </div>
      <div className="space-y-6">
        <SessionUpload
          onUploadComplete={() => setRefreshKey((prev) => prev + 1)}
        />
        <Stats key={refreshKey} />
      </div>
    </div>
  );
}
