import os
import json
import numpy as np
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict

app = FastAPI()

# Enable CORS for POST from any origin
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["POST"],
    allow_headers=["*"],
)

class RequestBody(BaseModel):
    regions: List[str]
    threshold_ms: int

@app.post("/")
async def analyze_latency(body: RequestBody):
    # Load the sample telemetry data (download q-vercel-latency.json and place in api/ folder)
    try:
        with open("q-vercel-latency.json", "r") as f:
            data = json.load(f)
    except FileNotFoundError:
        raise HTTPException(status_code=500, detail="Telemetry file missing")

    results = {}
    for region in body.regions:
        region_data = [r for r in data["records"] if r.get("region") == region]
        if not region_data:
            results[region] = {"error": "No data for region"}
            continue
        
        latencies = [r["latency_ms"] for r in region_data if "latency_ms" in r]
        uptimes = [r["uptime_percent"] for r in region_data if "uptime_percent" in r]
        
        results[region] = {
            "avg_latency": float(np.mean(latencies)),
            "p95_latency": float(np.percentile(latencies, 95)),
            "avg_uptime": float(np.mean(uptimes)),
            "breaches": sum(1 for lat in latencies if lat > body.threshold_ms)
        }
    
    return results
