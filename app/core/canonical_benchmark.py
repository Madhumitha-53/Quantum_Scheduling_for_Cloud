import time
import random
import numpy as np
from scipy import stats
from app.core.scheduler_engine import QuantumCarbonAwareScheduler

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

def run_canonical_benchmark(task_count=2000, provider_count=4, num_runs=30, seed=42, weights=None):
    if weights is None:
        weights = {"cost": 0.4, "carbon": 0.3, "sla": 0.2, "renewable": 0.1}

    algos = ["Classical", "Quantum-Inspired", "FCFS", "Round Robin", "Min-Min"]
    run_raw_results = {algo: [] for algo in algos}

    sample_q_res = []
    sample_c_res = []
    sample_util = {}
    sample_weights = {}
    sample_probe = {}

    start_bench = time.perf_counter()
    for run_idx in range(num_runs):
        current_seed = seed + run_idx
        random.seed(current_seed)
        np.random.seed(current_seed)

        engine = QuantumCarbonAwareScheduler()
        engine.initial_weights = weights.copy()

        tasks = []
        for tid in range(task_count):
            tasks.append({
                "id": tid,
                "cpu": random.randint(1, 8),
                "memory": random.randint(2, 32),
                "sla": random.randint(20, 50)
            })

        for algo in algos:
            engine.reset_state(provider_count)
            start_run = time.perf_counter()
            if algo == "Classical": res = engine.run_classical_mo(tasks, provider_count)
            elif algo == "Quantum-Inspired": res = engine.run_quantum_inspired(tasks, provider_count)
            elif algo == "FCFS": res = engine.run_fcfs(tasks, provider_count)
            elif algo == "Round Robin": res = engine.run_round_robin(tasks, provider_count)
            elif algo == "Min-Min": res = engine.run_min_min(tasks, provider_count)
            runtime = time.perf_counter() - start_run

            metrics = compute_metrics(res, engine)
            run_raw_results[algo].append(metrics + [runtime])

            if run_idx == 0:
                if algo == "Quantum-Inspired":
                    sample_q_res = res[:10]
                    sample_util = {p: int(engine.provider_loads[p]) for p in engine.active_providers}
                    sample_weights = {k: round(v, 4) for k, v in engine.weights.items()}
                    if res and "error" not in res[0]:
                        node = res[0]
                        sample_probe = {
                            "id": node["task_id"], "provider": node["selected_provider"], "score": node["score"],
                            "amp": node.get("quantum_details", {}).get("amplitude", 0),
                            "raw_prob": node.get("quantum_details", {}).get("raw_probability", node["score"]),
                            "softmax_prob": node.get("quantum_details", {}).get("softmax_probability", node.get("quantum_details", {}).get("probability", 0))
                        }
                elif algo == "Classical":
                    sample_c_res = res[:10]

    bench_runtime = (time.perf_counter() - start_bench) / num_runs

    summary_stats = {}
    for algo in algos:
        data = np.array(run_raw_results[algo])
        means = np.mean(data, axis=0)
        stds = np.std(data, axis=0)
        summary_stats[algo] = {
            "cost": f"{means[0]:.2f} ± {stds[0]:.2f}",
            "carbon": f"{means[1]:.2f} ± {stds[1]:.2f}",
            "sla": f"{means[2]*100:.1f}% ± {stds[2]*100:.1f}%",
            "cv": f"{means[3]:.2f} ± {stds[3]:.2f}",
            "runtime": f"{means[4]:.4f} ± {stds[4]:.4f}",
            "raw_means": means,
            "raw_stds": stds
        }

    return {
        "summary": summary_stats,
        "raw_results": run_raw_results,
        "sample_q_res": sample_q_res,
        "sample_c_res": sample_c_res,
        "sample_util": sample_util,
        "sample_weights": sample_weights,
        "sample_probe": sample_probe,
        "avg_runtime": round(bench_runtime, 4)
    }
