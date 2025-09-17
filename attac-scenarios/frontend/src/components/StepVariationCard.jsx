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
      <div className={`p-5 border-b border-gray-100 bg-gradient-to-r from-${color}-50 to-${color}-100 rounded-t-xl`}>
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <div>
              <h3 className={`font-bold text-lg text-${color}-800 flex items-center space-x-2`}>
                <span>{stepIndex + 1}. {config.label}</span>
              </h3>
              <p className="text-sm text-gray-600 mt-1">{config.description}</p>
            </div>
          </div>
        </div>
      </div>

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
