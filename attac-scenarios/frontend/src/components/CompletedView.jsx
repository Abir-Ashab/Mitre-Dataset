import React, { useState } from 'react';
import { CheckCircle, Clock, RefreshCw } from 'lucide-react';
import CompletedScenarioCard from './CompletedScenarioCard';
import ScenarioDetailModal from './ScenarioDetailModal';

const CompletedView = ({ 
  completedScenarios, 
  onRefresh, 
  onMarkIncomplete,
  onViewScenarios,
  loading 
}) => {
  const [selectedScenarioForDetails, setSelectedScenarioForDetails] = useState(null);
  const [isDetailModalOpen, setIsDetailModalOpen] = useState(false);

  const handleViewScenarioDetails = (scenario) => {
    setSelectedScenarioForDetails(scenario);
    setIsDetailModalOpen(true);
  };
  return (
    <>
      {/* Completed Scenarios Header */}
      <div className="bg-white rounded-2xl p-6 shadow-lg border border-gray-100 mb-8">
        <div className="flex justify-between items-center mb-6">
          <div>
            <h2 className="text-3xl font-bold text-gray-900 mb-2 flex items-center">
              <CheckCircle className="h-8 w-8 text-green-500 mr-3" />
              Completed Scenarios
            </h2>
            <p className="text-gray-600">Track your progress and manage completed attack scenarios</p>
          </div>
          <div className="flex items-center space-x-4">
            <div className="bg-green-100 rounded-lg px-4 py-2">
              <span className="text-sm font-semibold text-green-700">
                {completedScenarios.length} completed
              </span>
            </div>
            <button
              onClick={onRefresh}
              disabled={loading}
              className="flex items-center space-x-2 bg-gradient-to-r from-green-600 to-emerald-600 text-white px-6 py-3 rounded-xl font-semibold hover:from-green-700 hover:to-emerald-700 transition-all duration-300 shadow-lg hover:shadow-xl disabled:opacity-50"
            >
              <RefreshCw className="h-5 w-5" />
              <span>Refresh</span>
            </button>
          </div>
        </div>
      </div>

      {/* Completed Scenarios Content */}
      {completedScenarios.length === 0 ? (
        <div className="bg-white rounded-2xl p-12 shadow-lg border border-gray-100 text-center">
          <div className="w-24 h-24 bg-gray-100 rounded-full flex items-center justify-center mx-auto mb-6">
            <Clock className="h-12 w-12 text-gray-400" />
          </div>
          <h3 className="text-2xl font-bold text-gray-900 mb-4">No Completed Scenarios</h3>
          <p className="text-gray-600 mb-8">Complete your first attack scenario to see it here.</p>
          <button
            onClick={onViewScenarios}
            className="bg-gradient-to-r from-blue-600 to-indigo-600 text-white px-6 py-3 rounded-xl font-semibold hover:from-blue-700 hover:to-indigo-700 transition-all duration-300 shadow-lg hover:shadow-xl"
          >
            View Available Scenarios
          </button>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-6">
          {completedScenarios.map(scenario => (
            <CompletedScenarioCard 
              key={scenario._id} 
              scenario={scenario}
              onMarkIncomplete={onMarkIncomplete}
              loading={loading}
              onViewDetails={() => handleViewScenarioDetails(scenario)}
            />
          ))}
        </div>
      )}
      
      {/* Scenario Detail Modal */}
      <ScenarioDetailModal
        scenario={selectedScenarioForDetails}
        isOpen={isDetailModalOpen}
        onClose={() => {
          setIsDetailModalOpen(false);
          setSelectedScenarioForDetails(null);
        }}
        isCompleted={true}
        onMarkIncomplete={onMarkIncomplete}
        loading={loading}
      />
    </>
  );
};

export default CompletedView;
