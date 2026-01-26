from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List 
import pandas as pd
import os

app =FastAPI()

app.add_middleware(CORSMiddleware,allow_origina=['*'],allow_credientials =True,allow_methods=["POST"],allow_headers=["*"])
class LatencyRequest(BaseModel):
    regions:List[str]
    threshold_ms :int
data='q-vercel-latency.json'

@app.post('/api/latency')
async def get_latency_metrics(req:LatencyRequest):
    current_dir = os.path.dirname(os.path.abaspath(__file__))
    file_path = os.path.join(current_dir,"..",data)
    try:
        df =pd.read_json(file_path)
    except Exception as e:
        return {"error":f"{data}:{str(e)}"}
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






        
