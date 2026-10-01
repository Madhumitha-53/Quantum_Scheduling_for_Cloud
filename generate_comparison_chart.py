import os
import time
import random
import numpy as np
import matplotlib.pyplot as plt
from app.core.scheduler_engine import QuantumCarbonAwareScheduler

def generate_chart():
    print("====================================================")
    print("GENERATING CLASSICAL VS QUANTUM COMPARISON LINE CHART")
    print("====================================================")

    task_count = 2000
    num_runs = 30
    seed = 42
    provider_count = 4

    algos = ["Classical", "Quantum-Inspired"]
    run_results = {algo: [] for algo in algos}

    print(f"Executing {num_runs} evaluation runs for {task_count} tasks...")
    for run_idx in range(num_runs):
        current_seed = seed + run_idx
        random.seed(current_seed)
        np.random.seed(current_seed)

        engine = QuantumCarbonAwareScheduler()
        tasks = [{"id": tid, "cpu": random.randint(1, 8), "memory": random.randint(2, 32), "sla": random.randint(20, 50)} for tid in range(task_count)]

        # Classical
        engine.reset_state(provider_count)
        start = time.perf_counter()
        res_c = engine.run_classical_mo(tasks, provider_count)
        rt_c = time.perf_counter() - start
        valid_c = [x for x in res_c if "error" not in x]
        cost_c = sum(x["cost"] for x in valid_c)
        carb_c = sum(x["carbon"] for x in valid_c)
        sla_c = sum(1 for x in valid_c if x["sla_satisfied"]) / len(valid_c)
        loads_c = list(engine.provider_loads.values())
        cv_c = np.std(loads_c) / np.mean(loads_c) if np.mean(loads_c) > 1e-4 else 0
        run_results["Classical"].append([cost_c, carb_c, sla_c * 100, cv_c, rt_c])

        # Quantum-Inspired
        engine.reset_state(provider_count)
        start = time.perf_counter()
        res_q = engine.run_quantum_inspired(tasks, provider_count)
        rt_q = time.perf_counter() - start
        valid_q = [x for x in res_q if "error" not in x]
        cost_q = sum(x["cost"] for x in valid_q)
        carb_q = sum(x["carbon"] for x in valid_q)
        sla_q = sum(1 for x in valid_q if x["sla_satisfied"]) / len(valid_q)
        loads_q = list(engine.provider_loads.values())
        cv_q = np.std(loads_q) / np.mean(loads_q) if np.mean(loads_q) > 1e-4 else 0
        run_results["Quantum-Inspired"].append([cost_q, carb_q, sla_q * 100, cv_q, rt_q])

    # Compute means and stds
    metrics = ["Cost ($)", "Carbon (kg)", "SLA (%)", "Load CV", "Runtime (s)"]
    c_data = np.array(run_results["Classical"])
    q_data = np.array(run_results["Quantum-Inspired"])

    c_means = np.mean(c_data, axis=0)
    c_stds = np.std(c_data, axis=0)
    q_means = np.mean(q_data, axis=0)
    q_stds = np.std(q_data, axis=0)

    # Plotting Line Chart
    fig, ax = plt.subplots(figsize=(10, 6))

    ax.errorbar(metrics, c_means, yerr=c_stds, marker='o', linestyle='-', linewidth=2, capsize=5, label='Classical MO', color='#34495e')
    ax.errorbar(metrics, q_means, yerr=q_stds, marker='s', linestyle='--', linewidth=2, capsize=5, label='Proposed Quantum-Inspired', color='#2ecc71')

    ax.set_ylabel('Metric Value')
    ax.set_title('Classical vs. Proposed Quantum-Inspired Scheduler Performance (2000 Tasks, 30 Runs)')
    ax.legend(loc='best')
    ax.grid(True, linestyle='--', alpha=0.7)

    plt.tight_layout()
    chart_path = "comparison_chart.png"
    plt.savefig(chart_path, dpi=300)
    print(f"\nLine chart successfully generated and saved to: {os.path.abspath(chart_path)}")
    print("====================================================")

if __name__ == "__main__":
    generate_chart()
