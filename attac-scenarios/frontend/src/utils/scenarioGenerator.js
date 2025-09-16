import { attackSteps } from "./attackData";

export const generateAllScenarios = () => {
  const scenarios = [];
  let scenarioId = 1;

  // Generate all possible scenarios without limits
  attackSteps.initialAccess.forEach((initialAccess) => {
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

      // Generate all combinations with optional steps
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
        attackSteps[stepKey].forEach((variation) => {
          scenarios.push({
            ...baseScenario,
            id: scenarioId++,
            [stepKey]: variation,
          });
        });
      });

      // Add combinations with multiple optional steps
      optionalSteps.forEach((step1) => {
        optionalSteps.forEach((step2) => {
          if (step1 !== step2) {
            attackSteps[step1].forEach((var1) => {
              attackSteps[step2].forEach((var2) => {
                scenarios.push({
                  ...baseScenario,
                  id: scenarioId++,
                  [step1]: var1,
                  [step2]: var2,
                });
              });
            });
          }
        });
      });

      // Add combinations with three optional steps
      optionalSteps.forEach((step1) => {
        optionalSteps.forEach((step2) => {
          optionalSteps.forEach((step3) => {
            if (step1 !== step2 && step1 !== step3 && step2 !== step3) {
              attackSteps[step1].forEach((var1) => {
                attackSteps[step2].forEach((var2) => {
                  attackSteps[step3].forEach((var3) => {
                    scenarios.push({
                      ...baseScenario,
                      id: scenarioId++,
                      [step1]: var1,
                      [step2]: var2,
                      [step3]: var3,
                    });
                  });
                });
              });
            }
          });
        });
      });

      // Continue with 4, 5, and all 6 optional steps combinations
      // Generate all possible combinations systematically
      const generateCombinations = (arr, r) => {
        if (r === 1) return arr.map(x => [x]);
        const result = [];
        arr.forEach((item, index) => {
          const rest = arr.slice(index + 1);
          const combinations = generateCombinations(rest, r - 1);
          combinations.forEach(combo => {
            result.push([item, ...combo]);
          });
        });
        return result;
      };

      // Generate combinations for 4, 5, and 6 optional steps
      for (let r = 4; r <= 6; r++) {
        const combinations = generateCombinations(optionalSteps, r);
        combinations.forEach(stepCombination => {
          const generateVariations = (steps, index, currentScenario) => {
            if (index === steps.length) {
              scenarios.push({
                ...currentScenario,
                id: scenarioId++,
              });
              return;
            }
            
            const stepKey = steps[index];
            attackSteps[stepKey].forEach(variation => {
              generateVariations(steps, index + 1, {
                ...currentScenario,
                [stepKey]: variation,
              });
            });
          };
          
          generateVariations(stepCombination, 0, { ...baseScenario });
        });
      }
    });

  // Generate alternative scenarios with different control methods
  attackSteps.initialAccess.forEach((initialAccess) => {
    attackSteps.attackerControl.slice(1).forEach((controlMethod) => {

      // Create alternative scenarios with different combinations
      const alternativeSteps = [
        "credentialHarvesting",
        "dataExfiltration",
        "finalPayload",
      ];
      alternativeSteps.forEach((stepKey) => {
        attackSteps[stepKey].forEach((variation) => {
          scenarios.push({
            id: scenarioId++,
            type: "Alternative",
            initialAccess,
            attackerControl: controlMethod,
            [stepKey]: variation,
          });
        });
      });
    });
  });

  return scenarios;
};
