from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
import uvicorn
import database
import context_engine
import orchestrator
import generate_data

app = FastAPI(title="Agentic Inbound Voice Agent Backend", version="1.0.0")

# Enable CORS for frontend development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # In development, allow all origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class CallStartRequest(BaseModel):
    borrower_id: str

class CallInteractRequest(BaseModel):
    borrower_id: str
    text: str

class CallResetRequest(BaseModel):
    borrower_id: str

@app.get("/api/borrowers")
def get_borrowers():
    try:
        return database.get_all_borrowers()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/borrowers/{borrower_id}/context")
def get_borrower_context(borrower_id: str):
    try:
        ctx = context_engine.get_unified_borrower_context(borrower_id)
        if not ctx:
            raise HTTPException(status_code=404, detail="Borrower not found")
        return ctx
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/call/start")
def start_call(req: CallStartRequest):
    try:
        session = orchestrator.get_session(req.borrower_id)
        # Returns the initial agent greeting turn
        return {
            "session_transcript": session["turns"],
            "context": context_engine.get_unified_borrower_context(req.borrower_id),
            "response_text": session["turns"][0]["text"]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/call/interact")
def interact_call(req: CallInteractRequest):
    try:
        result = orchestrator.interact_call(req.borrower_id, req.text)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/call/reset")
def reset_call(req: CallResetRequest):
    try:
        orchestrator.reset_session(req.borrower_id)
        return {"status": "Success", "message": "Call session cleared."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/workflow/logs")
def get_workflow_logs():
    try:
        return database.get_workflow_logs()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/analytics")
def get_analytics():
    try:
        conn = database.get_connection()
        
        # Summary counts
        total_borrowers = conn.execute("SELECT COUNT(*) FROM borrowers").fetchone()[0]
        delinquent_count = conn.execute("SELECT COUNT(*) FROM borrowers WHERE delinquency_status != 'Current'").fetchone()[0]
        avg_risk = conn.execute("SELECT AVG(risk_score) FROM borrowers").fetchone()[0] or 0
        total_collected = conn.execute("SELECT SUM(amount) FROM payment_history WHERE status = 'Success'").fetchone()[0] or 0
        
        # Tickets status
        open_tickets = conn.execute("SELECT COUNT(*) FROM tickets WHERE status = 'Open'").fetchone()[0]
        resolved_tickets = conn.execute("SELECT COUNT(*) FROM tickets WHERE status = 'Resolved'").fetchone()[0]
        
        # Delinquency breakdown
        del_breakdown = {}
        rows = conn.execute("SELECT delinquency_status, COUNT(*) FROM borrowers GROUP BY delinquency_status").fetchall()
        for r in rows:
            del_breakdown[r[0]] = r[1]
            
        conn.close()
        
        return {
            "total_borrowers": total_borrowers,
            "delinquent_count": delinquent_count,
            "average_risk_score": round(avg_risk, 1),
            "total_payments_collected": round(total_collected, 2),
            "tickets": {
                "open": open_tickets,
                "resolved": resolved_tickets
            },
            "delinquency_breakdown": del_breakdown
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/reset-db")
def reset_database():
    try:
        # Re-run seeder
        generate_data.generate_dataset()
        # Reset any cached call sessions
        orchestrator.ACTIVE_SESSIONS.clear()
        return {"status": "Success", "message": "Database and sessions reset successfully."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
