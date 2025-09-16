import React, { useState, useMemo, useEffect } from 'react';
import Header from './components/Header';
import BuilderView from './components/BuilderView';
import ScenariosView from './components/ScenariosView';
import CompletedView from './components/CompletedView';
import Notification from './components/Notification';
import { useApi } from './hooks/useApi';
import { attackSteps } from './utils/attackData';
import { generateAllScenarios } from './utils/scenarioGenerator';

const AttackScenarioGenerator = () => {
  const [selectedValues, setSelectedValues] = useState({});
  const [viewMode, setViewMode] = useState('builder'); // 'builder', 'scenarios', or 'completed'
  const [completedScenarioIds, setCompletedScenarioIds] = useState(new Set());
  const [notification, setNotification] = useState(null);

  // Use custom API hook
  const {
    loading,
    apiStatus,
    completedScenarios,
    fetchCompletedScenarios,
    saveScenarioToDatabase,
    markScenarioComplete,
    markScenarioIncomplete
  } = useApi();

  // Generate all possible scenarios
  const allScenarios = useMemo(() => generateAllScenarios(), []);

  // Filter out completed scenarios from the scenarios view
  const availableScenarios = useMemo(() => {
    return allScenarios.filter(scenario => {
      const scenarioId = `SC${scenario.id.toString().padStart(3, '0')}`;
      return !completedScenarioIds.has(scenarioId);
    });
  }, [allScenarios, completedScenarioIds]);

  // Update completed scenario IDs when completedScenarios changes
  useEffect(() => {
    const ids = new Set(completedScenarios.map(scenario => scenario.scenarioId));
    setCompletedScenarioIds(ids);
  }, [completedScenarios]);

  // Helper functions
  const selectRandomVariation = (stepKey) => {
    const variations = attackSteps[stepKey];
    const randomIndex = Math.floor(Math.random() * variations.length);
    setSelectedValues(prev => ({ ...prev, [stepKey]: variations[randomIndex] }));
  };

  const selectAllRandom = () => {
    const newSelectedValues = {};
    Object.keys(attackSteps).forEach(stepKey => {
      const variations = attackSteps[stepKey];
      const randomIndex = Math.floor(Math.random() * variations.length);
      newSelectedValues[stepKey] = variations[randomIndex];
    });
    setSelectedValues(newSelectedValues);
  };

  const resetSelections = () => {
    setSelectedValues({});
  };

  const handleVariationSelect = (stepKey, variation) => {
    setSelectedValues(prev => ({ ...prev, [stepKey]: variation }));
  };

  // Custom handler for marking scenarios complete with view switching
  const handleMarkScenarioComplete = async (scenarioId) => {
    const success = await markScenarioComplete(scenarioId);
    if (success) {
      // Show success notification
      setNotification({
        message: `Scenario ${scenarioId} completed successfully!`,
        type: 'success'
      });
      
      // Switch to completed view after a short delay to show the success
      setTimeout(() => {
        setViewMode('completed');
      }, 1500);
    } else {
      setNotification({
        message: 'Failed to mark scenario as complete. Please try again.',
        type: 'error'
      });
    }
    return success;
  };

  // Custom handler for marking scenarios incomplete
  const handleMarkScenarioIncomplete = async (scenarioId) => {
    const success = await markScenarioIncomplete(scenarioId);
    if (success) {
      setNotification({
        message: `Scenario ${scenarioId} marked as incomplete.`,
        type: 'success'
      });
      // Switch to scenarios view to show the scenario is available again
      setTimeout(() => {
        setViewMode('scenarios');
      }, 1000);
    } else {
      setNotification({
        message: 'Failed to mark scenario as incomplete. Please try again.',
        type: 'error'
      });
    }
    return success;
  };

  const renderCurrentView = () => {
    switch (viewMode) {
      case 'builder':
        return (
          <BuilderView
            selectedValues={selectedValues}
            onVariationSelect={handleVariationSelect}
            onRandomSelect={selectRandomVariation}
            onSelectAllRandom={selectAllRandom}
            onResetSelections={resetSelections}
          />
        );
      case 'scenarios':
        return (
          <ScenariosView
            allScenarios={availableScenarios}
            onSaveScenario={saveScenarioToDatabase}
            onMarkComplete={handleMarkScenarioComplete}
            loading={loading}
          />
        );
      case 'completed':
        return (
          <CompletedView
            completedScenarios={completedScenarios}
            onRefresh={fetchCompletedScenarios}
            onMarkIncomplete={handleMarkScenarioIncomplete}
            onViewScenarios={() => setViewMode('scenarios')}
            loading={loading}
          />
        );
      default:
        return null;
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-100">
      <div className="max-w-7xl mx-auto px-6 py-8">
        <Header
          viewMode={viewMode}
          setViewMode={setViewMode}
          apiStatus={apiStatus}
          allScenariosLength={availableScenarios.length}
          completedScenariosLength={completedScenarios.length}
        />

        {renderCurrentView()}
      </div>

      {/* Notification */}
      {notification && (
        <Notification
          message={notification.message}
          type={notification.type}
          onClose={() => setNotification(null)}
        />
      )}

      {/* Custom Scrollbar Styles */}
      <style jsx>{`
        .custom-scrollbar::-webkit-scrollbar {
          width: 8px;
        }
        .custom-scrollbar::-webkit-scrollbar-track {
          background: #f1f5f9;
          border-radius: 4px;
        }
        .custom-scrollbar::-webkit-scrollbar-thumb {
          background: linear-gradient(180deg, #cbd5e1 0%, #94a3b8 100%);
          border-radius: 4px;
        }
        .custom-scrollbar::-webkit-scrollbar-thumb:hover {
          background: linear-gradient(180deg, #94a3b8 0%, #64748b 100%);
        }
        .line-clamp-2 {
          display: -webkit-box;
          -webkit-line-clamp: 2;
          -webkit-box-orient: vertical;
          overflow: hidden;
        }
      `}</style>
    </div>
  );
};

export default AttackScenarioGenerator;