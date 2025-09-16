import React from 'react';
import { CheckCircle, RotateCcw, Activity } from 'lucide-react';

const CompletedScenarioCard = ({ scenario, onMarkIncomplete, loading }) => {
  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  return (
    <div className="bg-white rounded-xl border-2 border-green-200 shadow-lg hover:shadow-xl transition-all duration-300 overflow-hidden">
      {/* Header */}
      <div className="p-4 border-b border-green-200 bg-gradient-to-r from-green-50 to-emerald-50">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <div className="w-12 h-12 bg-gradient-to-br from-green-500 to-emerald-600 rounded-xl flex items-center justify-center text-white shadow-lg">
              <CheckCircle className="h-6 w-6" />
            </div>
            <div>
              <h3 className="font-bold text-green-800">{scenario.title}</h3>
              <p className="text-sm text-green-600">Completed on {formatDate(scenario.completedAt)}</p>
            </div>
          </div>
          <div className="flex space-x-2">
            <button
              onClick={() => onMarkIncomplete(scenario.scenarioId)}
              disabled={loading}
              className="p-2 text-gray-500 hover:text-red-600 hover:bg-red-50 rounded-lg transition-colors disabled:opacity-50"
              title="Mark as incomplete"
            >
              <RotateCcw className="h-4 w-4" />
            </button>
          </div>
        </div>
      </div>

      {/* Content */}
      <div className="p-4 space-y-3">
        <div className="flex items-center justify-between text-sm">
          <span className="text-gray-600">Scenario ID:</span>
          <span className="font-mono bg-gray-100 px-2 py-1 rounded text-gray-800">{scenario.scenarioId}</span>
        </div>
        
        <div className="space-y-2">
          <span className="text-sm font-medium text-gray-700">Attack Techniques:</span>
          <div className="space-y-1">
            {scenario.attackTechniques.slice(0, 3).map((technique, idx) => (
              <div key={idx} className="flex items-center space-x-2 text-xs">
                <div className="w-2 h-2 bg-green-400 rounded-full"></div>
                <span className="text-gray-700">{technique.tactic}</span>
                <span className="text-gray-500">•</span>
                <span className="text-gray-600 flex-1 truncate">{technique.techniqueName}</span>
              </div>
            ))}
            {scenario.attackTechniques.length > 3 && (
              <div className="text-xs text-green-600 font-medium">
                +{scenario.attackTechniques.length - 3} more techniques
              </div>
            )}
          </div>
        </div>

        <div className="pt-3 border-t border-gray-100">
          <div className="flex items-center justify-between text-xs text-gray-500">
            <span>Created: {formatDate(scenario.createdAt)}</span>
            <div className="flex items-center space-x-1">
              <Activity className="h-3 w-3" />
              <span>{scenario.attackTechniques.length} steps</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default CompletedScenarioCard;
