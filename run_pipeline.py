"""
End-to-End Orchestration Runner for SupplyChain IQ (CoCo Lifecycle + Snowpark ML).
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
    print("\n[*] STARTING SUPPLYCHAIN IQ END-TO-END PIPELINE (CoCo Lifecyle + ML)")

    # 1. Synthetic Bridging
    run_step("1. Synthetic Data Bridging", "python scripts/generate_synthetic_bridge.py")

    # 2. Machine Learning Training
    run_step("2. Snowpark ML Disruption & Delay Training", "python ml/train_models.py")

    # 3. Ontology Governance Audit
    run_step("3. CoCo Skill Ontology Validator", "python .coco/skills/supplychain-ontology-validator/validate_ontology.py --dir data/bridged")

    # 4. Persona Reconciliation
    run_step("4. Persona Consistency Engine", "python engine/persona_resolver.py")

    # 5. Cortex Analyst + ML Simulation
    run_step("5. Governed Cortex Analyst + ML Simulation", "python engine/governed_cortex_engine.py")

    # 6. MCP Server Tools
    run_step("6. MCP Cross-Tool & ML Function Calling", "python mcp/supplychain_mcp_server.py")

    # 7. Automated Verification Tests
    run_step("7. Automated Verification Test Suite", "python -m unittest discover -s tests -p \"test_*.py\"")

    print("\n[SUCCESS] ALL 7 PIPELINE STAGES (DATA + ML + GOVERNANCE) COMPLETED SUCCESSFULLY!")
    print("Ready to launch Streamlit application: 'streamlit run app.py'\n")

if __name__ == "__main__":
    main()
