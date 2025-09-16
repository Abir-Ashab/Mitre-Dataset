import React, { useState, useMemo } from 'react';
import { Filter, X, Search } from 'lucide-react';
import ScenarioCard from './ScenarioCard';
import { attackSteps } from '../utils/attackData';

const ScenariosView = ({ 
  allScenarios, 
  onSaveScenario,
  onMarkComplete,
  loading 
}) => {
  // Start with the first initial access method as default
  const [selectedFilters, setSelectedFilters] = useState([attackSteps.initialAccess[0]]);
  const [searchTerm, setSearchTerm] = useState('');
  const [showFilterDropdown, setShowFilterDropdown] = useState(false);

  // Get exact initial access methods for filtering
  const initialAccessMethods = useMemo(() => {
    return attackSteps.initialAccess;
  }, []);

  // Filter scenarios based on selected filters and search term
  const filteredScenarios = useMemo(() => {
    let filtered = allScenarios;

    // Always apply initial access filters - never show all scenarios at once
    if (selectedFilters.length > 0) {
      filtered = filtered.filter(scenario => 
        selectedFilters.some(filter => scenario.initialAccess === filter)
      );
    } else {
      // If no filters selected, show empty results
      filtered = [];
    }

    // Apply search term
    if (searchTerm) {
      filtered = filtered.filter(scenario => 
        scenario.initialAccess.toLowerCase().includes(searchTerm.toLowerCase()) ||
        Object.values(scenario).some(value => 
          typeof value === 'string' && value.toLowerCase().includes(searchTerm.toLowerCase())
        )
      );
    }

    return filtered;
  }, [allScenarios, selectedFilters, searchTerm]);

  const handleFilterToggle = (method) => {
    setSelectedFilters(prev => 
      prev.includes(method) 
        ? prev.filter(f => f !== method)
        : [...prev, method]
    );
  };

  const clearFilters = () => {
    setSelectedFilters([attackSteps.initialAccess[0]]); // Reset to default filter
    setSearchTerm('');
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
              <span className="font-medium text-gray-700">Primary ({filteredScenarios.filter(s => s.type === 'Primary').length})</span>
            </div>
            <div className="flex items-center space-x-2">
              <div className="w-4 h-4 bg-gradient-to-r from-orange-500 to-orange-600 rounded-full"></div>
              <span className="font-medium text-gray-700">Alternative ({filteredScenarios.filter(s => s.type === 'Alternative').length})</span>
            </div>
            <div className="flex items-center space-x-2">
              <span className="font-medium text-gray-700">Showing: {filteredScenarios.length} scenarios</span>
            </div>
            <div className="flex items-center space-x-2">
              <span className="text-gray-500">Total Available: {allScenarios.length}</span>
            </div>
          </div>
        </div>

        {/* Search and Filter Controls */}
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
          <div className="relative">
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

      {filteredScenarios.length === 0 ? (
        <div className="text-center py-12 bg-gray-50 rounded-lg">
          <Filter className="h-12 w-12 text-gray-400 mx-auto mb-4" />
          <h3 className="text-lg font-medium text-gray-900 mb-2">Select initial access methods to view scenarios</h3>
          <p className="text-gray-600">Use the filter dropdown above to choose which initial access methods you want to explore.</p>
          <p className="text-gray-500 text-sm mt-2">Total scenarios available: {allScenarios.length}</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-6">
          {filteredScenarios.map(scenario => (
            <ScenarioCard 
              key={scenario.id} 
              scenario={scenario}
              onSave={onSaveScenario}
              onMarkComplete={onMarkComplete}
              loading={loading}
            />
          ))}
        </div>
      )}
    </>
  );
};

export default ScenariosView;
