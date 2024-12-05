from fastapi import FastAPI, Query
from typing import List

app = FastAPI()

# Mock data or logic for search results
data = ["apple", "banana", "orange", "grape", "pineapple"]

@app.get("/search")
async def search(q: str = Query(..., min_length=2, max_length=50)):
    # Filter the data for matching search results
    results = [item for item in data if q.lower() in item.lower()]
    return {"query": q, "results": results}
