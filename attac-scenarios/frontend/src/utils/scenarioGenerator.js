import { attackSteps } from "./attackData";

export const generateAllScenarios = () => {
  const scenarios = [];
  let scenarioId = 1;

  // Generate primary scenarios (with required defaults) - limited to 200
  const maxPrimaryScenarios = 2000;
  const maxInitialAccessForPrimary = Math.min(
    10,
    attackSteps.initialAccess.length
  );

  attackSteps.initialAccess
    .slice(0, maxInitialAccessForPrimary)
    .forEach((initialAccess) => {
      // Base scenario with required steps only
      const baseScenario = {
        id: scenarioId++,
        type: "Primary",
        initialAccess,
        attackerControl: attackSteps.attackerControl[0], // First one is compulsory
        postAttackCleanup: attackSteps.postAttackCleanup[0], // First one is compulsory
      };

      // Add base scenario
      scenarios.push(baseScenario);

      if (scenarios.length >= maxPrimaryScenarios) return;

      // Generate limited combinations with optional steps
      const optionalSteps = [
        "operationAfterInitialAccess",
        "credentialHarvesting",
        "persistence",
        "dataExfiltration",
        "lateralMovement",
        "finalPayload",
      ];

      // Add single optional step scenarios
      optionalSteps.forEach((stepKey) => {
        if (scenarios.length >= maxPrimaryScenarios) return;
        attackSteps[stepKey].forEach((variation) => {
          if (scenarios.length >= maxPrimaryScenarios) return;
          scenarios.push({
            ...baseScenario,
            id: scenarioId++,
            [stepKey]: variation,
          });
        });
      });

      // Add a few combinations with 2 optional steps
      if (scenarios.length < maxPrimaryScenarios - 10) {
        ["credentialHarvesting", "dataExfiltration"].forEach((step1) => {
          ["persistence", "finalPayload"].forEach((step2) => {
            if (scenarios.length >= maxPrimaryScenarios) return;
            attackSteps[step1].forEach((var1) => {
              attackSteps[step2].forEach((var2) => {
                if (scenarios.length >= maxPrimaryScenarios) return;
                scenarios.push({
                  ...baseScenario,
                  id: scenarioId++,
                  [step1]: var1,
                  [step2]: var2,
                });
              });
            });
          });
        });
      }
    });

  // Generate alternative scenarios (limited to 50 total)
  const maxAlternativeScenarios = Math.min(50, 2000 - scenarios.length);
  const remainingInitialAccess = attackSteps.initialAccess.slice(
    maxInitialAccessForPrimary
  );

  remainingInitialAccess
    .slice(0, Math.min(5, remainingInitialAccess.length))
    .forEach((initialAccess) => {
      if (scenarios.length >= 2000) return;

      // Create alternative scenarios with different combinations
      const alternativeSteps = [
        "credentialHarvesting",
        "dataExfiltration",
        "finalPayload",
      ];
      alternativeSteps.forEach((stepKey) => {
        if (scenarios.length >= 2000) return;
        attackSteps[stepKey].forEach((variation) => {
          if (scenarios.length >= 2000) return;
          scenarios.push({
            id: scenarioId++,
            type: "Alternative",
            initialAccess,
            attackerControl:
              attackSteps.attackerControl[1] || attackSteps.attackerControl[0],
            [stepKey]: variation,
          });
        });
      });
    });

  return scenarios.slice(0, 2000); // Ensure we don't exceed 2000 scenarios
};
