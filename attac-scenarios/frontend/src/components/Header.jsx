import React from 'react';
import { Shield, Play, FileText, CheckCircle } from 'lucide-react';

const Header = ({ 
  viewMode, 
  setViewMode, 
  apiStatus, 
  allScenariosLength, 
  completedScenariosLength 
}) => {
  return (
    <div className="mb-8">
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center space-x-6">
          <div className="flex items-center space-x-4">
            <div className="relative">
              <div className="w-16 h-16 bg-gradient-to-br from-blue-600 to-indigo-700 rounded-2xl flex items-center justify-center shadow-xl">
                <Shield className="h-8 w-8 text-white" />
              </div>
              <div className="absolute -bottom-1 -right-1 w-6 h-6 bg-green-500 rounded-full border-3 border-white flex items-center justify-center">
                <div className="w-2 h-2 bg-white rounded-full"></div>
              </div>
            </div>
            <div>
              <h1 className="text-4xl font-bold bg-gradient-to-r from-gray-900 to-gray-700 bg-clip-text text-transparent">
                MITRE ATT&CK
              </h1>
              <p className="text-xl text-gray-600 font-medium">Scenario Builder</p>
              <div className="flex items-center space-x-4 text-sm text-gray-500">
                <span>Build, customize, and export attack scenarios</span>
                <div className="flex items-center space-x-1">
                  <div className={`w-2 h-2 rounded-full ${
                    apiStatus === 'connected' ? 'bg-green-500' : 
                    apiStatus === 'disconnected' ? 'bg-red-500' : 'bg-yellow-500'
                  }`}></div>
                  <span className="text-xs">
                    {apiStatus === 'connected' ? 'Database Connected' : 
                     apiStatus === 'disconnected' ? 'Database Offline' : 'Checking...'}
                  </span>
                </div>
              </div>
            </div>
          </div>
          
          {/* Navigation Tabs */}
          <div className="flex items-center bg-white rounded-xl shadow-lg border border-gray-200 p-1">
            <button
              onClick={() => setViewMode('builder')}
              className={`flex items-center space-x-2 px-4 py-2 rounded-lg font-semibold transition-all duration-300 ${
                viewMode === 'builder' 
                  ? 'bg-gradient-to-r from-blue-600 to-indigo-600 text-white shadow-md' 
                  : 'text-gray-600 hover:text-gray-900 hover:bg-gray-50'
              }`}
            >
              <Play className="h-4 w-4" />
              <span>Builder</span>
            </button>
            
            <button
              onClick={() => setViewMode('scenarios')}
              className={`flex items-center space-x-2 px-4 py-2 rounded-lg font-semibold transition-all duration-300 ${
                viewMode === 'scenarios' 
                  ? 'bg-gradient-to-r from-blue-600 to-indigo-600 text-white shadow-md' 
                  : 'text-gray-600 hover:text-gray-900 hover:bg-gray-50'
              }`}
            >
              <FileText className="h-4 w-4" />
              <span>Scenarios</span>
              <span className="bg-blue-100 text-blue-600 text-xs px-2 py-0.5 rounded-full ml-1">
                {allScenariosLength}
              </span>
            </button>
            
            <button
              onClick={() => setViewMode('completed')}
              className={`flex items-center space-x-2 px-4 py-2 rounded-lg font-semibold transition-all duration-300 ${
                viewMode === 'completed' 
                  ? 'bg-gradient-to-r from-green-600 to-emerald-600 text-white shadow-md' 
                  : 'text-gray-600 hover:text-gray-900 hover:bg-gray-50'
              }`}
            >
              <CheckCircle className="h-4 w-4" />
              <span>Completed</span>
              <span className="bg-green-100 text-green-600 text-xs px-2 py-0.5 rounded-full ml-1">
                {completedScenariosLength}
              </span>
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Header;
