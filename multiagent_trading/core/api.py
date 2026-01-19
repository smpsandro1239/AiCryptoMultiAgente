from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import sqlite3
import json

app = FastAPI(title="MATF API")

class MemoryItem(BaseModel):
    timestamp: str
    key: str
    value: dict

@app.get("/")
def read_root():
    return {"status": "online", "framework": "MATF"}

@app.get("/memory", response_model=List[MemoryItem])
def get_memory(key: Optional[str] = None):
    conn = sqlite3.connect("memory.db")
    cursor = conn.cursor()
    if key:
        cursor.execute("SELECT timestamp, key, value FROM memory WHERE key = ?", (key,))
    else:
        cursor.execute("SELECT timestamp, key, value FROM memory")

    rows = cursor.fetchall()
    conn.close()

    return [
        {"timestamp": r[0], "key": r[1], "value": json.loads(r[2])}
        for r in rows
    ]

@app.post("/trade/manual")
def manual_trade(symbol: str, side: str, amount: float):
    # Placeholder para execução manual via API
    return {"message": f"Ordem manual de {side} para {symbol} recebida.", "amount": amount}
