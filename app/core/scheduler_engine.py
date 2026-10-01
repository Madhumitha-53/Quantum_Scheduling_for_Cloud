import random
import math
import uuid
import numpy as np
import time

class QuantumCarbonAwareScheduler:
    """
    Quantum-Inspired Multi-Objective Carbon-Aware Scheduler for Multi-Cloud Environments.

    IMPLEMENTATION AUDIT & TERMINOLOGY CLARIFICATION:
    - Weighted Multi-Objective Scoring: ACTUALLY IMPLEMENTED (Cost, Carbon, SLA, Renewable).
    - Amplitude-Like Representation: ACTUALLY IMPLEMENTED (A = sqrt(S)).
    - Probability P = |A|²: ACTUALLY IMPLEMENTED (Quantum-inspired probability mapping).
    - Softmax Selection: ACTUALLY IMPLEMENTED (Probabilistic selection over candidate scores).
    - Adaptive Weights: ACTUALLY IMPLEMENTED (Dynamic weight update mechanism).
    - QAOA / VQE / Grover / Quantum Annealing: NOT IMPLEMENTED in code (referenced strictly as conceptual inspiration from quantum mechanics principles).

    COMMON 4-DIMENSIONAL FEATURE SPACE (Resolving Dimension Mismatch):
    Task resource requirements (CPU, memory) and provider characteristics (cost, carbon, latency, renewable)
    are mapped into a normalized 4-dimensional common feature space F(i,j) = [CostScore, CarbonScore, SLAScore, RenewableScore]
    where each feature is in [0, 1] (cost and carbon are converted to benefit-style normalized scores: 1 - normalized_cost, etc.).
    Weight vector W = [alpha, beta, gamma, delta] (summing to 1.0) is dotted with F(i,j) to compute suitability S(i,j).

    COMPLEXITY ANALYSIS:
    N = Number of tasks, M = Number of providers, D = Multi-objective dimensions (D=4)
    1. Task-Provider Normalization: O(M * D) per task -> O(N * M * D) total.
    2. Multi-Objective Score: O(D) per candidate -> O(N * M * D) total.
    3. Quantum Probability Selection: O(M) per task -> O(N * M) total.
    4. Adaptive Weight Update: O(D) per task -> O(N * D) total.
    Overall Algorithmic Complexity: O(N * M * D) - Linear with respect to task count.
    """
    def __init__(self):
        # 1. ORIGINAL MULTI-OBJECTIVE WEIGHTS (α=0.4, β=0.3, γ=0.2, δ=0.1)
        self.weights = {
            "cost": 0.4,
            "carbon": 0.3,
            "sla": 0.2,
            "renewable": 0.1
        }
        self.w_floor = 0.05
        self.learning_rate = 0.02
        self.initial_weights = self.weights.copy()

        # Base Provider Definitions (Synthetic Benchmark Profiles)
        self.base_providers = [
            {"name": "Provider 1", "cost": 0.05, "carbon": 0.45, "renewable": 0.40, "latency": 15, "capacity": 2000, "region": "Zone-A"},
            {"name": "Provider 2", "cost": 0.045, "carbon": 0.35, "renewable": 0.55, "latency": 25, "capacity": 2500, "region": "Zone-B"},
            {"name": "Provider 3", "cost": 0.04, "carbon": 0.55, "renewable": 0.70, "latency": 35, "capacity": 1800, "region": "Zone-C"},
            {"name": "Provider 4", "cost": 0.06, "carbon": 0.15, "renewable": 0.85, "latency": 10, "capacity": 1200, "region": "Zone-D"},
            {"name": "Provider 5", "cost": 0.055, "carbon": 0.25, "renewable": 0.60, "latency": 20, "capacity": 2200, "region": "Zone-E"},
            {"name": "Provider 6", "cost": 0.048, "carbon": 0.40, "renewable": 0.50, "latency": 30, "capacity": 2000, "region": "Zone-F"},
            {"name": "Provider 7", "cost": 0.052, "carbon": 0.30, "renewable": 0.65, "latency": 18, "capacity": 2400, "region": "Zone-G"},
            {"name": "Provider 8", "cost": 0.042, "carbon": 0.50, "renewable": 0.75, "latency": 28, "capacity": 1900, "region": "Zone-H"}
        ]

        self.active_providers = {}
        self.reset_state(provider_count=4)

    def reset_state(self, provider_count=4):
        """Resets the scheduler state for a fresh algorithmic run with dynamic provider count."""
        # Restore and Normalize Weights
        self.weights = self.initial_weights.copy()
        total_w = sum(self.weights.values())
        if total_w > 0:
            for k in self.weights:
                self.weights[k] /= total_w

        # Configure Active Providers based on requested count
        self.active_providers = {}
        for i in range(provider_count):
            if i < len(self.base_providers):
                p = self.base_providers[i]
                self.active_providers[p["name"]] = p
            else:
                # Generate additional synthetic providers if count > 8
                name = f"Provider {i+1}"
                self.active_providers[name] = {
                    "name": name,
                    "cost": round(random.uniform(0.04, 0.07), 3),
                    "carbon": round(random.uniform(0.1, 0.6), 2),
                    "renewable": round(random.uniform(0.3, 0.9), 2),
                    "latency": random.randint(10, 50),
                    "capacity": random.randint(1000, 3000),
                    "region": f"Zone-{chr(65 + (i % 8))}"
                }

        self.task_queue = []
        self.task_counter = 0
        self.provider_loads = {p: 0.0 for p in self.active_providers}
        self.weight_history = []

    def add_task(self, task):
        task["id"] = self.task_counter
        self.task_counter += 1
        if "cpu" not in task: task["cpu"] = random.randint(1, 8)
        if "memory" not in task: task["memory"] = random.randint(2, 32)
        if "sla" not in task: task["sla"] = random.randint(20, 50)
        self.task_queue.append(task)
        return {"message": "Task added", "task": task}

    def get_stack(self):
        return self.task_queue

    # ---------------------------------------------------------
    # 3. MATHEMATICAL CORRECTION: Suitability Mapping (F_ij)
    # ---------------------------------------------------------
    def normalize_metrics(self, task, p_id):
        p_cfg = self.active_providers[p_id]
        cpu = task["cpu"]

        # Cost Suitability (Minimize Cost -> High Score)
        all_costs = [self.active_providers[p]["cost"] * cpu for p in self.active_providers]
        cost_score = min(all_costs) / max(1e-6, p_cfg["cost"] * cpu)

        # Carbon Suitability (Minimize Carbon -> High Score)
        all_carbons = [self.active_providers[p]["carbon"] * cpu for p in self.active_providers]
        carbon_score = min(all_carbons) / max(1e-6, p_cfg["carbon"] * cpu)

        # SLA Suitability (Meet Latency Requirement)
        actual_lat = p_cfg["latency"]
        if actual_lat <= task["sla"]:
            sla_score = 1.0
        else:
            sla_score = max(0.0, 1.0 - (actual_lat - task["sla"]) / task["sla"])

        # Renewable Suitability (Maximize Utilization)
        renewable_score = p_cfg["renewable"]

        return {
            "vector": [cost_score, carbon_score, sla_score, renewable_score],
            "raw": {
                "cost": p_cfg["cost"] * cpu,
                "carbon": p_cfg["carbon"] * cpu,
                "lat": actual_lat,
                "renew": p_cfg["renewable"]
            }
        }

    def compute_suitability_score(self, metrics):
        v = metrics["vector"]
        return (
            self.weights["cost"] * v[0] +
            self.weights["carbon"] * v[1] +
            self.weights["sla"] * v[2] +
            self.weights["renewable"] * v[3]
        )

    # ---------------------------------------------------------
    # 4. QUANTUM-INSPIRED PROBABILISTIC MODULE
    # ---------------------------------------------------------
    def run_quantum_inspired(self, tasks, provider_count=4, temperature=0.15):
        self.reset_state(provider_count)
        results = []
        for task in tasks:
            candidates = []
            for p_id in self.active_providers:
                if self.provider_loads[p_id] + task["cpu"] > self.active_providers[p_id]["capacity"]:
                    continue
                m = self.normalize_metrics(task, p_id)
                score = self.compute_suitability_score(m)
                candidates.append({"id": p_id, "metrics": m, "score": score})

            if not candidates:
                results.append({"task_id": task["id"], "error": "Infeasible"})
                continue

            # SoftMax probability calculation
            exp_scores = [math.exp(c["score"] / temperature) for c in candidates]
            total_exp = sum(exp_scores)
            probs = [e / total_exp for e in exp_scores]

            selected_idx = random.choices(range(len(candidates)), weights=probs, k=1)[0]
            selected = candidates[selected_idx]

            self.provider_loads[selected["id"]] += task["cpu"]
            self.update_adaptive_weights(selected["metrics"]["vector"])

            entry = self._build_result(task, selected["id"], selected["metrics"], selected["score"])
            entry["quantum_details"] = {
                "score": round(selected["score"], 4),
                "amplitude": round(math.sqrt(selected["score"]), 4),
                "raw_probability": round(selected["score"], 4),
                "softmax_probability": round(probs[selected_idx], 4),
                "probability": round(probs[selected_idx], 4),
                "probs_all": {candidates[i]["id"]: round(probs[i], 4) for i in range(len(probs))}
            }
            results.append(entry)
        return results

    # ---------------------------------------------------------
    # 5. CLASSICAL DETERMINISTIC SCHEDULER
    # ---------------------------------------------------------
    def run_classical_mo(self, tasks, provider_count=4):
        self.reset_state(provider_count)
        results = []
        for task in tasks:
            best_p, best_score, best_metrics = None, -1.0, None
            for p_id in self.active_providers:
                if self.provider_loads[p_id] + task["cpu"] > self.active_providers[p_id]["capacity"]:
                    continue
                m = self.normalize_metrics(task, p_id)
                score = self.compute_suitability_score(m)
                if score > best_score:
                    best_score, best_p, best_metrics = score, p_id, m

            if not best_p:
                best_p = random.choice(list(self.active_providers.keys()))
                best_metrics = self.normalize_metrics(task, best_p)
                best_score = self.compute_suitability_score(best_metrics)

            self.provider_loads[best_p] += task["cpu"]
            self.update_adaptive_weights(best_metrics["vector"])
            results.append(self._build_result(task, best_p, best_metrics, best_score))
        return results

    # ---------------------------------------------------------
    # 6. ADAPTIVE LEARNING / WEIGHT UPDATE
    # ---------------------------------------------------------
    def update_adaptive_weights(self, metrics_vec):
        for idx, key in enumerate(["cost", "carbon", "sla", "renewable"]):
            reward = metrics_vec[idx]
            self.weights[key] += self.learning_rate * (1.0 - reward)
            self.weights[key] = max(self.w_floor, self.weights[key])

        total = sum(self.weights.values())
        if total > 0:
            for k in self.weights:
                self.weights[k] /= total
        self.weight_history.append(self.weights.copy())

    # ---------------------------------------------------------
    # 7. STANDARD BASELINES
    # ---------------------------------------------------------
    def run_fcfs(self, tasks, provider_count=4):
        self.reset_state(provider_count)
        res = []
        p_ids = list(self.active_providers.keys())
        for idx, t in enumerate(tasks):
            p = p_ids[idx % len(p_ids)]
            m = self.normalize_metrics(t, p)
            self.provider_loads[p] += t["cpu"]
            res.append(self._build_result(t, p, m, self.compute_suitability_score(m)))
        return res

    def run_round_robin(self, tasks, provider_count=4):
        self.reset_state(provider_count)
        res = []
        p_ids = list(self.active_providers.keys())
        for idx, t in enumerate(tasks):
            p = p_ids[idx % len(p_ids)]
            original_p = p
            attempts = 0
            curr_idx = idx
            while self.provider_loads[p] + t["cpu"] > self.active_providers[p]["capacity"] and attempts < len(p_ids):
                curr_idx += 1
                p = p_ids[curr_idx % len(p_ids)]
                attempts += 1
            if self.provider_loads[p] + t["cpu"] > self.active_providers[p]["capacity"]:
                p = original_p
            m = self.normalize_metrics(t, p)
            self.provider_loads[p] += t["cpu"]
            res.append(self._build_result(t, p, m, self.compute_suitability_score(m)))
        return res

    def run_min_min(self, tasks, provider_count=4):
        self.reset_state(provider_count)
        sorted_tasks = sorted(tasks, key=lambda x: x["cpu"])
        res = []
        for t in sorted_tasks:
            best_p = min(self.active_providers.keys(), key=lambda p: self.active_providers[p]["cost"])
            m = self.normalize_metrics(t, best_p)
            self.provider_loads[best_p] += t["cpu"]
            res.append(self._build_result(t, best_p, m, self.compute_suitability_score(m)))
        return sorted(res, key=lambda x: x["task_id"])

    def _build_result(self, task, p_id, metrics, score):
        raw = metrics["raw"]
        return {
            "task_id": task["id"],
            "selected_provider": p_id,
            "region": self.active_providers[p_id]["region"],
            "cost": round(raw["cost"], 2),
            "carbon": round(raw["carbon"], 2),
            "latency": raw["lat"],
            "renewable": round(raw["renew"], 2),
            "sla_satisfied": raw["lat"] <= task["sla"],
            "score": round(score, 4)
        }

from app.core.cloud_connector import real_connector

class RealCloudValidator:
    def run_validation(self):
        aws_data = real_connector.get_aws_metrics()
        if aws_data: return aws_data
        return real_connector.get_private_cloud_metrics()

scheduler = QuantumCarbonAwareScheduler()
cloud_validator = RealCloudValidator()
