import re

def analyze_transcript_keywords(turns):
    """
    Scans the active call turns for keywords to detect intents, reasons, and commitments.
    """
    text = " ".join([turn.get("text", "").lower() for turn in turns])
    
    analysis = {
        "claimed_bank_glitch": False,
        "claimed_salary_delay": False,
        "asked_remaining_emi": False,
        "asked_interest_paid": False,
        "asked_penalty_reason": False,
        "asked_waiver": False,
        "provided_promise_date": None,
        "wants_human_agent": False
    }
    
    # Keyword detections
    if any(k in text for k in ["bank glitch", "bank error", "technical issue", "gateway error", "server down", "sufficient balance", "enough balance", "enough funds", "had balance"]):
        analysis["claimed_bank_glitch"] = True
    if any(k in text for k in ["salary delay", "salary late", "delayed salary", "paycheck delayed", "waiting for salary"]):
        analysis["claimed_salary_delay"] = True
    if any(k in text for k in ["remaining emi", "how many emi", "how many payments left", "remaining tenure", "tenure left", "emis remaining", "emis left"]):
        analysis["asked_remaining_emi"] = True
    if "interest" in text and any(w in text for w in ["paid", "how much", "total", "amount", "portion"]):
        analysis["asked_interest_paid"] = True
    if any(w in text for w in ["why", "reason", "explain", "cause", "how come"]) and any(w in text for w in ["penalty", "charge", "late fee", "fees", "fee"]):
        analysis["asked_penalty_reason"] = True
    if any(k in text for k in ["waive", "waiver", "refund penalty", "remove charge", "cancel late fee", "forgive"]):
        analysis["asked_waiver"] = True
    if any(k in text for k in ["human", "agent", "supervisor", "representative", "manager", "transfer"]):
        analysis["wants_human_agent"] = True
        
    # Extract promise date if mentioned (e.g. next Friday, next week, Friday, etc.)
    # Simple heuristic regex for demo; Voice Agent LLM will do precise extraction, 
    # but this keyword layer helps guarantee rule-based accuracy.
    date_matches = re.findall(r"(friday|monday|tuesday|wednesday|thursday|next week|next friday|tomorrow)", text)
    if date_matches:
        analysis["provided_promise_date"] = date_matches[-1]
        
    return analysis

def diagnose_session(context: dict, current_turns: list) -> dict:
    """
    Diagnoses borrower's state, detects information gaps, and checks policy eligibility.
    """
    borrower_name = context.get("name", "Borrower")
    delinquency_status = context.get("loan", {}).get("delinquency_status", "Current")
    recent_failures = context.get("operational", {}).get("recent_payment_failures", [])
    outstanding_penalty = context.get("operational", {}).get("outstanding_penalty", 0.0)
    risk_score = context.get("loan", {}).get("risk_score", 0)
    
    # 1. Gather transcript analysis
    transcript_info = analyze_transcript_keywords(current_turns)
    
    # 2. Determine Knowns
    knowns = {
        "borrower_identified": True,
        "loan_status": delinquency_status,
        "outstanding_penalty": outstanding_penalty,
        "risk_level": "High" if risk_score > 60 else ("Medium" if risk_score > 30 else "Low"),
        "has_failed_payment": len(recent_failures) > 0
    }
    
    # Gateway confirmation of bank glitch
    actual_bank_glitch_verified = False
    glitch_timestamp = None
    glitch_reason = None
    for f in recent_failures:
        if f["failure_reason"] in ["Bank Gateway Timeout", "Network Timeout", "Bank Server Down"]:
            actual_bank_glitch_verified = True
            glitch_timestamp = f["date"]
            glitch_reason = f["failure_reason"]
            break
            
    knowns["actual_bank_glitch_verified"] = actual_bank_glitch_verified
    knowns["glitch_date"] = glitch_timestamp
    knowns["glitch_reason"] = glitch_reason
    
    if transcript_info["claimed_salary_delay"]:
        knowns["failure_reason_category"] = "Salary Delay"
    elif transcript_info["claimed_bank_glitch"]:
        knowns["failure_reason_category"] = "Bank/Gateway Glitch"
    else:
        knowns["failure_reason_category"] = "Unknown"
        
    # 3. Determine Unknowns / Gaps
    unknowns = []
    prioritized_questions = []
    
    # Check for core missing pieces
    is_delinquent = delinquency_status != "Current"
    
    if is_delinquent:
        # Gap: Why did the payment fail?
        if knowns["failure_reason_category"] == "Unknown":
            unknowns.append("Reason for payment failure/delay")
            prioritized_questions.append({
                "gap": "Reason for payment failure/delay",
                "question": "Could you please help me understand the reason why your monthly payment was not completed?"
            })
            
        # Gap: When will they pay? (Commitment / PTP)
        ptp_exists = len(context.get("memory", {}).get("promises", [])) > 0
        if not ptp_exists and not transcript_info["provided_promise_date"]:
            unknowns.append("Payment commitment date (Promise-to-Pay)")
            prioritized_questions.append({
                "gap": "Payment commitment date (Promise-to-Pay)",
                "question": f"When can we expect you to make the payment of INR {context.get('loan', {}).get('emi_amount', 0.0)} to clear the overdue status?"
            })
            
    # 4. Action Eligibility
    # Penalty waiver eligibility rules:
    # 1. Must have a late fee (outstanding_penalty > 0)
    # 2. Must be verified as technical glitch (actual_bank_glitch_verified == True)
    # 3. Account must not be super high risk (risk_score <= 80)
    is_waiver_eligible = (
        outstanding_penalty > 0 and 
        actual_bank_glitch_verified and 
        risk_score <= 80
    )
    
    # Escalation eligibility rules:
    # 1. Explicit request for human agent
    # 2. Very high risk score (> 80) with active delinquency
    # 3. Delinquency is 30+ days
    is_escalation_eligible = (
        transcript_info["wants_human_agent"] or
        (is_delinquent and risk_score > 80) or
        delinquency_status == "Delinquent (30+ days)"
    )
    
    eligibility = {
        "eligible_for_penalty_waiver": is_waiver_eligible,
        "eligible_for_instant_payment_link": is_delinquent,
        "eligible_for_human_escalation": is_escalation_eligible,
        "eligible_for_settlement": delinquency_status == "Delinquent (30+ days)" and risk_score > 50
    }
    
    return {
        "knowns": knowns,
        "gaps": unknowns,
        "prioritized_questions": prioritized_questions,
        "eligibility": eligibility,
        "keywords_extracted": transcript_info
    }
