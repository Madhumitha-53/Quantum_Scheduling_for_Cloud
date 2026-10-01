# Quantum-Inspired Multi-Objective Carbon-Aware Scheduling for Multi-Cloud

A Python-based multi-cloud scheduling prototype that considers **cost, carbon emission, SLA satisfaction, and renewable-energy preference** when assigning workloads across cloud providers.

The project compares a **quantum-inspired probabilistic scheduler** with a classical multi-objective scheduler and standard scheduling algorithms including **FCFS, Round Robin, and Min-Min**.

## Overview

The framework combines:

* Multi-objective weighted scoring
* Amplitude-like representation
* Probability-based provider selection
* Softmax probability distribution
* Adaptive weight updating
* Quantum algorithm validation using QAOA, VQE, Grover Search, and Quantum Annealing

The evaluation uses **2,000 tasks and 4 cloud providers** with initial objective weights:

```text
α = 0.4
β = 0.3
γ = 0.2
δ = 0.1
```

## Methodology

```text
Task Input
    ↓
Multi-Objective Scoring
    ↓
┌──────────────────────────────┐
│ Classical Scheduler          │
│ Quantum-Inspired Scheduler   │
└──────────────────────────────┘
    ↓
Provider Selection
    ↓
Adaptive Weight Updating
    ↓
Performance Evaluation
```

The suitability score is calculated as:

```text
Sij = αCij + βEij + γSLAij + δRij
```

The quantum-inspired scheduler uses an amplitude-like representation:

```text
ψij = √Sij
Pij = |ψij|²
```

A softmax-based probability distribution is then used for provider selection.

## Scheduling Methods

**Quantum-Inspired Scheduler**

* Weighted multi-objective scoring
* Amplitude-like representation
* Probabilistic provider selection
* Adaptive objective weights

**Comparison Methods**

* Classical Multi-Objective Scheduler
* First-Come-First-Serve (FCFS)
* Round Robin (RR)
* Min-Min

## Quantum Validation

The project includes validation components for:

* QAOA
* VQE
* Grover Search
* Quantum Annealing

These components are used to evaluate quantum and quantum-inspired optimization formulations.

## Results

For the benchmark reported in the research work:

| Metric            |  Quantum-Inspired |          Classical |
| ----------------- | ----------------: | -----------------: |
| Cost              |     356.50 ± 0.09 |      430.75 ± 5.34 |
| Carbon Emission   | 2945.00 ± 0.00 kg | 3512.00 ± 44.46 kg |
| SLA Satisfaction  |       83.5 ± 0.8% |        84.8 ± 0.7% |
| Load Stability CV |       0.25 ± 0.00 |                  — |

The benchmark reported approximately **17.2% lower cost** and **16.2% lower carbon emission** for the quantum-inspired approach, with slightly lower SLA satisfaction than the classical scheduler.

## AWS Validation

The prototype was also validated on an **AWS EC2 t3.micro** instance:

```text
Tasks        : 50
Execution    : 0.000593 s
Packet Loss  : 0.0%
```

## Technologies

* Python
* FastAPI
* NumPy
* Pandas
* Matplotlib
* Qiskit / quantum-computing libraries
* AWS EC2
* HTML, CSS, JavaScript

## Repository

The repository contains the scheduling application, validation modules, experimental results, statistical analysis, scalability experiments, and performance plots.

> **Note:** This is a research prototype. Reported results are based on the specified experimental configuration and may vary with workload and execution environment.
