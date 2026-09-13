"""
End-to-End Orchestration Runner for SupplyChain IQ (CoCo Lifecycle).
"""

import sys
import subprocess
import time

if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

def run_step(step_name, command):
    print(f"\n=======================================================")
    print(f"STEP: {step_name}")
    print(f"COMMAND: {command}")
    print(f"=======================================================")
    start = time.time()
    res = subprocess.run(command, shell=True)
    elapsed = round(time.time() - start, 2)
    if res.returncode != 0:
        print(f"[-] FAILED: {step_name} (Exit code {res.returncode})")
        sys.exit(res.returncode)
    print(f"[+] COMPLETED: {step_name} in {elapsed}s")

def main():
    print("\n[*] STARTING SUPPLYCHAIN IQ END-TO-END PIPELINE (CoCo Lifecyle)")

    # 1. Synthetic Bridging
    run_step("1. Synthetic Data Bridging", "python scripts/generate_synthetic_bridge.py")

    # 2. Ontology Governance Audit
    run_step("2. CoCo Skill Ontology Validator", "python .coco/skills/supplychain-ontology-validator/validate_ontology.py --dir data/bridged")

    # 3. Persona Reconciliation
    run_step("3. Persona Consistency Engine", "python engine/persona_resolver.py")

    # 4. Cortex Analyst Simulation
    run_step("4. Governed Cortex Analyst Simulation", "python engine/governed_cortex_engine.py")

    # 5. MCP Server Tools
    run_step("5. MCP Cross-Tool Function Calling", "python mcp/supplychain_mcp_server.py")

    # 6. Automated Verification Tests
    run_step("6. Automated Verification Test Suite", "python -m unittest discover -s tests -p \"test_*.py\"")

    print("\n[SUCCESS] ALL 6 PIPELINE STAGES COMPLETED SUCCESSFULLY!")
    print("Ready to launch Streamlit application: 'streamlit run app.py'\n")

if __name__ == "__main__":
    main()
