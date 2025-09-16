import React from 'react';
import { Shuffle } from 'lucide-react';
import { stepConfig, getStepIcon, getStepColor } from '../utils/attackData';

const StepVariationCard = ({ 
  stepKey, 
  stepIndex, 
  variations, 
  selected, 
  onVariationSelect,
  onRandomSelect 
}) => {
  const color = getStepColor(stepIndex);
  const config = stepConfig[stepKey];
  const IconComponent = getStepIcon(stepKey);
  
  return (
    <div className={`bg-white rounded-xl shadow-sm border-2 transition-all duration-300 hover:shadow-md ${
      selected 
        ? `border-${color}-400 shadow-lg ring-2 ring-${color}-200` 
        : 'border-gray-200 hover:border-gray-300'
    }`}>
      {/* Header */}
      <div className={`p-5 border-b border-gray-100 bg-gradient-to-r from-${color}-50 to-${color}-100 rounded-t-xl`}>
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <div className={`w-12 h-12 rounded-xl bg-gradient-to-br from-${color}-500 to-${color}-600 flex items-center justify-center text-white shadow-lg`}>
              <IconComponent className="h-6 w-6" />
            </div>
            <div>
              <h3 className={`font-bold text-lg text-${color}-800 flex items-center space-x-2`}>
                <span>{stepIndex + 1}. {config.label}</span>
                {config.required && (
                  <span className="bg-red-500 text-white text-xs px-2 py-0.5 rounded-full">Required</span>
                )}
              </h3>
              <p className="text-sm text-gray-600 mt-1">{config.description}</p>
            </div>
          </div>
          <div className="flex flex-col items-end space-y-2">
            <button
              onClick={() => onRandomSelect(stepKey)}
              className={`flex items-center space-x-2 bg-white text-${color}-700 px-3 py-2 rounded-lg text-sm font-medium hover:shadow-md transition-all border border-${color}-200 hover:border-${color}-300`}
            >
              <Shuffle className="h-4 w-4" />
              <span>Random</span>
            </button>
            <span className={`bg-white text-${color}-700 text-xs px-3 py-1 rounded-full font-medium shadow-sm border border-${color}-200`}>
              {variations.length} options
            </span>
          </div>
        </div>
      </div>
      
      {/* Selected Item */}
      {selected && (
        <div className="p-4 border-b border-gray-100 bg-green-50">
          <div className="flex items-start space-x-3">
            <div className="flex-shrink-0 w-8 h-8 bg-green-500 rounded-lg flex items-center justify-center">
              <svg className="w-5 h-5 text-white" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
              </svg>
            </div>
            <div>
              <span className="text-sm font-semibold text-green-800 block mb-1">Selected Option</span>
              <p className="text-sm text-gray-700 leading-relaxed">{selected}</p>
            </div>
          </div>
        </div>
      )}
      
      {/* Options List */}
      <div className="p-4">
        <div className="space-y-2 max-h-64 overflow-y-auto custom-scrollbar">
          {variations.map((variation, index) => (
            <button
              key={index}
              onClick={() => onVariationSelect(stepKey, variation)}
              className={`w-full text-left p-3 rounded-lg text-sm transition-all duration-200 border-2 ${
                selected === variation 
                  ? `bg-${color}-50 text-${color}-900 border-${color}-300 shadow-sm` 
                  : 'hover:bg-gray-50 text-gray-700 border-gray-100 hover:border-gray-200'
              }`}
            >
              <div className="flex items-start space-x-3">
                <div className={`w-3 h-3 rounded-full mt-1 flex-shrink-0 ${
                  selected === variation ? `bg-${color}-500` : 'bg-gray-300'
                }`}></div>
                <span className="flex-1 leading-relaxed">{variation}</span>
                {selected === variation && (
                  <div className={`text-${color}-500`}>
                    <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                      <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                    </svg>
                  </div>
                )}
              </div>
            </button>
          ))}
        </div>
      </div>
    </div>
  );
};

export default StepVariationCard;
