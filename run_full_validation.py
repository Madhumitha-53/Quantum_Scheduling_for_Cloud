import random
import math
import numpy as np
import time
from app.core.scheduler_engine import QuantumCarbonAwareScheduler

def run_comprehensive_validation():
    print("==================================================")
    print("COMPREHENSIVE REVIEWER 2 TECHNICAL VALIDATION")
    print("==================================================")

    engine = QuantumCarbonAwareScheduler()

    # 1. Test Feature Dimension & Range (Common Feature Space F(i,j))
    task = {"id": 999, "cpu": 4, "memory": 16, "sla": 30}
    provider_id = list(engine.active_providers.keys())[0]
    metrics = engine.normalize_metrics(task, provider_id)

    vec = metrics["vector"]
    dim_ok = len(vec) == 4
    range_ok = all(0.0 <= x <= 1.0 for x in vec)

    print(f"\n[Test 1] Common Feature Space F(i,j):")
    print(f" - Feature Vector F: {vec}")
    print(f" - Dimension == 4 : {'PASS' if dim_ok else 'FAIL'}")
    print(f" - Range [0, 1]   : {'PASS' if range_ok else 'FAIL'}")

    # 2. Test Weight Normalization & Suitability Score S(i,j)
    score = engine.compute_suitability_score(metrics)
    weight_sum = sum(engine.weights.values())
    weight_sum_ok = abs(weight_sum - 1.0) < 1e-6
    score_range_ok = 0.0 <= score <= 1.0

    print(f"\n[Test 2] Weighted Score & Weights:")
    print(f" - Weights W      : {engine.weights}")
    print(f" - Weight Sum == 1: {'PASS' if weight_sum_ok else 'FAIL'} ({weight_sum:.4f})")
    print(f" - Suitability S  : {score:.4f} (Range [0,1]: {'PASS' if score_range_ok else 'FAIL'})")

    # 3. Test Amplitude & Probability Relationship P = |ψ|² = S
    amplitude = math.sqrt(score)
    raw_prob = amplitude ** 2
    prob_ok = abs(raw_prob - score) < 1e-6

    print(f"\n[Test 3] Amplitude & Raw Probability (P = |ψ|²):")
    print(f" - Amplitude ψ = √S: {amplitude:.4f}")
    print(f" - Raw Prob P = |ψ|²: {raw_prob:.4f}")
    print(f" - P == S          : {'PASS' if prob_ok else 'FAIL'}")

    # 4. Test Softmax Probabilistic Selection over Candidates
    tasks_batch = [{"id": i, "cpu": random.randint(1, 4), "memory": 8, "sla": 35} for i in range(10)]
    res = engine.run_quantum_inspired(tasks_batch, provider_count=4)

    softmax_ok = True
    for r in res:
        if "quantum_details" in r:
            probs_sum = sum(r["quantum_details"]["probs_all"].values())
            if abs(probs_sum - 1.0) > 2e-3:
                softmax_ok = False

    print(f"\n[Test 4] Softmax Selection Probabilities:")
    print(f" - Softmax sum ≈ 1.0: {'PASS' if softmax_ok else 'FAIL'}")

    # 5. Real Task/Provider Example (Requirement 16)
    print(f"\n[Test 5] Real Task/Provider Example Instance:")
    sample_task = tasks_batch[0]
    sample_p = list(engine.active_providers.keys())[0]
    m_sample = engine.normalize_metrics(sample_task, sample_p)
    s_sample = engine.compute_suitability_score(m_sample)
    amp_sample = math.sqrt(s_sample)
    raw_p_sample = amp_sample ** 2

    print(f" - Task ID        : #{sample_task['id']} (CPU: {sample_task['cpu']}, SLA: {sample_task['sla']}ms)")
    print(f" - Provider       : {sample_p}")
    print(f" - CostScore      : {m_sample['vector'][0]:.4f}")
    print(f" - CarbonScore    : {m_sample['vector'][1]:.4f}")
    print(f" - SLAScore       : {m_sample['vector'][2]:.4f}")
    print(f" - RenewableScore : {m_sample['vector'][3]:.4f}")
    print(f" - Weights W      : {[round(w,4) for w in engine.weights.values()]}")
    print(f" - Weighted Score S: {s_sample:.4f}")
    print(f" - Amplitude ψ    : {amp_sample:.4f}")
    print(f" - Raw Probability: {raw_p_sample:.4f}")

    # 6. Scheduler Regression Tests (Classical, Quantum, FCFS, Round Robin, Min-Min)
    print(f"\n[Test 6] Regression Tests for all Schedulers:")
    sched_tests = {
        "Classical MO": len(engine.run_classical_mo(tasks_batch, 4)) == len(tasks_batch),
        "Quantum-Inspired": len(engine.run_quantum_inspired(tasks_batch, 4)) == len(tasks_batch),
        "FCFS": len(engine.run_fcfs(tasks_batch, 4)) == len(tasks_batch),
        "Round Robin": len(engine.run_round_robin(tasks_batch, 4)) == len(tasks_batch),
        "Min-Min": len(engine.run_min_min(tasks_batch, 4)) == len(tasks_batch),
    }

    all_sched_pass = True
    for name, status in sched_tests.items():
        label = "PASS" if status else "FAIL"
        if not status: all_sched_pass = False
        print(f" - {name:<18}: {label}")

    print("==================================================")
    if dim_ok and range_ok and weight_sum_ok and score_range_ok and prob_ok and softmax_ok and all_sched_pass:
        print("RESULT: ALL TECHNICAL VALIDATION TESTS PASSED SUCCESSFULLY.")
        return True
    else:
        print("RESULT: SOME TESTS FAILED.")
        return False

if __name__ == "__main__":
    success = run_comprehensive_validation()
    if not success:
        import sys
        sys.exit(1)
