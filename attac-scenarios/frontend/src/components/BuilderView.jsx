import React from 'react';
import { AlertTriangle, Eye, Shuffle, FileText, RotateCcw, Play } from 'lucide-react';
import StepVariationCard from './StepVariationCard';
import { attackSteps, stepConfig, priorityStepOrder, getStepIcon, getStepColor } from '../utils/attackData';

const BuilderView = ({ 
  selectedValues, 
  onVariationSelect, 
  onRandomSelect, 
  onSelectAllRandom, 
  onResetSelections 
}) => {
  const stepKeys = Object.keys(attackSteps);

  return (
    <>
      <div className="grid grid-cols-2 md:grid-cols-4 gap-3 mb-8">
        {[
          { title: "Attack Steps", value: stepKeys.length, color: "blue", icon: AlertTriangle },
          { title: "Selected", value: Object.keys(selectedValues).length, color: "blue", icon: Eye },
          { title: "Variations", value: stepKeys.reduce((sum, key) => sum + attackSteps[key].length, 0), color: "blue", icon: Shuffle },
          { title: "Generated", value: "240+", color: "blue", icon: FileText }
        ].map((stat, index) => (
          <div key={index} className="bg-white rounded-xl p-4 shadow-md border border-gray-100 hover:shadow-lg transition-all duration-300">
            <div className="flex items-center justify-between mb-3">
              <div className={`w-10 h-10 bg-gradient-to-br from-${stat.color}-400 to-${stat.color}-600 rounded-lg flex items-center justify-center`}>
                <stat.icon className="h-5 w-5 text-white" />
              </div>
              <span className={`text-2xl font-bold bg-gradient-to-r from-${stat.color}-600 to-${stat.color}-700 bg-clip-text text-transparent`}>
                {stat.value}
              </span>
            </div>
            <h3 className="font-medium text-gray-700 text-sm">{stat.title}</h3>
          </div>
        ))}
      </div>

      <div className="flex justify-end space-x-3 mb-6">
        <button
          onClick={onSelectAllRandom}
          className="flex items-center space-x-2 bg-gradient-to-r from-green-500 to-emerald-600 text-white px-6 py-3 rounded-xl font-semibold hover:from-green-600 hover:to-emerald-700 transition-all duration-300 shadow-lg hover:shadow-xl"
        >
          <Shuffle className="h-5 w-5" />
          <span>Randomize All</span>
        </button>
        <button
          onClick={onResetSelections}
          className="flex items-center space-x-2 bg-white text-gray-700 px-6 py-3 rounded-xl font-semibold hover:bg-gray-50 transition-all duration-300 shadow-lg hover:shadow-xl border border-gray-200"
        >
          <RotateCcw className="h-5 w-5" />
          <span>Reset</span>
        </button>
      </div>

      {/* Current Scenario Preview */}
      {Object.keys(selectedValues).length > 0 && (
        <div className="bg-gradient-to-r from-blue-50 to-indigo-50 rounded-2xl p-6 mb-8 border border-blue-200 shadow-lg">
          <h2 className="text-2xl font-bold text-gray-900 mb-4 flex items-center">
            <div className="w-10 h-10 bg-gradient-to-br from-blue-600 to-indigo-600 rounded-xl flex items-center justify-center mr-3 shadow-lg">
              <Play className="h-5 w-5 text-white" />
            </div>
            Current Attack Scenario
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {priorityStepOrder.map((key, index) => {
              if (!selectedValues[key]) return null;
              const config = stepConfig[key];
              const color = getStepColor(index);
              const IconComponent = getStepIcon(key);
              
              return (
                <div key={key} className="flex items-start space-x-3 p-4 bg-white/70 rounded-xl border border-blue-200/50">
                  <div className={`flex-shrink-0 w-10 h-10 rounded-xl bg-gradient-to-br from-${color}-500 to-${color}-600 flex items-center justify-center text-white shadow-lg`}>
                    <IconComponent className="h-5 w-5" />
                  </div>
                  <div className="min-w-0 flex-1">
                    <div className="flex items-center space-x-2 mb-2">
                      <span className={`text-sm font-semibold text-${color}-700`}>
                        {config.label}
                      </span>
                    </div>
                    <p className="text-gray-700 text-sm leading-relaxed break-words">{selectedValues[key]}</p>
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      )}

      {/* Attack Steps Grid */}
      <div className="grid grid-cols-1 xl:grid-cols-2 gap-8">
        {priorityStepOrder.map((key, index) => (
          <StepVariationCard
            key={key}
            stepKey={key}
            stepIndex={index}
            variations={attackSteps[key]}
            selected={selectedValues[key]}
            onVariationSelect={onVariationSelect}
            onRandomSelect={onRandomSelect}
          />
        ))}
      </div>
    </>
  );
};

export default BuilderView;
