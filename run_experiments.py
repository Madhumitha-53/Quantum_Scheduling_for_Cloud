import os
import time
import random
import numpy as np
import pandas as pd
from app.core.scheduler_engine import QuantumCarbonAwareScheduler

# Experimental configuration per Reviewer 1/2/3
TASK_COUNTS = [50, 100, 250, 500, 1000, 2000]
NUM_RUNS = 30
SEED = 42
DEFAULT_PROVIDER_COUNT = 4

def generate_identical_tasks(count, seed):
    random.seed(seed)
    tasks = []
    for i in range(count):
        tasks.append({
            "id": i,
            "cpu": random.randint(1, 8),
            "memory": random.randint(2, 32),
            "sla": random.randint(20, 50)
        })
    return tasks

def compute_metrics(res, engine):
    if not res: return [0]*5
    valid = [x for x in res if "error" not in x]
    if not valid: return [0]*5

    cost = sum(x["cost"] for x in valid)
    carbon = sum(x["carbon"] for x in valid)
    sla = sum(1 for x in valid if x["sla_satisfied"]) / len(valid)

    loads = list(engine.provider_loads.values())
    avg_load = np.mean(loads)
    cv = np.std(loads) / avg_load if avg_load > 1e-4 else 0
    return [cost, carbon, sla, cv]

def run_scalability_suite():
    print(f"Starting Multi-Run Research Scalability Suite (Runs: {NUM_RUNS})...")
    os.makedirs("results/scalability", exist_ok=True)

    engine = QuantumCarbonAwareScheduler()
    algorithms = ["Classical", "Quantum-Inspired", "FCFS", "Min-Min"]

    summary_data = []

    for count in TASK_COUNTS:
        print(f" - Evaluating Scale: {count} Tasks")

        # For very high scales, we use 10 runs to keep runtime reasonable in demo
        current_runs = 10 if count >= 1000 else NUM_RUNS

        run_results = {algo: [] for algo in algorithms}

        for run_idx in range(current_runs):
            tasks = generate_identical_tasks(count, SEED + run_idx)

            for algo in algorithms:
                engine.reset_state(provider_count=DEFAULT_PROVIDER_COUNT)
                start = time.perf_counter()

                if algo == "Classical": res = engine.run_classical_mo(tasks, provider_count=DEFAULT_PROVIDER_COUNT)
                elif algo == "Quantum-Inspired": res = engine.run_quantum_inspired(tasks, provider_count=DEFAULT_PROVIDER_COUNT)
                elif algo == "FCFS": res = engine.run_fcfs(tasks, provider_count=DEFAULT_PROVIDER_COUNT)
                elif algo == "Min-Min": res = engine.run_min_min(tasks, provider_count=DEFAULT_PROVIDER_COUNT)

                runtime = time.perf_counter() - start
                metrics = compute_metrics(res, engine)
                run_results[algo].append(metrics + [runtime])

        for algo in algorithms:
            data = np.array(run_results[algo])
            means = np.mean(data, axis=0)
            stds = np.std(data, axis=0)

            summary_data.append({
                "Tasks": count,
                "Algorithm": algo,
                "Cost_mean": means[0], "Cost_std": stds[0],
                "Carbon_mean": means[1], "Carbon_std": stds[1],
                "SLA_mean": means[2], "SLA_std": stds[2],
                "CV_mean": means[3], "CV_std": stds[3],
                "Runtime_mean": means[4], "Runtime_std": stds[4]
            })

    df = pd.DataFrame(summary_data)
    df.to_csv("results/scalability/scalability_full_report.csv", index=False)
    print("\nScalability Evaluation Completed. Saved to results/scalability/scalability_full_report.csv")

if __name__ == "__main__":
    run_scalability_suite()
