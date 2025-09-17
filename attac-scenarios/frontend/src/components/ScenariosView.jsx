import React, { useState, useMemo, useEffect, useRef } from 'react';
import { Filter, X, Search, CheckSquare, Square, Users } from 'lucide-react';
import ScenarioCard from './ScenarioCard';
import ScenarioDetailModal from './ScenarioDetailModal';
import { attackSteps } from '../utils/attackData';

const ScenariosView = ({ 
  onSaveScenario,
  onMarkComplete,
  loading 
}) => {
  const [selectedFilters, setSelectedFilters] = useState([attackSteps.initialAccess[0]]);
  const [searchTerm, setSearchTerm] = useState('');
  const [debouncedSearchTerm, setDebouncedSearchTerm] = useState('');
  const [showFilterDropdown, setShowFilterDropdown] = useState(false);
  const [selectedScenarios, setSelectedScenarios] = useState(new Set());
  const [isMultiSelectMode, setIsMultiSelectMode] = useState(false);
  const [selectedScenarioForDetails, setSelectedScenarioForDetails] = useState(null);
  const [isDetailModalOpen, setIsDetailModalOpen] = useState(false);
  
  // New state for server-side filtering
  const [scenarios, setScenarios] = useState([]);
  const [totalCount, setTotalCount] = useState(0);
  const [currentPage, setCurrentPage] = useState(1);
  const [isLoadingScenarios, setIsLoadingScenarios] = useState(false);
  
  const SCENARIOS_PER_PAGE = 50;
  
  // Ref for dropdown click-outside detection
  const dropdownRef = useRef(null);

  // Get exact initial access methods for filtering (memoized once)
  const initialAccessMethods = useMemo(() => {
    return attackSteps.initialAccess;
  }, []);

  // Function to generate scenarios server-side (replacing the heavy client-side generation)
  const generateScenariosForFilters = (filters, searchTerm = '', page = 1) => {
    const scenarios = [];
    let scenarioId = 1;
    let matchCount = 0;
    const startIndex = (page - 1) * SCENARIOS_PER_PAGE;
    const endIndex = startIndex + SCENARIOS_PER_PAGE;

    // Only generate scenarios for selected initial access methods
    filters.forEach((initialAccess) => {
      // Base scenario
      const baseScenario = {
        id: scenarioId++,
        type: "Primary",
        initialAccess,
        attackerControl: attackSteps.attackerControl[0],
        postAttackCleanup: attackSteps.postAttackCleanup[0],
      };

      // Check if matches search term
      const matchesSearch = !searchTerm || 
        initialAccess.toLowerCase().includes(searchTerm.toLowerCase()) ||
        baseScenario.type.toLowerCase().includes(searchTerm.toLowerCase());

      if (matchesSearch) {
        if (matchCount >= startIndex && matchCount < endIndex) {
          scenarios.push(baseScenario);
        }
        matchCount++;
      }

      // Generate scenarios with optional steps (limited to prevent memory overload)
      const optionalSteps = [
        "operationAfterInitialAccess",
        "credentialHarvesting", 
        "persistence",
        "dataExfiltration",
        "lateralMovement",
        "finalPayload",
      ];

      // Add single optional step scenarios (first few variations only)
      optionalSteps.forEach((stepKey) => {
        // Limit to first 5 variations to keep it manageable
        attackSteps[stepKey].slice(0, 5).forEach((variation) => {
          const scenario = {
            ...baseScenario,
            id: scenarioId++,
            [stepKey]: variation,
          };

          const stepMatchesSearch = !searchTerm || 
            variation.toLowerCase().includes(searchTerm.toLowerCase()) ||
            initialAccess.toLowerCase().includes(searchTerm.toLowerCase());

          if (stepMatchesSearch) {
            if (matchCount >= startIndex && matchCount < endIndex) {
              scenarios.push(scenario);
            }
            matchCount++;
          }
        });
      });
    });

    return { scenarios, totalCount: matchCount };
  };

  // Function to load scenarios based on current filters
  const loadScenarios = async (filters = selectedFilters, searchTerm = debouncedSearchTerm, page = 1) => {
    if (filters.length === 0) {
      setScenarios([]);
      setTotalCount(0);
      return;
    }

    setIsLoadingScenarios(true);
    try {
      // Simulate async operation (in real app, this would be an API call)
      await new Promise(resolve => setTimeout(resolve, 100));
      
      const { scenarios: newScenarios, totalCount: count } = generateScenariosForFilters(filters, searchTerm, page);
      
      if (page === 1) {
        setScenarios(newScenarios);
      } else {
        // Append to existing scenarios for pagination
        setScenarios(prev => [...prev, ...newScenarios]);
      }
      setTotalCount(count);
      setCurrentPage(page);
    } catch (error) {
      console.error('Error loading scenarios:', error);
    } finally {
      setIsLoadingScenarios(false);
    }
  };

  // Load scenarios when filters change
  useEffect(() => {
    loadScenarios(selectedFilters, debouncedSearchTerm, 1);
  }, [selectedFilters, debouncedSearchTerm]);

  // Initial load
  useEffect(() => {
    loadScenarios();
  }, []);

  // Close dropdown when clicking outside
  useEffect(() => {
    const handleClickOutside = (event) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target)) {
        setShowFilterDropdown(false);
      }
    };

    if (showFilterDropdown) {
      document.addEventListener('mousedown', handleClickOutside);
      return () => {
        document.removeEventListener('mousedown', handleClickOutside);
      };
    }
  }, [showFilterDropdown]);

  // Debounce search term for better performance
  useEffect(() => {
    const timer = setTimeout(() => {
      setDebouncedSearchTerm(searchTerm);
    }, 300);

    return () => clearTimeout(timer);
  }, [searchTerm]);

  // Clear selections when scenarios change
  useEffect(() => {
    setSelectedScenarios(new Set());
  }, [scenarios]);

  const handleFilterToggle = (method) => {
    setSelectedFilters(prev => {
      const newFilters = prev.includes(method) 
        ? prev.filter(f => f !== method)
        : [...prev, method];
      return newFilters;
    });
    setCurrentPage(1); // Reset to first page when filters change
  };

  const clearFilters = () => {
    setSelectedFilters([attackSteps.initialAccess[0]]); // Reset to default filter
    setSearchTerm('');
    setDebouncedSearchTerm(''); // Clear debounced term immediately
    setShowFilterDropdown(false); // Close dropdown after clearing
  };

  const handleScenarioSelect = (scenarioId) => {
    setSelectedScenarios(prev => {
      const newSet = new Set(prev);
      if (newSet.has(scenarioId)) {
        newSet.delete(scenarioId);
      } else {
        newSet.add(scenarioId);
      }
      return newSet;
    });
  };

  const handleSelectAll = () => {
    const allIds = scenarios.map(s => s.id);
    if (selectedScenarios.size === allIds.length) {
      setSelectedScenarios(new Set());
    } else {
      setSelectedScenarios(new Set(allIds));
    }
  };

  const handleBulkMarkComplete = async () => {
    if (selectedScenarios.size === 0) return;
    
    const selectedScenariosList = scenarios.filter(s => selectedScenarios.has(s.id));
    
    for (const scenario of selectedScenariosList) {
      const success = await onSaveScenario(scenario);
      if (success) {
        const scenarioId = `SC${scenario.id.toString().padStart(3, '0')}`;
        await onMarkComplete(scenarioId);
      }
    }
    
    // Clear selections after bulk operation
    setSelectedScenarios(new Set());
  };

  const handleViewScenarioDetails = (scenario) => {
    setSelectedScenarioForDetails(scenario);
    setIsDetailModalOpen(true);
  };

  const handleMarkCompleteFromModal = async (scenario) => {
    const success = await onSaveScenario(scenario);
    if (success) {
      const scenarioId = `SC${scenario.id.toString().padStart(3, '0')}`;
      await onMarkComplete(scenarioId);
      return true;
    }
    return false;
  };

  // Function to load more scenarios (pagination)
  const loadMoreScenarios = () => {
    if (!isLoadingScenarios && scenarios.length < totalCount) {
      loadScenarios(selectedFilters, debouncedSearchTerm, currentPage + 1);
    }
  };
  
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
              <span className="font-medium text-gray-700">Primary ({scenarios.filter(s => s.type === 'Primary').length})</span>
            </div>
            <div className="flex items-center space-x-2">
              <div className="w-4 h-4 bg-gradient-to-r from-orange-500 to-orange-600 rounded-full"></div>
              <span className="font-medium text-gray-700">Alternative ({scenarios.filter(s => s.type === 'Alternative').length})</span>
            </div>
            <div className="flex items-center space-x-2">
              <span className="font-medium text-gray-700">Showing: {scenarios.length} scenarios</span>
              {scenarios.length < totalCount && (
                <span className="text-blue-600 font-medium">of {totalCount} total</span>
              )}
            </div>
            {isLoadingScenarios && (
              <div className="flex items-center space-x-2">
                <div className="w-4 h-4 border-2 border-blue-500 border-t-transparent rounded-full animate-spin"></div>
                <span className="text-gray-600 text-sm">Loading...</span>
              </div>
            )}
          </div>
        </div>

        {/* Multi-Select Controls */}
        {scenarios.length > 0 && (
          <div className="flex items-center justify-between mb-4 p-4 bg-gray-50 rounded-lg border">
            <div className="flex items-center space-x-4">
              <button
                onClick={() => setIsMultiSelectMode(!isMultiSelectMode)}
                className={`flex items-center space-x-2 px-3 py-2 rounded-lg transition-colors ${
                  isMultiSelectMode 
                    ? 'bg-blue-100 text-blue-700 border border-blue-300' 
                    : 'bg-white text-gray-600 border border-gray-300 hover:bg-gray-50'
                }`}
              >
                {isMultiSelectMode ? <CheckSquare className="h-4 w-4" /> : <Square className="h-4 w-4" />}
                <span className="font-medium">Multi-Select Mode</span>
              </button>
              
              {isMultiSelectMode && (
                <>
                  <button
                    onClick={handleSelectAll}
                    className="flex items-center space-x-2 px-3 py-2 text-gray-600 hover:text-gray-800 border border-gray-300 rounded-lg hover:bg-gray-50"
                  >
                    <Users className="h-4 w-4" />
                    <span>
                      {selectedScenarios.size === scenarios.length ? 'Deselect All' : 'Select All'}
                    </span>
                  </button>
                  
                  {selectedScenarios.size > 0 && (
                    <span className="text-sm text-gray-600 bg-white px-3 py-2 rounded-lg border">
                      {selectedScenarios.size} scenario{selectedScenarios.size !== 1 ? 's' : ''} selected
                    </span>
                  )}
                </>
              )}
            </div>
            
            {isMultiSelectMode && selectedScenarios.size > 0 && (
              <button
                onClick={handleBulkMarkComplete}
                disabled={loading}
                className="flex items-center space-x-2 bg-gradient-to-r from-green-500 to-emerald-600 text-white px-4 py-2 rounded-lg font-medium hover:from-green-600 hover:to-emerald-700 transition-all duration-300 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {loading ? (
                  <>
                    <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
                    <span>Processing...</span>
                  </>
                ) : (
                  <>
                    <CheckSquare className="h-4 w-4" />
                    <span>Mark {selectedScenarios.size} as Complete</span>
                  </>
                )}
              </button>
            )}
          </div>
        )}


        <div className="flex flex-col lg:flex-row gap-4 mb-6">
          {/* Search Bar */}
          <div className="flex-1 relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 h-4 w-4" />
            <input
              type="text"
              placeholder="Search scenarios..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            />
          </div>

          {/* Filter Dropdown */}
          <div className="relative" ref={dropdownRef}>
            <button
              onClick={() => setShowFilterDropdown(!showFilterDropdown)}
              className="flex items-center space-x-2 px-4 py-2 bg-blue-50 border border-blue-200 rounded-lg hover:bg-blue-100 transition-colors"
            >
              <Filter className="h-4 w-4 text-blue-600" />
              <span className="text-blue-600 font-medium">
                Filter by Initial Access {selectedFilters.length > 0 && `(${selectedFilters.length} selected)`}
              </span>
            </button>

            {showFilterDropdown && (
              <div className="absolute right-0 mt-2 w-96 bg-white rounded-lg shadow-lg border border-gray-200 z-10 max-h-96 overflow-y-auto">
                <div className="p-4">
                  <div className="flex items-center justify-between mb-3">
                    <h3 className="font-medium text-gray-900">Select Initial Access Methods</h3>
                    <button
                      onClick={clearFilters}
                      className="text-sm text-gray-500 hover:text-gray-700 flex items-center space-x-1"
                    >
                      <X className="h-3 w-3" />
                      <span>Reset to default</span>
                    </button>
                  </div>

                  <div className="space-y-1">
                    {initialAccessMethods.map((method) => (
                      <label
                        key={method}
                        className="flex items-start space-x-2 cursor-pointer hover:bg-gray-50 p-2 rounded"
                      >
                        <input
                          type="checkbox"
                          checked={selectedFilters.includes(method)}
                          onChange={() => handleFilterToggle(method)}
                          className="rounded border-gray-300 text-blue-600 focus:ring-blue-500 mt-1 flex-shrink-0"
                        />
                        <span className="text-sm text-gray-700 leading-tight">{method}</span>
                      </label>
                    ))}
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>

        {/* Active Filters Display */}
        <div className="flex flex-wrap gap-2 mb-4">
          <span className="text-sm text-gray-600">Currently showing scenarios for:</span>
          {selectedFilters.map(filter => (
            <span
              key={filter}
              className="inline-flex items-center space-x-1 bg-blue-100 text-blue-800 text-sm px-3 py-1 rounded-full"
            >
              <span className="truncate max-w-md">{filter.length > 60 ? `${filter.substring(0, 60)}...` : filter}</span>
              <button
                onClick={() => handleFilterToggle(filter)}
                className="hover:bg-blue-200 rounded-full p-0.5"
              >
                <X className="h-3 w-3" />
              </button>
            </span>
          ))}
        </div>
      </div>

      {scenarios.length === 0 && !isLoadingScenarios ? (
        <div className="text-center py-12 bg-gray-50 rounded-lg">
          <Filter className="h-12 w-12 text-gray-400 mx-auto mb-4" />
          <h3 className="text-lg font-medium text-gray-900 mb-2">
            {selectedFilters.length === 0 ? 'Select initial access methods to view scenarios' : 'No scenarios found'}
          </h3>
          <p className="text-gray-600">
            {selectedFilters.length === 0 
              ? 'Use the filter dropdown above to choose which initial access methods you want to explore.'
              : 'Try adjusting your filters or search terms.'
            }
          </p>
          {totalCount > 0 && (
            <p className="text-gray-500 text-sm mt-2">Total scenarios available: {totalCount}</p>
          )}
        </div>
      ) : (
        <>
          <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-6">
            {scenarios.map(scenario => (
              <div key={scenario.id} className="relative">
                {isMultiSelectMode && (
                  <div className="absolute top-2 right-2 z-10">
                    <button
                      onClick={() => handleScenarioSelect(scenario.id)}
                      className={`w-6 h-6 rounded border-2 flex items-center justify-center transition-colors ${
                        selectedScenarios.has(scenario.id)
                          ? 'bg-blue-500 border-blue-500 text-white'
                          : 'bg-white border-gray-300 hover:border-blue-400'
                      }`}
                    >
                      {selectedScenarios.has(scenario.id) && (
                        <CheckSquare className="h-4 w-4" />
                      )}
                    </button>
                  </div>
                )}
                <ScenarioCard 
                  scenario={scenario}
                  onSave={onSaveScenario}
                  onMarkComplete={onMarkComplete}
                  loading={loading}
                  isMultiSelectMode={isMultiSelectMode}
                  isSelected={selectedScenarios.has(scenario.id)}
                  onSelect={() => handleScenarioSelect(scenario.id)}
                  onViewDetails={() => handleViewScenarioDetails(scenario)}
                />
              </div>
            ))}
          </div>

          {scenarios.length < totalCount && (
            <div className="flex justify-center mt-8">
              <button
                onClick={loadMoreScenarios}
                disabled={isLoadingScenarios}
                className="flex items-center space-x-2 bg-gradient-to-r from-blue-500 to-blue-600 text-white px-6 py-3 rounded-lg font-medium hover:from-blue-600 hover:to-blue-700 transition-all duration-300 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {isLoadingScenarios ? (
                  <>
                    <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
                    <span>Loading more...</span>
                  </>
                ) : (
                  <span>Load More Scenarios ({scenarios.length} of {totalCount})</span>
                )}
              </button>
            </div>
          )}
        </>
      )}
      
      {/* Scenario Detail Modal */}
      <ScenarioDetailModal
        scenario={selectedScenarioForDetails}
        isOpen={isDetailModalOpen}
        onClose={() => {
          setIsDetailModalOpen(false);
          setSelectedScenarioForDetails(null);
        }}
        onMarkComplete={handleMarkCompleteFromModal}
        loading={loading}
      />
    </>
  );
};

export default ScenariosView;
