import json
import os
import sys

# Vercel handler setup FIRST
def handler(request):
    # Handle CORS preflight
    if request['method'] == 'OPTIONS':
        return {
            'statusCode': 200,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'POST, OPTIONS',
                'Access-Control-Allow-Headers': 'Content-Type',
            },
            'body': ''
        }
    
    # Parse POST body
    body = json.loads(request['body'])
    regions = body['regions']
    threshold_ms = body['threshold_ms']
    
    # Load telemetry (download q-vercel-latency.json to project root)
    telemetry_path = os.path.join(os.path.dirname(__file__), '..', 'q-vercel-latency.json')
    with open(telemetry_path) as f:
        telemetry = json.load(f)
    
    results = {}
    for region in regions:
        region_data = [r for r in telemetry if r.get('region') == region]
        if not region_data:
            results[region] = {'error': 'No data'}
            continue
        
        latencies = [r['latency_ms'] for r in region_data]
        uptimes = [r['uptime'] for r in region_data]
        
        # Sort for p95 (95th percentile)
        latencies_sorted = sorted(latencies)
        p95_index = int(0.95 * len(latencies_sorted))
        p95_latency = latencies_sorted[p95_index]
        
        results[region] = {
            'avg_latency': round(sum(latencies)/len(latencies), 2),
            'p95_latency': round(p95_latency, 2),
            'avg_uptime': round(sum(uptimes)/len(uptimes), 4),
            'breaches': sum(lat > threshold_ms for lat in latencies)
        }
    
    return {
        'statusCode': 200,
        'headers': {
            'Access-Control-Allow-Origin': '*',
            'Content-Type': 'application/json',
        },
        'body': json.dumps(results)
    }
