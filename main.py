from fastapi import FastAPI, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from datetime import datetime
import json

from database import get_conn, init_db
from scraper import scrape_all
from verdict import run_verdicts

app = FastAPI(title="Promise Tracker API")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

@app.on_event("startup")
def startup():
    init_db()

@app.get("/promises")
def get_promises(politician: str = None, category: str = None):
    conn = get_conn()
    query = "SELECT * FROM promises WHERE 1=1"
    params = []
    if politician:
        query += " AND politician=?"; params.append(politician)
    if category:
        query += " AND category=?"; params.append(category)
    query += " ORDER BY id"
    rows = conn.execute(query, params).fetchall()
    conn.close()
    return [dict(r) for r in rows]

@app.get("/promises/{promise_id}")
def get_promise(promise_id: int):
    conn = get_conn()
    promise = conn.execute("SELECT * FROM promises WHERE id=?", (promise_id,)).fetchone()
    articles = conn.execute(
        "SELECT * FROM news_articles WHERE promise_id=? ORDER BY id DESC LIMIT 6", (promise_id,)
    ).fetchall()
    conn.close()
    if not promise: return {"error": "Not found"}
    return {**dict(promise), "articles": [dict(a) for a in articles]}

@app.get("/stats")
def get_stats(politician: str = None):
    conn = get_conn()
    query = "SELECT status, COUNT(*) as count FROM promises"
    params = []
    if politician:
        query += " WHERE politician=?"; params.append(politician)
    query += " GROUP BY status"
    rows = conn.execute(query, params).fetchall()
    conn.close()
    return {r["status"]: r["count"] for r in rows}

@app.get("/politicians")
def get_politicians():
    return [
        {"id": "trump",     "name": "Donald Trump",  "role": "US President",          "flag": "🇺🇸"},
        {"id": "wes_moore", "name": "Wes Moore",      "role": "Governor of Maryland",  "flag": "🦅"},
        {"id": "modi",      "name": "Narendra Modi",  "role": "Prime Minister of India","flag": "🇮🇳"},
    ]

class SubscribeRequest(BaseModel):
    email: str
    topics: list[str]

@app.post("/subscribe")
def subscribe(req: SubscribeRequest):
    conn = get_conn()
    try:
        conn.execute(
            "INSERT OR REPLACE INTO subscribers (email, topics, created) VALUES (?,?,?)",
            (req.email, json.dumps(req.topics), datetime.now().isoformat())
        )
        conn.commit(); conn.close()
        return {"success": True}
    except Exception as e:
        return {"success": False, "error": str(e)}

@app.post("/refresh")
def refresh(background_tasks: BackgroundTasks):
    def run():
        scrape_all()
        run_verdicts()
    background_tasks.add_task(run)
    return {"message": "Refresh started"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)