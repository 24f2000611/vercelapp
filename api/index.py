from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
import json
import statistics
import os

app = FastAPI()

@app.options("/{full_path:path}")
async def options():
    return {"status": "ok"}
    
class RequestBody(BaseModel):
    regions: List[str]
    threshold_ms: int


CORS_HEADERS = {
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Methods": "POST, GET, OPTIONS",
    "Access-Control-Allow-Headers": "Content-Type, Authorization",
    "Access-Control-Expose-Headers": "Access-Control-Allow-Origin",
}
@app.post("/")
async def analytics_endpoint(body: RequestBody):
    telemetry_path = os.path.join(os.path.dirname(__file__), '..', 'q-vercel-latency.json')
    with open(telemetry_path, 'r') as f:
        telemetry = json.load(f)
    
    results = {}
    for region in body.regions:
        region_data = [r for r in telemetry if r.get("region") == region]
        if not region_data:
            results[region] = {"error": "No data for region"}
            continue
        
        latencies = [r["latency_ms"] for r in region_data]
        uptimes = [r["uptime"] for r in region_data]
        
        results[region] = {
            "avg_latency": round(statistics.mean(latencies), 2),
            "p95_latency": round(sorted(latencies)[int(0.95 * len(latencies))], 2),
            "avg_uptime": round(statistics.mean(uptimes), 4),
            "breaches": sum(1 for lat in latencies if lat > body.threshold_ms)
        }
    
    return results

@app.get("/")
async def root():
    return {"message": "POST analytics endpoint ready"}
