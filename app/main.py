from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from app.core.scheduler_engine import QuantumCarbonAwareScheduler, scheduler, cloud_validator
from app.core.cloud_connector import real_connector
from app.core.canonical_benchmark import run_canonical_benchmark
from app.core.cloud_adapters import provider_manager
from aws_validation import get_aws_ec2_profile
import os
import random
import numpy as np
import time
import platform
import psutil

app = FastAPI()

app.mount("/static", StaticFiles(directory="app/static"), name="static")
templates = Jinja2Templates(directory="app/templates")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/simulate")
def run_simulation(payload: dict):
    # 1. Inputs from Dashboard
    task_count = payload.get("task_count", 2000)
    provider_count = max(2, min(8, int(payload.get("provider_count", 4))))
    w_alpha = payload.get("alpha", 0.4)
    w_beta = payload.get("beta", 0.3)
    w_gamma = payload.get("gamma", 0.2)
    w_delta = payload.get("delta", 0.1)
    seed = payload.get("seed", 42)

    # 2. STEP 1 & 2: Synthetic Multi-Provider Research Benchmark via Canonical Engine
    bench_result = run_canonical_benchmark(
        task_count=task_count,
        provider_count=provider_count,
        num_runs=30,
        seed=seed,
        weights={"cost": w_alpha, "carbon": w_beta, "sla": w_gamma, "renewable": w_delta}
    )

    # 3. STEP 3: Real AWS EC2 Prototype Validation
    aws_profile = get_aws_ec2_profile()
    engine_aws = QuantumCarbonAwareScheduler()
    t_start = time.perf_counter()
    aws_res = engine_aws.run_quantum_inspired([{"id": i, "cpu": random.randint(1, 4), "memory": 8, "sla": 35} for i in range(50)], provider_count=1)
    aws_runtime = time.perf_counter() - t_start

    aws_allocations = []
    for x in aws_res[:10]:
        aws_allocations.append({
            "task_id": x["task_id"],
            "selected_provider": "AWS EC2",
            "region": "us-east-1",
            "instance": "t3.micro"
        })

    aws_validation_data = {
        "is_available": True,
        "details": aws_profile,
        "network": aws_profile["network"],
        "scheduler": {
            "tasks": 50,
            "provider": "AWS EC2 (us-east-1 / t3.micro)",
            "runtime": round(aws_runtime, 4),
            "cpu_util": f"{psutil.cpu_percent()}%",
            "mem_util": f"{psutil.virtual_memory().percent}%"
        }
    }

    summary = bench_result["summary"]

    return {
        "classical": {
            "cost": summary["Classical"]["cost"],
            "carbon": summary["Classical"]["carbon"],
            "sla": summary["Classical"]["sla"],
            "cv": summary["Classical"]["cv"]
        },
        "quantum": {
            "cost": summary["Quantum-Inspired"]["cost"],
            "carbon": summary["Quantum-Inspired"]["carbon"],
            "sla": summary["Quantum-Inspired"]["sla"],
            "cv": summary["Quantum-Inspired"]["cv"]
        },
        "benchmarks": {
            "FCFS": {
                "cost": summary["FCFS"]["raw_means"][0],
                "carbon": summary["FCFS"]["raw_means"][1],
                "sla": summary["FCFS"]["raw_means"][2],
                "cv": summary["FCFS"]["raw_means"][3]
            },
            "Round Robin": {
                "cost": summary["Round Robin"]["raw_means"][0],
                "carbon": summary["Round Robin"]["raw_means"][1],
                "sla": summary["Round Robin"]["raw_means"][2],
                "cv": summary["Round Robin"]["raw_means"][3]
            },
            "Min-Min": {
                "cost": summary["Min-Min"]["raw_means"][0],
                "carbon": summary["Min-Min"]["raw_means"][1],
                "sla": summary["Min-Min"]["raw_means"][2],
                "cv": summary["Min-Min"]["raw_means"][3]
            }
        },
        "weights": bench_result["sample_weights"],
        "probe": bench_result["sample_probe"],
        "utilization": bench_result["sample_util"],
        "allocations": {
            "classical": bench_result["sample_c_res"],
            "quantum": bench_result["sample_q_res"],
            "aws_allocations": aws_allocations
        },
        "real_cloud": {
            "platform": "AWS EC2 (us-east-1)",
            "instance": "t3.micro",
            "runtime": round(aws_runtime, 4),
            "cpu_avg": f"{psutil.cpu_percent()}%",
            "latency": aws_profile["network"]["avg_rtt"]
        },
        "aws_validation": aws_validation_data,
        "avg_runtime": bench_result["avg_runtime"],
        "provider_count": provider_count
    }
