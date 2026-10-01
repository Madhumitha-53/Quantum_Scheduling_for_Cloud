import time
import random
import numpy as np
import pandas as pd
from scipy import stats
from app.core.scheduler_engine import QuantumCarbonAwareScheduler
from app.core.canonical_benchmark import run_canonical_benchmark
from aws_validation import run_aws_validation

TASK_COUNT = 2000
NUM_RUNS = 30
SEED = 42
DEFAULT_PROVIDER_COUNT = 4

def run_evaluation():
    print("====================================================")
    print("PROTOTYPE EVALUATION REPORT (IEEE Camera-Ready)")
    print("====================================================")

    print("\n----------------------------------------------------")
    print("1. EXPERIMENT CONFIGURATION")
    print("----------------------------------------------------")
    print(f"Benchmark Task Count: {TASK_COUNT}")
    print(f"Statistical Runs: {NUM_RUNS}")
    print(f"Random Seed: {SEED}")
    print(f"Number of Simulated Providers: {DEFAULT_PROVIDER_COUNT}")

    print(f"\nExecuting {NUM_RUNS}-run evaluation suite for {TASK_COUNT} tasks...")
    bench_result = run_canonical_benchmark(
        task_count=TASK_COUNT,
        provider_count=DEFAULT_PROVIDER_COUNT,
        num_runs=NUM_RUNS,
        seed=SEED
    )

    print("\n----------------------------------------------------")
    print("2. STATISTICAL PERFORMANCE ANALYSIS (Mean ± Std)")
    print("----------------------------------------------------")
    print(f"{'Algorithm':<20} {'Cost ($)':<18} {'Carbon (kg)':<18} {'SLA (%)':<15} {'Load CV':<15} {'Runtime (s)':<15}")

    for algo, stats_dict in bench_result["summary"].items():
        print(f"{algo:<20} {stats_dict['cost']:<18} {stats_dict['carbon']:<18} {stats_dict['sla']:<15} {stats_dict['cv']:<15} {stats_dict['runtime']:<15}")

    print("\n----------------------------------------------------")
    print("3. STATISTICAL SIGNIFICANCE ANALYSIS (Wilcoxon Signed-Rank Test vs Proposed)")
    print("----------------------------------------------------")
    print(f"{'Comparison (Proposed vs)':<25} {'Cost p-value':<15} {'Carbon p-value':<15} {'SLA p-value':<15} {'Load CV p-value':<15}")

    q_data = np.array(bench_result["raw_results"]["Quantum-Inspired"])
    for comp_algo in ["Classical", "FCFS", "Round Robin", "Min-Min"]:
        c_data = np.array(bench_result["raw_results"][comp_algo])
        p_vals = []
        for m_idx in range(4):
            try:
                stat, pval = stats.wilcoxon(q_data[:, m_idx], c_data[:, m_idx])
            except:
                pval = 1.0
            p_vals.append(f"{pval:.4e}" if pval < 0.001 else f"{pval:.4f}")
        print(f"{'Quantum vs ' + comp_algo:<25} {p_vals[0]:<15} {p_vals[1]:<15} {p_vals[2]:<15} {p_vals[3]:<15}")

    print("\n----------------------------------------------------")
    print("4. SCALABILITY EVIDENCE (Dynamic Runtimes O(NM))")
    print("----------------------------------------------------")
    scales = [50, 100, 250, 500, 1000, 2000]
    engine = QuantumCarbonAwareScheduler()
    for s in scales:
        s_tasks = [{"id": tid, "cpu": random.randint(1, 8), "memory": random.randint(2, 32), "sla": random.randint(20, 50)} for tid in range(s)]
        start = time.perf_counter()
        engine.run_quantum_inspired(s_tasks, DEFAULT_PROVIDER_COUNT)
        runtime = time.perf_counter() - start
        print(f"Tasks: {s:<5} | Runtime: {runtime:.4f}s")

    print("\n----------------------------------------------------")
    print("5. ADAPTIVE WEIGHT VALIDATION")
    print("----------------------------------------------------")
    print(f"Initial Weights: [0.4, 0.3, 0.2, 0.1]")
    print(f"Final Weights: {list(bench_result['sample_weights'].values())}")
    print(f"Weight Sum: {sum(bench_result['sample_weights'].values()):.4f}")

    print("\n----------------------------------------------------")
    print("6. REAL AWS EC2 PROTOTYPE VALIDATION")
    print("----------------------------------------------------")
    run_aws_validation()

    print("====================================================")

if __name__ == "__main__":
    run_evaluation()
