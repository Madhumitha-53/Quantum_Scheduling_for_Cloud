import sys
import random
import numpy as np
from app.core.scheduler_engine import QuantumCarbonAwareScheduler

def run_research_validation():
    print("Executing Research Workflow and Logic Integrity Check...")
    engine = QuantumCarbonAwareScheduler()

    # Use identical parameters as dashboard default
    tasks_data = [
        {"cpu": 4, "memory": 16, "sla": 30},
        {"cpu": 2, "memory": 8, "sla": 20},
        {"cpu": 8, "memory": 32, "sla": 40}
    ]

    # 1. Workflow Preservation Check
    engine.reset_state(provider_count=4)
    for t in tasks_data: engine.add_task(t)
    task_stack = engine.get_stack()

    # 2. Mathematical Consistency Check (Weights Sum = 1.0)
    random.seed(42)
    res = engine.run_quantum_inspired(task_stack, provider_count=4)

    weight_sum = sum(engine.weights.values())

    # 3. Allocation consistency check
    provider_names = list(engine.active_providers.keys())
    allocation_providers = [x["selected_provider"] for x in res if "selected_provider" in x]

    validations = {
        "Adaptive Weights sum exactly to 1.0000": abs(weight_sum - 1.0) < 1e-6,
        "All weights are strictly positive (>=0.05)": all(v >= 0.05 for v in engine.weights.values()),
        "Task count in allocation matches input": len(res) == len(tasks_data),
        "SLA Satisfaction mapped correctly": all(isinstance(x["sla_satisfied"], bool) for x in res),
        "Quantum Probabilities are normalized": all(abs(sum(x["quantum_details"]["probs_all"].values()) - 1.0) < 1e-5 for x in res),
        "Cost and Carbon are strictly positive": all(x["cost"] > 0 and x["carbon"] > 0 for x in res),
        "Provider IDs in results are valid": all(p in provider_names for p in allocation_providers)
    }

    all_passed = True
    print("\nIndividual Constraint Validations:")
    for desc, status in validations.items():
        label = "PASS" if status else "FAIL"
        if not status: all_passed = False
        print(f" - [{label}] {desc}")

    if all_passed:
        print("\nSUCCESS: All core research logic and mathematical constraints validated.")
        sys.exit(0)
    else:
        print("\nFAILURE: Logic inconsistencies detected.")
        sys.exit(1)

if __name__ == "__main__":
    run_research_validation()
