import React, { useState, useMemo } from 'react';
import { Download, Shield, AlertTriangle, Eye, EyeOff } from 'lucide-react';

const AttackScenarioGenerator = () => {
  const [showDetails, setShowDetails] = useState(false);
  const [selectedScenario, setSelectedScenario] = useState(null);
  const [filterByStep, setFilterByStep] = useState('all');

  // Define attack steps and their variants
  const attackSteps = {
    initialAccess: [
      "Phishing email/message with website link",
      "Phishing email/message with .exe file",
      "Phishing email/message with fake installer (game update)",
      "Phishing email/message with payload bound to image/pdf/doc",
      "Watering hole attack on compromised website",
      "USB drop attack with malicious payload",
      "Supply chain compromise through software update"
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
      "Cloud Drive exfiltration",
      "RAT server exfiltration",
      "OneDrive exfiltration",
      "Mega exfiltration",
      "FTP exfiltration",
      "GitHub exfiltration"
    ],
    lateralMovement: [
      null, // No lateral movement
      "Windows SMB lateral movement",
      "Internal spear phishing"
    ],
    finalPayload: [
      "System wipeout",
      "Data theft",
      "Ransomware deployment"
    ],
    postAttackCleanup: [
      "Leaving no trace (stealth cleanup)",
      "Leaving identifiable traces (attribution/confusion)"
    ]
  };

  // Generate all possible combinations
  const scenarios = useMemo(() => {
    const combinations = [];
    let scenarioId = 1;

    attackSteps.initialAccess.forEach(initial => {
      attackSteps.credentialHarvesting.forEach(cred => {
        attackSteps.attackerControl.forEach(control => {
          attackSteps.persistence.forEach(persist => {
            attackSteps.dataExfiltration.forEach(exfil => {
              attackSteps.lateralMovement.forEach(lateral => {
                attackSteps.finalPayload.forEach(payload => {
                  attackSteps.postAttackCleanup.forEach(cleanup => {
                    combinations.push({
                      id: scenarioId++,
                      initialAccess: initial,
                      credentialHarvesting: cred,
                      attackerControl: control,
                      persistence: persist,
                      dataExfiltration: exfil,
                      lateralMovement: lateral,
                      finalPayload: payload,
                      postAttackCleanup: cleanup,
                      hasLateralMovement: lateral !== null
                    });
                  });
                });
              });
            });
          });
        });
      });
    });

    return combinations;
  }, []);

  // Filter scenarios based on selected criteria
  const filteredScenarios = useMemo(() => {
    if (filterByStep === 'all') return scenarios;
    if (filterByStep === 'with-lateral') return scenarios.filter(s => s.hasLateralMovement);
    if (filterByStep === 'without-lateral') return scenarios.filter(s => !s.hasLateralMovement);
    return scenarios;
  }, [scenarios, filterByStep]);

  const exportToCSV = () => {
    const headers = [
      'Scenario ID',
      'Initial Access',
      'Credential Harvesting',
      'Attacker Control',
      'Persistence',
      'Data Exfiltration',
      'Lateral Movement',
      'Final Payload',
      'Post-Attack Cleanup'
    ];

    const csvContent = [
      headers.join(','),
      ...filteredScenarios.map(scenario => [
        scenario.id,
        `"${scenario.initialAccess}"`,
        `"${scenario.credentialHarvesting}"`,
        `"${scenario.attackerControl}"`,
        `"${scenario.persistence}"`,
        `"${scenario.dataExfiltration}"`,
        `"${scenario.lateralMovement || 'None'}"`,
        `"${scenario.finalPayload}"`,
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

  const ScenarioCard = ({ scenario }) => (
    <div className="bg-white border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow">
      <div className="flex justify-between items-start mb-3">
        <h3 className="font-semibold text-lg text-gray-800">Scenario #{scenario.id}</h3>
        <div className="flex space-x-2">
          {scenario.hasLateralMovement && (
            <span className="bg-red-100 text-red-800 text-xs px-2 py-1 rounded">
              Lateral Movement
            </span>
          )}
          <span className="bg-blue-100 text-blue-800 text-xs px-2 py-1 rounded">
            {scenario.finalPayload}
          </span>
        </div>
      </div>
      
      <div className="space-y-2 text-sm">
        <div><span className="font-medium text-red-600">Initial Access:</span> {scenario.initialAccess}</div>
        <div><span className="font-medium text-orange-600">Credentials:</span> {scenario.credentialHarvesting}</div>
        <div><span className="font-medium text-yellow-600">Control:</span> {scenario.attackerControl}</div>
        <div><span className="font-medium text-green-600">Persistence:</span> {scenario.persistence}</div>
        <div><span className="font-medium text-blue-600">Exfiltration:</span> {scenario.dataExfiltration}</div>
        {scenario.lateralMovement && (
          <div><span className="font-medium text-purple-600">Lateral Movement:</span> {scenario.lateralMovement}</div>
        )}
        <div><span className="font-medium text-pink-600">Final Action:</span> {scenario.finalPayload}</div>
        <div><span className="font-medium text-gray-600">Cleanup:</span> {scenario.postAttackCleanup}</div>
      </div>
    </div>
  );

  return (
    <div className="max-w-7xl mx-auto p-6 bg-gray-50 min-h-screen">
      <div className="mb-8">
        <div className="flex items-center space-x-3 mb-4">
          <Shield className="h-8 w-8 text-blue-600" />
          <h1 className="text-3xl font-bold text-gray-900">MITRE ATT&CK Attack Scenario Generator</h1>
        </div>
        <p className="text-gray-600">
          Comprehensive simulation of attack scenarios based on your defined attack chain. 
          Generate all possible permutations for security planning and threat modeling.
        </p>
      </div>

      {/* Statistics and Controls */}
      <div className="bg-white rounded-lg p-6 mb-6 shadow-sm">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
          <div className="bg-blue-50 p-4 rounded-lg">
            <h3 className="font-semibold text-blue-800">Total Scenarios</h3>
            <p className="text-2xl font-bold text-blue-600">{scenarios.length}</p>
          </div>
          <div className="bg-green-50 p-4 rounded-lg">
            <h3 className="font-semibold text-green-800">With Lateral Movement</h3>
            <p className="text-2xl font-bold text-green-600">
              {scenarios.filter(s => s.hasLateralMovement).length}
            </p>
          </div>
          <div className="bg-yellow-50 p-4 rounded-lg">
            <h3 className="font-semibold text-yellow-800">Without Lateral Movement</h3>
            <p className="text-2xl font-bold text-yellow-600">
              {scenarios.filter(s => !s.hasLateralMovement).length}
            </p>
          </div>
          <div className="bg-purple-50 p-4 rounded-lg">
            <h3 className="font-semibold text-purple-800">Attack Steps</h3>
            <p className="text-2xl font-bold text-purple-600">8</p>
          </div>
        </div>

        <div className="flex flex-wrap items-center gap-4">
          <div className="flex items-center space-x-2">
            <label className="font-medium text-gray-700">Filter:</label>
            <select 
              value={filterByStep} 
              onChange={(e) => setFilterByStep(e.target.value)}
              className="border border-gray-300 rounded px-3 py-1 focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="all">All Scenarios</option>
              <option value="with-lateral">With Lateral Movement</option>
              <option value="without-lateral">Without Lateral Movement</option>
            </select>
          </div>
          
          <button
            onClick={exportToCSV}
            className="flex items-center space-x-2 bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700 transition-colors"
          >
            <Download className="h-4 w-4" />
            <span>Export CSV</span>
          </button>

          <button
            onClick={() => setShowDetails(!showDetails)}
            className="flex items-center space-x-2 bg-gray-600 text-white px-4 py-2 rounded hover:bg-gray-700 transition-colors"
          >
            {showDetails ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
            <span>{showDetails ? 'Hide' : 'Show'} Details</span>
          </button>
        </div>
      </div>

      {/* Attack Chain Overview */}
      <div className="bg-white rounded-lg p-6 mb-6 shadow-sm">
        <h2 className="text-xl font-bold text-gray-900 mb-4 flex items-center">
          <AlertTriangle className="h-5 w-5 text-yellow-500 mr-2" />
          Attack Chain Overview
        </h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          <div className="bg-red-50 p-3 rounded border-l-4 border-red-400">
            <h4 className="font-semibold text-red-800">1. Initial Access</h4>
            <p className="text-sm text-red-600">{attackSteps.initialAccess.length} variants</p>
          </div>
          <div className="bg-orange-50 p-3 rounded border-l-4 border-orange-400">
            <h4 className="font-semibold text-orange-800">2. Credential Harvesting</h4>
            <p className="text-sm text-orange-600">{attackSteps.credentialHarvesting.length} method</p>
          </div>
          <div className="bg-yellow-50 p-3 rounded border-l-4 border-yellow-400">
            <h4 className="font-semibold text-yellow-800">3. Attacker Control</h4>
            <p className="text-sm text-yellow-600">{attackSteps.attackerControl.length} timing variants</p>
          </div>
          <div className="bg-green-50 p-3 rounded border-l-4 border-green-400">
            <h4 className="font-semibold text-green-800">4. Persistence</h4>
            <p className="text-sm text-green-600">{attackSteps.persistence.length} techniques</p>
          </div>
          <div className="bg-blue-50 p-3 rounded border-l-4 border-blue-400">
            <h4 className="font-semibold text-blue-800">5. Data Exfiltration</h4>
            <p className="text-sm text-blue-600">{attackSteps.dataExfiltration.length} channels</p>
          </div>
          <div className="bg-purple-50 p-3 rounded border-l-4 border-purple-400">
            <h4 className="font-semibold text-purple-800">6. Lateral Movement</h4>
            <p className="text-sm text-purple-600">{attackSteps.lateralMovement.length - 1} techniques (optional)</p>
          </div>
          <div className="bg-pink-50 p-3 rounded border-l-4 border-pink-400">
            <h4 className="font-semibold text-pink-800">7. Final Payload</h4>
            <p className="text-sm text-pink-600">{attackSteps.finalPayload.length} actions</p>
          </div>
          <div className="bg-gray-50 p-3 rounded border-l-4 border-gray-400">
            <h4 className="font-semibold text-gray-800">8. Post-Attack Cleanup</h4>
            <p className="text-sm text-gray-600">{attackSteps.postAttackCleanup.length} approaches</p>
          </div>
        </div>
      </div>

      {/* Scenarios Display */}
      <div className="bg-white rounded-lg p-6 shadow-sm">
        <h2 className="text-xl font-bold text-gray-900 mb-4">
          Generated Attack Scenarios ({filteredScenarios.length})
        </h2>
        
        {showDetails ? (
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
            {filteredScenarios.map(scenario => (
              <ScenarioCard key={scenario.id} scenario={scenario} />
            ))}
          </div>
        ) : (
          <div className="space-y-2">
            {filteredScenarios.slice(0, 10).map(scenario => (
              <div key={scenario.id} className="flex items-center justify-between p-3 bg-gray-50 rounded border">
                <div className="flex items-center space-x-4">
                  <span className="font-semibold text-gray-700">#{scenario.id}</span>
                  <span className="text-sm text-gray-600">{scenario.initialAccess}</span>
                  <span className="text-sm text-gray-500">→</span>
                  <span className="text-sm text-gray-600">{scenario.finalPayload}</span>
                </div>
                {scenario.hasLateralMovement && (
                  <span className="bg-red-100 text-red-800 text-xs px-2 py-1 rounded">Lateral</span>
                )}
              </div>
            ))}
            {filteredScenarios.length > 10 && (
              <div className="text-center py-4">
                <p className="text-gray-500">
                  Showing 10 of {filteredScenarios.length} scenarios. 
                  <button 
                    onClick={() => setShowDetails(true)}
                    className="text-blue-600 hover:underline ml-1"
                  >
                    Show all details
                  </button>
                </p>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
};

export default AttackScenarioGenerator;