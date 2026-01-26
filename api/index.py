from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List 
import pandas as pd

app =FastAPI()

app.add_middleware(CORSMiddleware,allow_origina=['*'],allow_credientials =True,allow_methods=["POST"],allow_headers=["*"])
class LatencyRequest(BaseModel):
    regions:List[str]
    threshold_ms :int
data='q-vercel-latency.json'

@app.post('/api/latency')
async def get_latency_metrics(req:LatencyRequest):
    try:
        df =pd.read_csv(data)
    except FileNotFoundError:
        return {"error":f"file{data} not found."}
    results = {} 
    for region in req.regions:
        region_df = df[df['region']==region]
        if region_df.empty:
            continue
        avg_latency = region_df['latency_ms'].mean()
        p95_latency = region_df['latency_ms'].quantile(0.95)
        avg_uptime = region_df['uptime_pct'].mean()

        breaches = (region_df['latency_ms']>req.threshold_ms).sum()

        results[region]={
            "avg_latency":float(avg_latency),
            "p95_latecy":float(p95_latency),
            "avg_uptime":float(avg_uptime),
            "breaches":int(breaches)}
    return results






        
