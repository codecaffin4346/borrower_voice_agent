import database
import json
from datetime import datetime

def retrieve_borrower_memory(borrower_id: str) -> dict:
    """
    Retrieves the short-term and long-term memory logs linked to a borrower.
    """
    return database.get_memory(borrower_id)

def record_ptp_promise(borrower_id: str, date_str: str, amount: float, reason: str = "Salary delayed"):
    """
    Programmatically logs a Promise-to-Pay (PTP) commitment into the borrower's memory.
    """
    mem = database.get_memory(borrower_id)
    promises = mem.get("promises", [])
    
    # Check if this promise date is already recorded to avoid duplicates
    exists = False
    for p in promises:
        if p.get("date") == date_str and p.get("amount") == amount:
            exists = True
            break
            
    if not exists:
        new_promise = {
            "date": date_str,
            "amount": amount,
            "reason": reason,
            "status": "Pending",
            "created_at": datetime.now().strftime("%Y-%m-%d")
        }
        promises.append(new_promise)
        
    database.update_memory(
        borrower_id=borrower_id,
        promises=promises,
        preferences=mem.get("preferences", {}),
        outstanding_issues=mem.get("outstanding_issues", []),
        agent_success_paths=mem.get("agent_success_paths", []),
        last_interaction=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    )
    return promises

def update_preferences_and_paths(borrower_id: str, new_preferences: dict = None, new_success_path: str = None):
    """
    Updates communication preferences and logs successful agent resolution paths.
    """
    mem = database.get_memory(borrower_id)
    
    prefs = mem.get("preferences", {})
    if new_preferences:
        prefs.update(new_preferences)
        
    paths = mem.get("agent_success_paths", [])
    if new_success_path and new_success_path not in paths:
        paths.append(new_success_path)
        
    database.update_memory(
        borrower_id=borrower_id,
        promises=mem.get("promises", []),
        preferences=prefs,
        outstanding_issues=mem.get("outstanding_issues", []),
        agent_success_paths=paths,
        last_interaction=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    )

def finalize_call_session(borrower_id: str, turns: list, summary: str, sentiment: str, outcome: str):
    """
    Finalizes a call session:
    1. Saves the full transcript to the conversation history database.
    2. Updates borrower memories (extracting commitments, preferences, resolved issues).
    """
    conv_id = f"CONV_AUTO_{uuid_short()}"
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # Save conversation log
    database.add_conversation(
        conversation_id=conv_id,
        borrower_id=borrower_id,
        timestamp=ts,
        transcript_json=json.dumps(turns),
        summary=summary,
        sentiment=sentiment,
        outcome=outcome
    )
    
    # Extract any commitments from transcript
    # (In dynamic mode, the agent updates memory via tool calls, but we do a fallback sweep here)
    mem = database.get_memory(borrower_id)
    promises = mem.get("promises", [])
    issues = mem.get("outstanding_issues", [])
    
    # Simple rule based checks to ensure data is updated on call hang-up
    text_content = " ".join([t.get("text", "").lower() for t in turns])
    
    # If a payment link or ticket was created successfully, log success path
    if "payment link" in outcome.lower() or "sent link" in text_content:
        if "Sent Razorpay payment link to borrower" not in mem.get("agent_success_paths", []):
            mem["agent_success_paths"].append("Sent Razorpay payment link to borrower")
            
    if "waiver ticket" in outcome.lower() or "waive" in text_content:
        if "Initiated penalty waiver ticket for bank glitch" not in mem.get("agent_success_paths", []):
            mem["agent_success_paths"].append("Initiated penalty waiver ticket for bank glitch")
            
    # Remove outstanding issues if resolved
    if "resolve" in outcome.lower() or "cleared" in outcome.lower():
        issues = []
    elif "penalty" in text_content and "open" in outcome.lower():
        if "Late fee dispute unresolved" not in issues:
            issues.append("Late fee dispute unresolved")
            
    database.update_memory(
        borrower_id=borrower_id,
        promises=promises,
        preferences=mem.get("preferences", {}),
        outstanding_issues=issues,
        agent_success_paths=mem.get("agent_success_paths", []),
        last_interaction=ts
    )
    
    return conv_id

def uuid_short():
    import uuid
    return uuid.uuid4().hex[:8]
