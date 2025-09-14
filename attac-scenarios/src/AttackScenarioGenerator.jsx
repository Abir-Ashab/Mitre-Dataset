import React, { useState, useMemo } from 'react';
import { Download, Shield, AlertTriangle, ChevronRight, Shuffle, Play, RotateCcw, FileText, Eye, Target, Zap, Key, Gamepad, Lock, Upload, RefreshCw, Bomb, Trash2 } from 'lucide-react';

const AttackScenarioGenerator = () => {
  const [selectedValues, setSelectedValues] = useState({});
  const [viewMode, setViewMode] = useState('builder'); // 'builder' or 'scenarios'
  const [scenarioSelection, setScenarioSelection] = useState(new Set());

  const attackSteps = {
    initialAccess: [
      "Phishing email/message with mega link (direct exe download)",
      "Phishing email/message with mega link (direct zip download)",
      "Phishing email/message with mega link (direct rar download(without password))",
      "Phishing email/message with mega link (direct rar download(with password))",
      "Phishing email/message with mega link (bound to image)",
      "Phishing email/message with mega link (bound to pdf)",
      "Phishing email/message with mega link (bound to doc)",
      "Phishing email/message with drive link (direct exe download)",
      "Phishing email/message with drive link (direct zip download)",
      "Phishing email/message with drive link (direct rar download(without password))",
      "Phishing email/message with drive link (direct rar download(with password))",
      "Phishing email/message with drive link (bound to image)",
      "Phishing email/message with drive link (bound to pdf)",
      "Phishing email/message with drive link (bound to doc)",
      "Phishing whatsapp/message with drive link (direct exe download)",
      "Phishing whatsapp/message with drive link (direct zip download)",
      "Phishing whatsapp/message with drive link (direct rar download(without password))",
      "Phishing whatsapp/message with drive link (direct rar download(with password))",
      "Phishing whatsapp/message with drive link (bound to image)",
      "Phishing whatsapp/message with drive link (bound to pdf)",
      "Phishing whatsapp/message with drive link (bound to doc)",
      "Phishing whatsapp/message with fake installer (game update)",
      "Phishing messenger/message with drive link (direct exe download)",
      "Phishing messenger/message with drive link (direct zip download)",
      "Phishing messenger/message with drive link (direct rar download(without password))",
      "Phishing messenger/message with drive link (direct rar download(with password))",
      "Phishing messenger/message with drive link (bound to image)",
      "Phishing messenger/message with drive link (bound to pdf)",
      "Phishing messenger/message with drive link (bound to doc)",
      "Phishing telegram/message with drive link (direct exe download)",
      "Phishing telegram/message with drive link (direct zip download)",
      "Phishing telegram/message with drive link (direct rar download(without password))",
      "Phishing telegram/message with drive link (direct rar download(with password))",
      "Phishing telegram/message with drive link (bound to image)",
      "Phishing telegram/message with drive link (bound to pdf)",
      "Phishing telegram/message with drive link (bound to doc)",
      "Phishing in telegram through direct exe download",
      "Phishing in telegram through direct zip download",
      "Phishing in telegram through direct rar download(without password)",
      "Phishing in telegram through direct rar download(with password)",
      "Phishing in telegram through link bound to image",
      "Phishing in telegram through link bound to pdf",
      "Payload from public GitHub repo by cloning (click exe directly)",
      "Payload from public GitHub repo by cloning (click to a js/ts/md/other file)",
      "Payload from public GitHub repo by cloning (click to an image file)",
      "Payload from public GitHub repo by cloning (Run the project)",
      "Payload from public GitHub repo by downloading (click exe directly)",
      "Payload from public GitHub repo by downloading (click to a js/ts/md/other file)",
      "Payload from public GitHub repo by downloading (click to an image file)",
      "Payload from public GitHub repo by downloading (Run the project)",
      "Watering hole attack on compromised website",
      "USB drop attack with malicious payload",
    ],
    operationAfterInitialAccess: [
      "Delete files",
      "Edit files",
    ],
    credentialHarvesting: [
      "RAT + WebBrowserPassView credential extraction"
    ],
    attackerControl: [
      "Immediate control after compromise (RAT activation)",
      "Delayed control after dormancy period (scheduled activation, trigger-based)"
    ],
    persistence: [
      "Bootloader-based payload persistence",
      "Task Scheduler payload persistence"
    ],
    dataExfiltration: [
      "USB exfiltration",
      "Google Drive exfiltration",
      "RAT server exfiltration",
      "OneDrive exfiltration",
      "GitHub exfiltration"
    ],
    finalPayload: [
      "Ransomware (using 7zip to compress files/folders before encryption)",
      "Ransomware (full disk encryption)"
    ],
    postAttackCleanup: [
      "Leaving traces",
      "Leaving no trace (stealth cleanup)",
    ],
    lateralMovement: [
      "Windows SMB lateral movement",
      "Internal spear phishing"
    ],
  };

  const stepConfig = {
    initialAccess: { required: true, label: "Initial Access Vector", description: "How the attacker gains first access to the system" },
    operationAfterInitialAccess: { required: true, label: "Post-Breach Operations", description: "Immediate actions after gaining access", defaultIndex: 0 },
    credentialHarvesting: { required: true, label: "Credential Harvesting", description: "Methods to extract user credentials", defaultIndex: 0 },
    attackerControl: { required: true, label: "Command & Control", description: "How the attacker maintains control", defaultIndex: 0 },
    dataExfiltration: { required: true, label: "Data Exfiltration", description: "How sensitive data is stolen", defaultIndex: 0 },
    finalPayload: { required: true, label: "Final Impact", description: "The ultimate goal of the attack", defaultIndex: 0 },
    postAttackCleanup: { required: false, label: "Attack Cleanup", description: "How traces are handled" },
    lateralMovement: { required: false, label: "Lateral Movement", description: "Spreading to other systems" },
    persistence: { required: true, label: "Persistence Mechanism", description: "Methods to maintain access across reboots", defaultIndex: 0 },
  };

  const stepNames = [
    'Initial Access Vector',
    'Post-Breach Operations',
    'Credential Harvesting', 
    'Command & Control',
    'Persistence Mechanism',
    'Data Exfiltration',
    'Lateral Movement',
    'Final Impact',
    'Attack Cleanup'
  ];

  const stepKeys = Object.keys(attackSteps);

  // Define step priority order: 7 required steps first, then 2 optional steps
  const priorityStepOrder = [
    'initialAccess',
    'operationAfterInitialAccess', 
    'credentialHarvesting',
    'attackerControl',
    'dataExfiltration',
    'finalPayload',
    'postAttackCleanup',
    'persistence',
    'lateralMovement'
  ];

  // Generate all possible scenarios based on conditions (max 200)
  const allScenarios = useMemo(() => {
    const scenarios = [];
    let scenarioId = 1;

    // Generate primary scenarios (with required defaults) - limited to 150
    const maxPrimaryScenarios = 150;
    const maxInitialAccessForPrimary = Math.min(10, attackSteps.initialAccess.length);
    
    attackSteps.initialAccess.slice(0, maxInitialAccessForPrimary).forEach(initialAccess => {
      // Base scenario with required steps only
      const baseScenario = {
        id: scenarioId++,
        type: 'Primary',
        initialAccess,
        attackerControl: attackSteps.attackerControl[0], // First one is compulsory
        postAttackCleanup: attackSteps.postAttackCleanup[0], // First one is compulsory
      };

      // Add base scenario
      scenarios.push(baseScenario);

      if (scenarios.length >= maxPrimaryScenarios) return;

      // Generate limited combinations with optional steps
      const optionalSteps = ['operationAfterInitialAccess', 'credentialHarvesting', 'persistence', 'dataExfiltration', 'lateralMovement', 'finalPayload'];
      
      // Add single optional step scenarios
      optionalSteps.forEach(stepKey => {
        if (scenarios.length >= maxPrimaryScenarios) return;
        attackSteps[stepKey].forEach(variation => {
          if (scenarios.length >= maxPrimaryScenarios) return;
          scenarios.push({
            ...baseScenario,
            id: scenarioId++,
            [stepKey]: variation
          });
        });
      });

      // Add a few combinations with 2 optional steps
      if (scenarios.length < maxPrimaryScenarios - 10) {
        ['credentialHarvesting', 'dataExfiltration'].forEach(step1 => {
          ['persistence', 'finalPayload'].forEach(step2 => {
            if (scenarios.length >= maxPrimaryScenarios) return;
            attackSteps[step1].forEach(var1 => {
              attackSteps[step2].forEach(var2 => {
                if (scenarios.length >= maxPrimaryScenarios) return;
                scenarios.push({
                  ...baseScenario,
                  id: scenarioId++,
                  [step1]: var1,
                  [step2]: var2
                });
              });
            });
          });
        });
      }
    });

    // Generate alternative scenarios (limited to 50 total)
    const maxAlternativeScenarios = 50;
    const alternativeCount = Math.min(5, attackSteps.initialAccess.length);
    
    attackSteps.initialAccess.slice(0, alternativeCount).forEach(initialAccess => {
      if (scenarios.length >= 200) return;
      
      // Alternative attacker control
      scenarios.push({
        id: scenarioId++,
        type: 'Alternative',
        initialAccess,
        attackerControl: attackSteps.attackerControl[1], // Second variation
        postAttackCleanup: attackSteps.postAttackCleanup[0],
      });

      if (scenarios.length >= 200) return;

      // Alternative cleanup
      scenarios.push({
        id: scenarioId++,
        type: 'Alternative', 
        initialAccess,
        attackerControl: attackSteps.attackerControl[0],
        postAttackCleanup: attackSteps.postAttackCleanup[1], // Second variation
      });
    });

    return scenarios.slice(0, 200); // Ensure max 200 scenarios
  }, []);

  const exportScenariosToCSV = () => {
    const headers = [
      'Scenario ID',
      'Type',
      'Initial Access',
      'Post-Breach Operations',
      'Credential Harvesting',
      'Command & Control',
      'Persistence',
      'Data Exfiltration',
      'Lateral Movement',
      'Final Impact',
      'Attack Cleanup'
    ];

    const csvContent = [
      headers.join(','),
      ...allScenarios.map(scenario => [
        scenario.id,
        scenario.type,
        `"${scenario.initialAccess}"`,
        `"${scenario.operationAfterInitialAccess || ''}"`,
        `"${scenario.credentialHarvesting || ''}"`,
        `"${scenario.attackerControl}"`,
        `"${scenario.persistence || ''}"`,
        `"${scenario.dataExfiltration || ''}"`,
        `"${scenario.lateralMovement || ''}"`,
        `"${scenario.finalPayload || ''}"`,
        `"${scenario.postAttackCleanup}"`
      ].join(','))
    ].join('\n');

    const blob = new Blob([csvContent], { type: 'text/csv' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'attack_scenarios.csv';
    a.click();
    URL.revokeObjectURL(url);
  };

  const selectRandomVariation = (stepKey) => {
    const variations = attackSteps[stepKey];
    const randomIndex = Math.floor(Math.random() * variations.length);
    setSelectedValues(prev => ({
      ...prev,
      [stepKey]: variations[randomIndex]
    }));
  };

  const selectAllRandom = () => {
    const newValues = {};
    priorityStepOrder.forEach(key => {
      const variations = attackSteps[key];
      const randomIndex = Math.floor(Math.random() * variations.length);
      newValues[key] = variations[randomIndex];
    });
    setSelectedValues(newValues);
  };

  const resetSelections = () => {
    setSelectedValues({});
  };

  const toggleScenarioSelection = (scenarioId) => {
    const newSelection = new Set(scenarioSelection);
    if (newSelection.has(scenarioId)) {
      newSelection.delete(scenarioId);
    } else {
      newSelection.add(scenarioId);
    }
    setScenarioSelection(newSelection);
  };

  const exportSelectedScenarios = () => {
    const selectedScenarios = allScenarios.filter(s => scenarioSelection.has(s.id));
    if (selectedScenarios.length === 0) {
      alert('Please select at least one scenario to export.');
      return;
    }

    const headers = [
      'Scenario ID',
      'Type',
      'Initial Access',
      'Post-Breach Operations',
      'Credential Harvesting',
      'Command & Control',
      'Persistence',
      'Data Exfiltration',
      'Lateral Movement',
      'Final Impact',
      'Attack Cleanup'
    ];

    const csvContent = [
      headers.join(','),
      ...selectedScenarios.map(scenario => [
        scenario.id,
        scenario.type,
        `"${scenario.initialAccess}"`,
        `"${scenario.operationAfterInitialAccess || ''}"`,
        `"${scenario.credentialHarvesting || ''}"`,
        `"${scenario.attackerControl}"`,
        `"${scenario.persistence || ''}"`,
        `"${scenario.dataExfiltration || ''}"`,
        `"${scenario.lateralMovement || ''}"`,
        `"${scenario.finalPayload || ''}"`,
        `"${scenario.postAttackCleanup}"`
      ].join(','))
    ].join('\n');

    const blob = new Blob([csvContent], { type: 'text/csv' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `selected_attack_scenarios_${selectedScenarios.length}.csv`;
    a.click();
    URL.revokeObjectURL(url);
  };

  const getStepIcon = (stepKey) => {
    const iconMap = {
      initialAccess: Target,
      operationAfterInitialAccess: Zap,
      credentialHarvesting: Key,
      attackerControl: Gamepad,
      persistence: Lock,
      dataExfiltration: Upload,
      lateralMovement: RefreshCw,
      finalPayload: Bomb,
      postAttackCleanup: Trash2
    };
    return iconMap[stepKey] || Target;
  };

  const getStepColor = (index) => {
    const colors = [
      'red', 'orange', 'yellow', 'green', 'blue', 'purple', 'pink', 'gray'
    ];
    return colors[index] || 'gray';
  };

  const StepVariationCard = ({ stepKey, stepIndex, variations, selected }) => {
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
                onClick={() => selectRandomVariation(stepKey)}
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
                onClick={() => setSelectedValues(prev => ({ ...prev, [stepKey]: variation }))}
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

  const ScenarioCard = ({ scenario }) => {
    const scenarioSteps = stepKeys.filter(key => scenario[key]);
    const isSelected = scenarioSelection.has(scenario.id);
    
    return (
      <div 
        className={`relative rounded-xl border-2 transition-all duration-300 hover:shadow-xl cursor-pointer group ${
          scenario.type === 'Alternative' 
            ? 'bg-gradient-to-br from-orange-50 to-orange-100 border-orange-200 hover:border-orange-400' 
            : 'bg-gradient-to-br from-blue-50 to-indigo-50 border-blue-200 hover:border-blue-400'
        } ${isSelected ? 'ring-4 ring-blue-200 border-blue-500 shadow-lg' : 'hover:shadow-md'}`}
        onClick={() => toggleScenarioSelection(scenario.id)}
      >
        {/* Header */}
        <div className={`p-4 border-b ${
          scenario.type === 'Alternative' 
            ? 'border-orange-200 bg-gradient-to-r from-orange-100 to-orange-200' 
            : 'border-blue-200 bg-gradient-to-r from-blue-100 to-indigo-100'
        }`}>
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <div className="relative">
                <input
                  type="checkbox"
                  checked={isSelected}
                  onChange={(e) => {
                    e.stopPropagation();
                    toggleScenarioSelection(scenario.id);
                  }}
                  className="w-5 h-5 text-blue-600 bg-white border-2 border-gray-300 rounded focus:ring-blue-500 focus:ring-2"
                />
                {isSelected && (
                  <div className="absolute -top-1 -right-1 w-3 h-3 bg-blue-500 rounded-full animate-ping"></div>
                )}
              </div>
              <div className={`flex items-center justify-center w-10 h-10 rounded-full text-sm font-bold shadow-md ${
                scenario.type === 'Primary' 
                  ? 'bg-gradient-to-r from-blue-500 to-blue-600 text-white' 
                  : 'bg-gradient-to-r from-orange-500 to-orange-600 text-white'
              }`}>
                {scenario.id}
              </div>
              <div>
                <h3 className="font-semibold text-gray-800">Scenario #{scenario.id}</h3>
                <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                  scenario.type === 'Primary' 
                    ? 'bg-blue-200 text-blue-900 border border-blue-300' 
                    : 'bg-orange-200 text-orange-900 border border-orange-300'
                }`}>
                  {scenario.type}
                </span>
              </div>
            </div>
            <div className="flex items-center space-x-2">
              <span className={`text-xs font-medium px-2 py-1 rounded-full ${
                scenario.type === 'Alternative' 
                  ? 'bg-orange-200 text-orange-800' 
                  : 'bg-blue-200 text-blue-800'
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
                <div className={`flex-shrink-0 w-8 h-8 rounded-lg bg-gradient-to-br from-${color}-400 to-${color}-600 flex items-center justify-center text-white shadow-sm`}>
                  <IconComponent className="h-4 w-4" />
                </div>
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
            <div className="text-center pt-2 border-t border-gray-200">
              <span className={`text-xs font-medium px-3 py-1 rounded-full ${
                scenario.type === 'Alternative' 
                  ? 'bg-orange-100 text-orange-700 border border-orange-200' 
                  : 'bg-blue-100 text-blue-700 border border-blue-200'
              }`}>
                +{priorityStepOrder.filter(key => scenario[key]).length - 4} more steps
              </span>
            </div>
          )}
        </div>

        {/* Selection indicator */}
        {isSelected && (
          <div className="absolute top-3 right-3">
            <div className="w-6 h-6 bg-blue-500 rounded-full flex items-center justify-center shadow-lg">
              <svg className="w-4 h-4 text-white" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
              </svg>
            </div>
          </div>
        )}
      </div>
    );
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-100">
      <div className="max-w-7xl mx-auto px-6 py-8">
        {/* Header */}
        <div className="mb-8">
          <div className="flex items-center justify-between mb-6">
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
                <p className="text-sm text-gray-500">Build, customize, and export attack scenarios</p>
              </div>
            </div>
            <button
              onClick={() => setViewMode(viewMode === 'builder' ? 'scenarios' : 'builder')}
              className={`flex items-center space-x-2 px-6 py-3 rounded-xl font-semibold transition-all duration-300 shadow-lg hover:shadow-xl ${
                viewMode === 'scenarios' 
                  ? 'bg-gradient-to-r from-blue-600 to-indigo-600 text-white hover:from-blue-700 hover:to-indigo-700' 
                  : 'bg-white text-blue-600 border-2 border-blue-200 hover:border-blue-300 hover:bg-blue-50'
              }`}
            >
              {viewMode === 'builder' ? <FileText className="h-5 w-5" /> : <Play className="h-5 w-5" />}
              <span>{viewMode === 'builder' ? 'View Scenarios' : 'Back to Builder'}</span>
            </button>
          </div>
        </div>

        {viewMode === 'builder' ? (
          <>
            {/* Statistics Dashboard */}
            <div className="grid grid-cols-2 md:grid-cols-4 gap-6 mb-8">
              {[
                { title: "Attack Steps", value: stepKeys.length, color: "blue", icon: AlertTriangle },
                { title: "Selected", value: Object.keys(selectedValues).length, color: "green", icon: Eye },
                { title: "Variations", value: stepKeys.reduce((sum, key) => sum + attackSteps[key].length, 0), color: "purple", icon: Shuffle },
                { title: "Scenarios", value: allScenarios.length, color: "orange", icon: FileText }
              ].map((stat, index) => (
                <div key={index} className={`bg-white rounded-2xl p-6 shadow-lg border border-gray-100 hover:shadow-xl transition-all duration-300`}>
                  <div className="flex items-center justify-between mb-4">
                    <div className={`w-12 h-12 bg-gradient-to-br from-${stat.color}-400 to-${stat.color}-600 rounded-xl flex items-center justify-center shadow-lg`}>
                      <stat.icon className="h-6 w-6 text-white" />
                    </div>
                    <span className={`text-3xl font-bold bg-gradient-to-r from-${stat.color}-600 to-${stat.color}-700 bg-clip-text text-transparent`}>
                      {stat.value}
                    </span>
                  </div>
                  <h3 className="font-semibold text-gray-800">{stat.title}</h3>
                </div>
              ))}
            </div>

            {/* Action Buttons */}
            <div className="flex justify-end space-x-3 mb-8">
              <button
                onClick={selectAllRandom}
                className="flex items-center space-x-2 bg-gradient-to-r from-green-500 to-emerald-600 text-white px-6 py-3 rounded-xl font-semibold hover:from-green-600 hover:to-emerald-700 transition-all duration-300 shadow-lg hover:shadow-xl"
              >
                <Shuffle className="h-5 w-5" />
                <span>Randomize All</span>
              </button>
              <button
                onClick={resetSelections}
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
                    const IconComponent = getStepIcon(key);
                    return (
                      selectedValues[key] && (
                        <div key={key} className="flex items-start space-x-4 bg-white rounded-xl p-4 shadow-sm border border-gray-100">
                          <div className={`w-10 h-10 rounded-xl bg-gradient-to-br from-${getStepColor(index)}-400 to-${getStepColor(index)}-600 flex items-center justify-center flex-shrink-0 shadow-md`}>
                            <IconComponent className="h-5 w-5 text-white" />
                          </div>
                          <div className="flex-1 min-w-0">
                            <span className={`font-semibold text-${getStepColor(index)}-700 text-sm block mb-1`}>
                              {stepConfig[key].label}
                            </span>
                            <p className="text-gray-700 text-sm leading-relaxed break-words">{selectedValues[key]}</p>
                          </div>
                        </div>
                      )
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
                />
              ))}
            </div>
          </>
        ) : (
          <>
            {/* Scenarios Header */}
            <div className="bg-white rounded-2xl p-6 shadow-lg border border-gray-100 mb-8">
              <div className="flex justify-between items-center mb-6">
                <div>
                  <h2 className="text-3xl font-bold text-gray-900 mb-2">Generated Scenarios</h2>
                  <p className="text-gray-600">Select and export the scenarios you need</p>
                </div>
                <div className="flex items-center space-x-4">
                  <div className="flex items-center space-x-4 text-sm">
                    <div className="flex items-center space-x-2">
                      <div className="w-4 h-4 bg-gradient-to-r from-blue-500 to-blue-600 rounded-full"></div>
                      <span className="font-medium text-gray-700">Primary ({allScenarios.filter(s => s.type === 'Primary').length})</span>
                    </div>
                    <div className="flex items-center space-x-2">
                      <div className="w-4 h-4 bg-gradient-to-r from-orange-500 to-orange-600 rounded-full"></div>
                      <span className="font-medium text-gray-700">Alternative ({allScenarios.filter(s => s.type === 'Alternative').length})</span>
                    </div>
                  </div>
                  <div className="flex items-center space-x-3">
                    <div className="bg-gray-100 rounded-lg px-4 py-2">
                      <span className="text-sm font-semibold text-gray-700">
                        {scenarioSelection.size} selected
                      </span>
                    </div>
                    <button
                      onClick={exportSelectedScenarios}
                      disabled={scenarioSelection.size === 0}
                      className="flex items-center space-x-2 bg-gradient-to-r from-blue-600 to-indigo-600 text-white px-6 py-3 rounded-xl font-semibold hover:from-blue-700 hover:to-indigo-700 transition-all duration-300 shadow-lg hover:shadow-xl disabled:from-gray-400 disabled:to-gray-500 disabled:cursor-not-allowed"
                    >
                      <Download className="h-5 w-5" />
                      <span>Export Selected</span>
                    </button>
                  </div>
                </div>
              </div>
            </div>

            {/* Scenarios Grid */}
            <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-6">
              {allScenarios.map(scenario => (
                <ScenarioCard key={scenario.id} scenario={scenario} />
              ))}
            </div>
          </>
        )}
      </div>

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