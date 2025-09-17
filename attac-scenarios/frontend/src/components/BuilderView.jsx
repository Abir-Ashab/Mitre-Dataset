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
