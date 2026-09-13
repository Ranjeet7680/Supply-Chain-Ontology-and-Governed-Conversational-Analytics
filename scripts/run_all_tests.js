/**
 * All-Function Test Runner for SupplyChain IQ (invoked via `npm test`)
 * Executes all function test suites:
 * 1. Python Unit Test Suite (tests/test_solution.py)
 * 2. CoCo Skill Ontology Validator (.coco/skills/)
 * 3. Cross-Persona Metric Reconciliation (engine/persona_resolver.py)
 * 4. Machine Learning Inference Engine (ml/predictor.py)
 * 5. Model Context Protocol Server (mcp/supplychain_mcp_server.py)
 * 6. Cortex Analyst Governed Query Engine (engine/governed_cortex_engine.py)
 */

const { execSync } = require('child_process');

console.log("\n================================================================================");
console.log("⚡ SUPPLYCHAIN IQ — ALL-FUNCTION TEST SUITE (NPM TEST RUNNER)");
console.log("================================================================================\n");

const tests = [
  {
    name: "1. Python Unit Test Suite (7 Core Assertions)",
    command: 'python -m unittest discover -s tests -p "test_*.py"'
  },
  {
    name: "2. CoCo Skill Canonical Ontology Validator",
    command: "python .coco/skills/supplychain-ontology-validator/validate_ontology.py --dir data/bridged"
  },
  {
    name: "3. Cross-Persona Metric Reconciliation Engine",
    command: "python engine/persona_resolver.py"
  },
  {
    name: "4. Machine Learning Inference & Explainability Engine",
    command: "python ml/predictor.py"
  },
  {
    name: "5. MCP Server Cross-System Function Calling",
    command: "python mcp/supplychain_mcp_server.py"
  },
  {
    name: "6. Snowflake Cortex Analyst Governed Conversational Query Engine",
    command: "python engine/governed_cortex_engine.py"
  }
];

let passedCount = 0;
const startTime = Date.now();

for (const t of tests) {
  console.log(`\n>>> EXECUTING: ${t.name}`);
  console.log(`    Command: ${t.command}`);
  try {
    execSync(t.command, { stdio: 'inherit', shell: true });
    console.log(`[+] PASSED: ${t.name}`);
    passedCount++;
  } catch (err) {
    console.error(`[-] FAILED: ${t.name}`);
    process.exit(1);
  }
}

const totalDuration = ((Date.now() - startTime) / 1000).toFixed(2);

console.log("\n================================================================================");
console.log(`🎉 ALL FUNCTION TESTS PASSED (${passedCount}/${tests.length} TEST SUITES) IN ${totalDuration}s`);
console.log("================================================================================\n");
