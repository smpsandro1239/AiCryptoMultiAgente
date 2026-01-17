from fastapi import FastAPI
from pydantic import BaseModel
from typing import List, Dict, Any

app = FastAPI(title="MATF API")

# Global reference to orchestrator (would be set during startup)
orchestrator = None

class SystemStatus(BaseModel):
    status: str
    agents: List[str]
    portfolio_value: float

@app.get("/status", response_model=SystemStatus)
async def get_status():
    if not orchestrator:
        return {"status": "Not Initialized", "agents": [], "portfolio_value": 0.0}

    return {
        "status": "Running",
        "agents": list(orchestrator.agents.keys()),
        "portfolio_value": orchestrator.context.portfolio.total_value
    }

@app.get("/memory")
async def get_memory(query: str = None):
    if not orchestrator:
        return []
    if query:
        return orchestrator.context.memory.query(query)
    return orchestrator.context.memory.memory

@app.post("/trade/manual")
async def manual_trade(symbol: str, side: str, amount: float):
    if not orchestrator:
        return {"error": "Orchestrator not initialized"}

    opp = {"symbol": symbol, "side": side, "optimized_size": amount, "reason": "Manual API Order"}
    await orchestrator.event_bus.publish("trade_approved", opp)
    return {"status": "Order Sent", "order": opp}
