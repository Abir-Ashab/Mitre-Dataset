import React from 'react';
import { X, Target, Clock, CheckCircle, Activity, Copy } from 'lucide-react';
import { stepConfig, priorityStepOrder, getStepIcon, getStepColor } from '../utils/attackData';

const ScenarioDetailModal = ({ scenario, isOpen, onClose, isCompleted = false, onMarkComplete, onMarkIncomplete, loading }) => {
  if (!isOpen || !scenario) return null;

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const copyScenarioId = () => {
    const scenarioId = isCompleted ? scenario.scenarioId : `SC${scenario.id.toString().padStart(3, '0')}`;
    navigator.clipboard.writeText(scenarioId);
  };

  const scenarioSteps = isCompleted 
    ? scenario.attackTechniques || []
    : priorityStepOrder.filter(key => scenario[key]);

  return (
    <div className="fixed inset-0 flex items-center justify-center z-50 p-4 bg-white/10 backdrop-blur-sm">
      <div className="bg-white rounded-2xl shadow-2xl max-w-4xl max-h-[90vh] overflow-hidden w-full">
        <div className={`p-6 border-b ${
          isCompleted 
            ? 'bg-gradient-to-r from-green-50 to-emerald-50 border-green-200'
            : scenario.type === 'Alternative' 
              ? 'bg-gradient-to-r from-orange-50 to-orange-100 border-orange-200' 
              : 'bg-gradient-to-r from-blue-50 to-indigo-50 border-blue-200'
        }`}>
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <div className={`w-12 h-12 rounded-xl flex items-center justify-center text-white shadow-lg ${
                isCompleted 
                  ? 'bg-gradient-to-br from-green-500 to-emerald-600'
                  : scenario.type === 'Alternative' 
                    ? 'bg-gradient-to-br from-orange-500 to-orange-600' 
                    : 'bg-gradient-to-br from-blue-500 to-indigo-600'
              }`}>
                {isCompleted ? <CheckCircle className="h-6 w-6" /> : <Target className="h-6 w-6" />}
              </div>
              <div>
                <h2 className="text-2xl font-bold text-gray-900">
                  {isCompleted ? scenario.title : `Scenario #${scenario.id}`}
                  {!isCompleted && (
                    <span className={`ml-3 text-sm px-3 py-1 rounded-full ${
                      scenario.type === 'Alternative' 
                        ? 'bg-orange-200 text-orange-800' 
                        : 'bg-blue-200 text-blue-800'
                    }`}>
                      {scenario.type}
                    </span>
                  )}
                </h2>
                <div className="flex items-center space-x-4 mt-2">
                  <div className="flex items-center space-x-2">
                    <button
                      onClick={copyScenarioId}
                      className="flex items-center space-x-1 text-sm text-gray-600 hover:text-gray-800 bg-white px-2 py-1 rounded border"
                    >
                      <Copy className="h-3 w-3" />
                      <span className="font-mono">
                        {isCompleted ? scenario.scenarioId : `SC${scenario.id.toString().padStart(3, '0')}`}
                      </span>
                    </button>
                  </div>
                  {isCompleted && (
                    <div className="flex items-center space-x-2 text-sm text-gray-600">
                      <Clock className="h-4 w-4" />
                      <span>Completed: {formatDate(scenario.completedAt)}</span>
                    </div>
                  )}
                </div>
              </div>
            </div>
            <button
              onClick={onClose}
              className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
            >
              <X className="h-6 w-6 text-gray-500" />
            </button>
          </div>
        </div>

        {/* Content */}
        <div className="p-6 overflow-y-auto max-h-[60vh]">
          <div className="space-y-6">
            {/* Attack Steps */}
            <div>
              <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
                <Activity className="h-5 w-5 mr-2" />
                Attack Chain ({isCompleted ? scenario.attackTechniques?.length || 0 : scenarioSteps.length} steps)
              </h3>
              <div className="space-y-4">
                {isCompleted ? (
                  // Completed scenario display
                  scenario.attackTechniques?.map((technique, idx) => (
                    <div key={idx} className="flex items-start space-x-4 p-4 bg-gray-50 rounded-lg border">
                      <div className="flex-shrink-0 w-8 h-8 bg-green-500 text-white rounded-lg flex items-center justify-center text-sm font-bold">
                        {idx + 1}
                      </div>
                      <div className="flex-1">
                        <div className="flex items-center space-x-2 mb-2">
                          <span className="text-sm font-medium text-green-700 bg-green-100 px-2 py-1 rounded">
                            {technique.tactic}
                          </span>
                          <span className="text-xs text-gray-500">•</span>
                          <span className="text-sm text-gray-600">{technique.techniqueId}</span>
                        </div>
                        <h4 className="font-medium text-gray-900 mb-1">{technique.techniqueName}</h4>
                        {technique.description && (
                          <p className="text-sm text-gray-600">{technique.description}</p>
                        )}
                      </div>
                    </div>
                  ))
                ) : (
                  // Regular scenario display
                  scenarioSteps.map((key, idx) => {
                    const config = stepConfig[key];
                    const color = getStepColor(priorityStepOrder.indexOf(key));
                    const IconComponent = getStepIcon(key);
                    
                    return (
                      <div key={key} className="flex items-start space-x-4 p-4 bg-gray-50 rounded-lg border">
                        <div className={`flex-shrink-0 w-8 h-8 rounded-lg bg-gradient-to-br from-${color}-400 to-${color}-600 flex items-center justify-center text-white shadow-sm`}>
                          <IconComponent className="h-4 w-4" />
                        </div>
                        <div className="flex-1">
                          <div className="flex items-center space-x-2 mb-2">
                            <span className={`text-sm font-medium text-${color}-700 bg-${color}-100 px-2 py-1 rounded`}>
                              {config.label}
                            </span>
                            <div className={`w-2 h-2 rounded-full bg-${color}-400`}></div>
                          </div>
                          <p className="text-sm text-gray-700 leading-relaxed">
                            {scenario[key]}
                          </p>
                          {config.description && (
                            <p className="text-xs text-gray-500 mt-1 italic">{config.description}</p>
                          )}
                        </div>
                      </div>
                    );
                  })
                )}
              </div>
            </div>

            {/* Additional Info */}
            {isCompleted && (
              <div className="border-t pt-4">
                <h3 className="text-lg font-semibold text-gray-900 mb-3">Timeline</h3>
                <div className="space-y-2 text-sm">
                  <div className="flex justify-between">
                    <span className="text-gray-600">Created:</span>
                    <span className="font-medium">{formatDate(scenario.createdAt)}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600">Completed:</span>
                    <span className="font-medium">{formatDate(scenario.completedAt)}</span>
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>

        {/* Footer Actions */}
        <div className="p-6 border-t bg-gray-50 flex items-center justify-between">
          <div className="text-sm text-gray-500">
            {isCompleted ? (
              `${scenario.attackTechniques?.length || 0} attack techniques`
            ) : (
              `${scenarioSteps.length} attack steps`
            )}
          </div>
          <div className="flex items-center space-x-3">
            <button
              onClick={onClose}
              className="px-4 py-2 text-gray-600 hover:text-gray-800 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
            >
              Close
            </button>
            {isCompleted ? (
              <button
                onClick={() => onMarkIncomplete(scenario.scenarioId)}
                disabled={loading}
                className="flex items-center space-x-2 px-4 py-2 bg-gradient-to-r from-red-500 to-red-600 text-white rounded-lg hover:from-red-600 hover:to-red-700 transition-all duration-300 disabled:opacity-50"
              >
                {loading ? (
                  <>
                    <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
                    <span>Processing...</span>
                  </>
                ) : (
                  <>
                    <X className="h-4 w-4" />
                    <span>Mark Incomplete</span>
                  </>
                )}
              </button>
            ) : (
              <button
                onClick={async () => {
                  const success = await onMarkComplete(scenario);
                  if (success) {
                    onClose();
                  }
                }}
                disabled={loading}
                className="flex items-center space-x-2 px-4 py-2 bg-gradient-to-r from-green-500 to-emerald-600 text-white rounded-lg hover:from-green-600 hover:to-emerald-700 transition-all duration-300 disabled:opacity-50"
              >
                {loading ? (
                  <>
                    <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
                    <span>Processing...</span>
                  </>
                ) : (
                  <>
                    <CheckCircle className="h-4 w-4" />
                    <span>Mark Complete</span>
                  </>
                )}
              </button>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default ScenarioDetailModal;