from fastapi import FastAPI,Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List ,Dict
import pandas as pd
import statistics
import uvicorn
import os

app =FastAPI()

app.add_middleware(CORSMiddleware,allow_origina=['*'],allow_credientials =True,allow_methods=["POST"],allow_headers=["*"])
class LatencyRequest(BaseModel):
    regions:List[str]
    threshold_ms :int

@app.post('/')
async def analytics_endpoint(body:RequestBody):
    import json
    with open('q-vercel-latency.json') as f:
        telemetry= json.load(f)
    results = {} 
    for region in body.regions:
        region_data= [r for r in telemetry if r.get('region')==region]
        if not region_data:
            results[region] ={"error":"No data for region"}
            continue
        latencies= [r['latency_ms'] for r in region_data]
        uptimes = [r['uptime']for r in region_data]
        results[region] ={
        "avg_latency" : round(statistics.mean(latencies),2),
        "p95_latency" :round(statistics.quantiles(latencies,n=20)[19],2),
        "avg_uptimes: : round(statistics.mean(uptimes),4),
        "breaches":sum(1 for lat in latencies if lat>body.threshold_ms)
    return results






        
