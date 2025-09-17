import React from 'react';
import { ChevronRight, CheckCircle, Database } from 'lucide-react';
import { stepConfig, priorityStepOrder, getStepIcon, getStepColor } from '../utils/attackData';

const ScenarioCard = ({ 
  scenario, 
  onSave,
  onMarkComplete,
  loading,
  isMultiSelectMode = false,
  isSelected = false,
  onSelect,
  onViewDetails
}) => {
  const scenarioSteps = priorityStepOrder.filter(key => scenario[key]);
  
  return (
    <div 
      className={`relative rounded-xl border-2 transition-all duration-300 hover:shadow-xl group cursor-pointer ${
        isSelected 
          ? 'border-blue-500 bg-blue-50 shadow-lg' 
          : scenario.type === 'Alternative' 
            ? 'bg-gradient-to-br from-orange-50 to-orange-100 border-orange-200 hover:border-orange-400' 
            : 'bg-gradient-to-br from-blue-50 to-indigo-50 border-blue-200 hover:border-blue-400'
      } hover:shadow-md`}
      onClick={(e) => {
        e.stopPropagation();
        if (isMultiSelectMode) {
          onSelect();
        } else {
          onViewDetails();
        }
      }}
    >
      {/* Header */}
      <div className={`p-4 border-b ${
        scenario.type === 'Alternative' 
          ? 'border-orange-200 bg-gradient-to-r from-orange-100 to-orange-200' 
          : 'border-blue-200 bg-gradient-to-r from-blue-100 to-indigo-100'
      }`}>
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <div>
              <h3 className="font-bold text-gray-900">
                Scenario #{scenario.id} <span className={`text-sm px-2 py-0.5 rounded-full ${
                  scenario.type === 'Alternative' 
                    ? 'bg-orange-200 text-orange-800' 
                    : 'bg-blue-200 text-blue-800'
                }`}>{scenario.type}</span>
              </h3>
              <p className="text-sm text-gray-600 mt-1">Multi-stage attack simulation</p>
            </div>
          </div>
          <div className="flex items-center space-x-2 text-sm text-gray-500">
            <span className={`bg-white px-3 py-1 rounded-full font-medium border ${
              scenario.type === 'Alternative' 
                ? 'border-orange-200 text-orange-700' 
                : 'border-blue-200 text-blue-700'
            }`}>
              {scenarioSteps.length} steps
            </span>
            <ChevronRight className="w-4 h-4 text-gray-500 group-hover:text-gray-700 transition-colors" />
          </div>
        </div>
      </div>

      {/* Content */}
      <div className="p-4 space-y-3">
        {priorityStepOrder.filter(key => scenario[key]).slice(0, 4).map((key, idx) => {
          const config = stepConfig[key];
          const color = getStepColor(priorityStepOrder.indexOf(key));
          const IconComponent = getStepIcon(key);
          
          return (
            <div key={key} className={`flex items-start space-x-3 p-3 rounded-lg ${
              scenario.type === 'Alternative' 
                ? 'bg-white/60 border border-orange-200/50' 
                : 'bg-white/60 border border-blue-200/50'
            }`}>
              <div className="min-w-0 flex-1">
                <div className="flex items-center space-x-2 mb-1">
                  <span className={`text-sm font-medium text-${color}-700`}>{config.label}</span>
                  <div className={`w-2 h-2 rounded-full bg-${color}-400`}></div>
                </div>
                <p className="text-xs text-gray-700 leading-relaxed line-clamp-2">
                  {scenario[key].length > 80 ? `${scenario[key].substring(0, 80)}...` : scenario[key]}
                </p>
              </div>
            </div>
          );
        })}
        
        {priorityStepOrder.filter(key => scenario[key]).length > 4 && (
          <div className={`text-center pt-2 border-t border-gray-200 ${!isMultiSelectMode ? 'group-hover:border-gray-300' : ''}`}>
            <span className={`text-xs font-medium px-3 py-1 rounded-full transition-colors ${
              scenario.type === 'Alternative' 
                ? 'bg-orange-100 text-orange-700 border border-orange-200 group-hover:bg-orange-200' 
                : 'bg-blue-100 text-blue-700 border border-blue-200 group-hover:bg-blue-200'
            }`}>
              +{priorityStepOrder.filter(key => scenario[key]).length - 4} more steps • Click to view details
            </span>
          </div>
        )}
      </div>

      {!isMultiSelectMode && (
        <div className="p-4 pt-0 flex items-center space-x-2">
          <button
            onClick={async (e) => {
              e.stopPropagation();
              const success = await onSave(scenario);
              if (success) {
                const scenarioId = `SC${scenario.id.toString().padStart(3, '0')}`;
                await onMarkComplete(scenarioId);
              }
            }}
            disabled={loading}
            className="flex-1 flex items-center justify-center space-x-2 bg-gradient-to-r from-green-500 to-emerald-600 text-white px-4 py-2 rounded-lg text-sm font-medium hover:from-green-600 hover:to-emerald-700 transition-all duration-300 shadow-sm hover:shadow-md disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {loading ? (
              <>
                <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
                <span>Processing...</span>
              </>
            ) : (
              <>
                <CheckCircle className="h-4 w-4" />
                <span>Mark As Completed</span>
              </>
            )}
          </button>
        </div>
      )}
    </div>
  );
};

export default ScenarioCard;
