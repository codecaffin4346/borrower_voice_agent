import database
from datetime import datetime
import json

def get_outstanding_fees_and_penalties(borrower, payments):
    """
    Calculates penalties based on failed/missed payments.
    Standard policy: INR 500 late charge per auto-debit / payment failure,
    plus 2% penal interest per month on the overdue amount.
    """
    delinquency = borrower.get("delinquency_status", "Current")
    if delinquency == "Current":
        return 0.0
        
    penalty = 0.0
    for p in payments:
        # Check failed payments in the last 60 days
        if p["status"] in ["Failed", "Auto-Debit Failed"]:
            penalty += 500.0 # Standard late fee bounce charge
            
    # Cap penalty at INR 2000 for safety, or return calculated
    return min(penalty, 2000.0)

def calculate_loan_breakdown(borrower, payments):
    """
    Calculates principal paid, interest paid, and outstanding principal balance 
    using the reducing balance interest formula based on actual successful payments.
    """
    loan_amount = borrower["loan_amount"]
    rate = borrower["interest_rate"]
    emi = borrower["emi_amount"]
    
    # Sort successful payments in chronological order (oldest first)
    success_payments = [p for p in payments if p["status"] == "Success"]
    success_payments.sort(key=lambda x: x["payment_date"])
    
    monthly_rate = (rate / 12.0) / 100.0
    current_principal = loan_amount
    total_interest_paid = 0.0
    total_principal_paid = 0.0
    
    for p in success_payments:
        # Calculate interest for this month based on outstanding principal
        interest_charge = current_principal * monthly_rate
        payment_amount = p["amount"]
        
        # Deduct interest, remainder reduces principal
        if payment_amount >= interest_charge:
            principal_reduction = payment_amount - interest_charge
            interest_paid = interest_charge
        else:
            principal_reduction = 0
            interest_paid = payment_amount
            
        # Update trackers
        current_principal -= principal_reduction
        total_interest_paid += interest_paid
        total_principal_paid += principal_reduction
        
        # Guard against negative principal
        if current_principal < 0:
            current_principal = 0.0
            
    # Calculate remaining EMIs
    remaining_balance = max(current_principal, 0.0)
    remaining_emis = 0
    if remaining_balance > 0 and emi > 0:
        # Simple estimation of remaining EMIs based on standard amortization
        # Or just divide balance by EMI
        remaining_emis = int(round(remaining_balance / emi))
        if remaining_emis == 0:
            remaining_emis = 1
            
    return {
        "original_principal": loan_amount,
        "total_principal_paid": round(total_principal_paid, 2),
        "total_interest_paid": round(total_interest_paid, 2),
        "outstanding_principal": round(remaining_balance, 2),
        "successful_payments_count": len(success_payments),
        "estimated_remaining_emis": remaining_emis
    }

def get_unified_borrower_context(borrower_id: str) -> dict:
    """
    Aggregates database records from CRM, Core Lending, Payments, Tickets, and Memory 
    to construct a single Unified Borrower Context object.
    """
    borrower = database.get_borrower(borrower_id)
    if not borrower:
        return {}
        
    payments = database.get_payment_history(borrower_id)
    tickets = database.get_tickets(borrower_id)
    conversations = database.get_conversations(borrower_id)
    memory = database.get_memory(borrower_id)
    
    # Calculate operational metrics
    loan_breakdown = calculate_loan_breakdown(borrower, payments)
    outstanding_penalty = get_outstanding_fees_and_penalties(borrower, payments)
    
    # Analyze recent payment failures (last 30 days)
    recent_failures = []
    for p in payments:
        if p["status"] in ["Failed", "Auto-Debit Failed"]:
            recent_failures.append({
                "payment_id": p["payment_id"],
                "amount": p["amount"],
                "date": p["payment_date"],
                "failure_reason": p["failure_reason"],
                "payment_method": p["payment_method"]
            })
            
    # Construct Context Engine Object
    unified_context = {
        "borrower_id": borrower["borrower_id"],
        "name": borrower["name"],
        "phone": borrower["phone"],
        "loan": {
            "loan_id": borrower["loan_id"],
            "loan_amount": borrower["loan_amount"],
            "interest_rate": borrower["interest_rate"],
            "emi_amount": borrower["emi_amount"],
            "loan_start_date": borrower["loan_start_date"],
            "loan_end_date": borrower["loan_end_date"],
            "delinquency_status": borrower["delinquency_status"],
            "kyc_status": borrower["kyc_status"],
            "risk_score": borrower["risk_score"],
            "preferred_language": borrower["preferred_language"],
            "breakdown": loan_breakdown
        },
        "operational": {
            "outstanding_penalty": outstanding_penalty,
            "recent_payment_failures": recent_failures,
            "has_open_tickets": any(t["status"] == "Open" for t in tickets),
            "open_tickets_count": sum(1 for t in tickets if t["status"] == "Open")
        },
        "interaction_history": {
            "tickets": [
                {
                    "ticket_id": t["ticket_id"],
                    "title": t["title"],
                    "category": t["category"],
                    "status": t["status"],
                    "created_at": t["created_at"],
                    "resolution_notes": t["resolution_notes"]
                }
                for t in tickets
            ],
            "past_conversations": [
                {
                    "conversation_id": c["conversation_id"],
                    "timestamp": c["timestamp"],
                    "summary": c["summary"],
                    "sentiment": c["sentiment"],
                    "outcome": c["outcome"]
                }
                for c in conversations
            ]
        },
        "memory": {
            "promises": memory.get("promises", []),
            "preferences": memory.get("preferences", {}),
            "outstanding_issues": memory.get("outstanding_issues", []),
            "agent_success_paths": memory.get("agent_success_paths", [])
        }
    }
    
    return unified_context
