import React from 'react';
import ScenarioCard from './ScenarioCard';

const ScenariosView = ({ 
  allScenarios, 
  onSaveScenario,
  onMarkComplete,
  loading 
}) => {
  return (
    <>
      <div className="bg-white rounded-2xl p-6 shadow-lg border border-gray-100 mb-8">
        <div className="flex justify-between items-center mb-6">
          <div>
            <h2 className="text-3xl font-bold text-gray-900 mb-2">Generated Scenarios</h2>
            <p className="text-gray-600">Review and mark scenarios as complete</p>
          </div>
          <div className="flex items-center space-x-4 text-sm">
            <div className="flex items-center space-x-2">
              <div className="w-4 h-4 bg-gradient-to-r from-blue-500 to-blue-600 rounded-full"></div>
              <span className="font-medium text-gray-700">Primary ({allScenarios.filter(s => s.type === 'Primary').length})</span>
            </div>
            <div className="flex items-center space-x-2">
              <div className="w-4 h-4 bg-gradient-to-r from-orange-500 to-orange-600 rounded-full"></div>
              <span className="font-medium text-gray-700">Alternative ({allScenarios.filter(s => s.type === 'Alternative').length})</span>
            </div>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-6">
        {allScenarios.map(scenario => (
          <ScenarioCard 
            key={scenario.id} 
            scenario={scenario}
            onSave={onSaveScenario}
            onMarkComplete={onMarkComplete}
            loading={loading}
          />
        ))}
      </div>
    </>
  );
};

export default ScenariosView;
