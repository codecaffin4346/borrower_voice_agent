import os
import random
import uuid
import json
from datetime import datetime, timedelta
import database

# Seed for reproducibility
random.seed(42)

# Names and details generators
FIRST_NAMES = [
    "Rajesh", "Amit", "Priya", "Sunita", "Rahul", "Anjali", "Sanjay", "Deepa", "Vikram", "Neha",
    "Arjun", "Karan", "Sneha", "Aditya", "Rohan", "Pooja", "Manish", "Divya", "Suresh", "Ramesh",
    "Kiran", "Vijay", "Aisha", "Harish", "Preeti", "Alok", "Shweta", "Anil", "Meera", "Gaurav"
]
LAST_NAMES = [
    "Sharma", "Verma", "Gupta", "Kumar", "Singh", "Patel", "Joshi", "Mehta", "Reddy", "Nair",
    "Choudhury", "Das", "Sen", "Rao", "Iyer", "Mishra", "Pandey", "Saxena", "Trivedi", "Shah"
]

POLICY_DOCS = [
    # Loan FAQs (5 documents)
    {
        "doc_id": "KB_FAQ_001",
        "category": "FAQ",
        "title": "What is an EMI and how is it calculated?",
        "content": "An Equated Monthly Installment (EMI) is a fixed payment amount made by a borrower to a lender at a specified date each calendar month. EMIs are used to pay off both interest and principal each month so that over a specified number of years, the loan is paid off in full. The formula for EMI calculation is: EMI = [P x R x (1+R)^N]/[((1+R)^N)-1], where P is the Principal loan amount, R is the monthly interest rate (annual rate divided by 12 and then by 100), and N is the number of monthly installments."
    },
    {
        "doc_id": "KB_FAQ_002",
        "category": "FAQ",
        "title": "What happens if I miss my EMI payment date?",
        "content": "If you miss your EMI payment date, your account status is changed to delinquent. A late payment charge or bounce charge of INR 500 is applied, and interest is charged on the overdue amount at an overdue interest rate of 2% per month (24% per annum) calculated on a daily basis from the due date until the payment is received. Additionally, your credit score (CIBIL) is negatively impacted since payment delays are reported to credit bureaus."
    },
    {
        "doc_id": "KB_FAQ_003",
        "category": "FAQ",
        "title": "Can I change my EMI due date?",
        "content": "Borrowers can request a change of their monthly EMI due date (typically choices are 1st, 5th, 10th, or 15th of the month) by submitting a formal request via the Support Desk. Due date changes are subject to an administrative fee of INR 1000 and can only be done if there are no active delinquencies or unpaid penalties on the account, and the current loan has run for at least 6 months."
    },
    {
        "doc_id": "KB_FAQ_004",
        "category": "FAQ",
        "title": "What is NACH/Auto-Debit and how do I register?",
        "content": "National Automated Clearing House (NACH) is a centralized system launched by the NPCI to facilitate high-volume, repetitive electronic transactions. Borrowers register a NACH mandate to automate their EMI payments directly from their bank account on the due date. To register, you can submit an e-mandate request online using Netbanking/Debit Card, or submit a physical signed mandate form. It takes 7-10 working days for NACH activation. During this time, payments must be made manually via payment links."
    },
    {
        "doc_id": "KB_FAQ_005",
        "category": "FAQ",
        "title": "How is interest calculated on my loan?",
        "content": "Interest is calculated on a monthly reducing balance basis. Under this method, interest is calculated every month on the outstanding principal balance. As you pay your EMI each month, a portion goes toward reducing the principal balance, and the interest for the next month is calculated only on the remaining principal. This means the interest component of your EMI decreases over time while the principal repayment component increases."
    },
    
    # Foreclosure Policy (3 documents)
    {
        "doc_id": "KB_POL_FC_001",
        "category": "Policy",
        "title": "Foreclosure Eligibility and Charges",
        "content": "Foreclosure refers to the full prepayment of the outstanding loan principal before the scheduled end of the loan tenure. Borrowers are eligible for foreclosure only after successful completion of at least 6 months' EMIs. The foreclosure charges are: (a) For floating rate loans: 0% foreclosure charges for individual borrowers. (b) For fixed-rate loans: 4% of the outstanding principal amount at the time of foreclosure. All outstanding EMIs, late payment charges, and interest accrued up to the foreclosure date must be cleared before processing."
    },
    {
        "doc_id": "KB_POL_FC_002",
        "category": "Policy",
        "title": "Step-by-Step Foreclosure Process",
        "content": "To foreclose a loan: 1. The borrower must raise a 'Foreclosure Request' ticket or contact support. 2. The support system generates a Foreclosure Letter detailing the outstanding balance, interest till date, foreclosure charges, and validity date (typically 7 days). 3. The borrower makes the full payment using the custom foreclosure payment link. 4. Upon verification, the account is closed and a No Objection Certificate (NOC) is dispatched via email and registered post within 15 working days."
    },
    {
        "doc_id": "KB_POL_FC_003",
        "category": "Policy",
        "title": "Refunding Excess Foreclosure Payments",
        "content": "If a borrower pays more than the foreclosure amount stated in their Foreclosure Letter, the excess amount is refunded directly to their registered bank account. The refund process is triggered automatically within 5 working days of loan closure verification. No manual ticket is required, but if the refund is not received within 10 days, the borrower should raise a payment dispute ticket."
    },

    # Settlement Policy (3 documents)
    {
        "doc_id": "KB_POL_ST_001",
        "category": "Policy",
        "title": "One-Time Settlement (OTS) Eligibility Criteria",
        "content": "One-Time Settlement (OTS) is a resolution mechanism offered only to borrowers facing extreme, verified financial distress (such as severe medical emergency, death of primary earner, or loss of livelihood) and whose accounts have been delinquent for more than 90 days (NPA status). OTS is a last resort and results in a 'Settled' status on credit reports, which negatively impacts credit scores for up to 7 years. The minimum settlement amount is generally the principal outstanding amount, and all waivers of interest and penalties are subject to Credit Committee approval."
    },
    {
        "doc_id": "KB_POL_ST_002",
        "category": "Policy",
        "title": "Settlement Request Documentation and Approval",
        "content": "To apply for an OTS, the borrower must submit: 1. An OTS application letter outlining the reason for default. 2. Financial proof (bank statements for last 6 months, income tax returns, or termination letters). 3. Supporting evidence of distress (medical reports, death certificate, etc.). The agent raises a support ticket of category 'Settlement Request' attaching the files. A credit manager reviews the case and issues a formal Settlement Offer Letter detailing the agreed amount and payment schedule (maximum 3 installments)."
    },
    {
        "doc_id": "KB_POL_ST_003",
        "category": "Policy",
        "title": "Effects of Settlement on Credit Score and Future Loans",
        "content": "Settling a loan is not the same as closing a loan. In a foreclosure or normal closure, the lender reports the status to CIBIL as 'Closed' or 'Written Off - Fully Paid'. In a settlement, the status is reported as 'Settled'. A settled status flags the borrower as a high-risk individual who failed to repay the full contractual obligation, making it extremely difficult to obtain loans or credit cards from any financial institution for a period of 5 to 7 years."
    },

    # Late Payment Policy (3 documents)
    {
        "doc_id": "KB_POL_LP_001",
        "category": "Policy",
        "title": "Late Payment Charges and Grace Periods",
        "content": "EMIs are due on the designated due date of every month. A grace period of 3 calendar days is provided. If the payment is not credited to the lender's account by 11:59 PM on the 3rd day after the due date, a late payment fee of INR 500 is applied. In addition, penal interest at the rate of 2% per month (calculated daily) is levied on the overdue EMI amount from the original due date until the date of actual payment."
    },
    {
        "doc_id": "KB_POL_LP_002",
        "category": "Policy",
        "title": "Loan Delinquency Tiers and Recovery Actions",
        "content": "Delinquency is categorized into tiers based on Days Past Due (DPD): 1. DPD 1-30 (SMA-0): Telephonic reminders, SMS notifications, and system alerts. 2. DPD 31-60 (SMA-1): Collection team assignments, intensive follow-up calls, and physical visitation if unresponsive. 3. DPD 61-90 (SMA-2): Formal legal notice dispatch, reference contacts, and pre-action notifications. 4. DPD 90+ (NPA): Legal recovery proceedings under Section 138 of Negotiable Instruments Act or arbitration, and credit reporting as Default/NPA."
    },
    {
        "doc_id": "KB_POL_LP_003",
        "category": "Policy",
        "title": "Promise-to-Pay (PTP) Commitment Guidelines",
        "content": "A Promise-to-Pay (PTP) is a formal commitment made by a delinquent borrower regarding the exact date and amount they will pay to clear their arrears. Agents can register a PTP in the system. The commitment date must not exceed 10 calendar days from the call date. If a borrower breaks a PTP commitment, the account is immediately escalated to the high-risk recovery queue, and any active waiver requests are cancelled."
    },

    # Penalty Waiver Policy (3 documents)
    {
        "doc_id": "KB_POL_PW_001",
        "category": "Policy",
        "title": "Penalty Fee Waiver Eligibility",
        "content": "Late payment fees and penal interest can only be waived under specific conditions: 1. The delay was caused by a documented system glitch on the lender's side or payment gateway failure (verified via payment logs). 2. The delay was due to a bank-side technical glitch (e.g. NACH mandate failure despite sufficient balance, supported by a bank transaction failure statement). 3. The borrower has a perfect payment track record (no delinquencies in the last 12 months) and defaulted due to temporary emergency, subject to a one-time limit per loan. The maximum waiver amount an agent can approve autonomously is INR 1000; higher amounts require Credit Supervisor approval."
    },
    {
        "doc_id": "KB_POL_PW_002",
        "category": "Policy",
        "title": "Procedure for Submitting a Penalty Waiver Request",
        "content": "To submit a penalty waiver request: 1. The agent verifies the borrower's payment history and the payment logs. 2. If eligible, the agent creates a 'Penalty Waiver Request' ticket. 3. The ticket must include the payment attempt reference ID, the failure reason, and the borrower's bank statement showing sufficient balance on the due date. 4. The operations team reviews and approves/rejects the waiver within 48 hours. If approved, the waived amount is credited back to the loan account, reducing the outstanding balance."
    },
    {
        "doc_id": "KB_POL_PW_003",
        "category": "Policy",
        "title": "Waiver Thresholds and Agent Autonomy",
        "content": "Agents have the following delegation of authority limits for fee waivers: (a) Tier 1 Agent: Up to INR 500 (covers single bounce fee). (b) Tier 2 / Senior Representative: Up to INR 2000. (c) Credit Manager: Up to INR 10,000. Any waiver exceeding INR 10,000 or involving principal concessions requires Credit Committee approval. All waivers must be backed by system audit logs or documentation."
    },

    # Payment Failure Handling Process (3+ documents)
    {
        "doc_id": "KB_POL_PF_001",
        "category": "Policy",
        "title": "Auto-Debit/NACH Failure Analysis and Resolution",
        "content": "When a NACH/Auto-Debit transaction fails, the payment gateway returns a specific error code. The main failure reasons are: 1. 'Insufficient Balance' (Code: E01): The customer did not have enough funds. Customer responsibility; late fee applies. 2. 'Account Blocked/Dormant' (Code: E08): Customer's bank account is inactive. Customer must update bank details. 3. 'Network/Gateway Timeout' (Code: E99): Technical error between gateway and bank. System responsibility; late fee is eligible for waiver. 4. 'Mandate Not Found' (Code: E03): Mandate is either not registered or cancelled. Customer must re-register NACH."
    },
    {
        "doc_id": "KB_POL_PF_002",
        "category": "Policy",
        "title": "How to Handle Bank Glitch Claims",
        "content": "If a borrower claims their payment failed due to a bank glitch despite having sufficient balance: 1. Check the payment history and payment gateway log for the transaction on the due date. 2. If the gateway log shows status 'Failed' with reason 'Bank Timeout', 'Internal Server Error', or 'Network Error', the claim is verified. 3. Instruct the borrower to make a manual payment using the payment link sent via SMS. 4. Initiate a penalty waiver ticket to waive the late fees applied due to this failed transaction."
    },
    {
        "doc_id": "KB_POL_PF_003",
        "category": "Policy",
        "title": "Generating and Sending Payment Links",
        "content": "For borrowers who experience auto-debit failure or wish to make manual payments, agents can trigger a secure payment link via the toolset. The system integrates with Stripe/Razorpay Sandboxes to create a unique checkout URL. This link is sent to the borrower's registered mobile number and email. Payment links remain active for 48 hours. Once paid, the core lending system is updated in real-time, clearing the delinquency."
    }
]

def generate_dataset():
    # Ensure database is initialized
    database.init_db()
    
    conn = database.get_connection()
    cursor = conn.cursor()
    
    # Clean existing data to avoid primary key collisions if script is re-run
    cursor.execute("DELETE FROM workflow_logs")
    cursor.execute("DELETE FROM memory")
    cursor.execute("DELETE FROM conversation_history")
    cursor.execute("DELETE FROM kb_documents")
    cursor.execute("DELETE FROM tickets")
    cursor.execute("DELETE FROM payment_history")
    cursor.execute("DELETE FROM borrowers")
    conn.commit()
    
    print("Database cleared. Generating synthetic data...")
    
    # 1. Insert KB Documents
    for doc in POLICY_DOCS:
        cursor.execute(
            "INSERT INTO kb_documents (doc_id, title, category, content) VALUES (?, ?, ?, ?)",
            (doc["doc_id"], doc["title"], doc["category"], doc["content"])
        )
    conn.commit()
    print(f"Inserted {len(POLICY_DOCS)} policy documents into Knowledge Base.")
    
    # Prepare specific borrowers for Demo Scenarios
    # Scenario 1: Remaining EMI Inquiry
    # Scenario 2: Interest Paid Inquiry
    # Scenario 3: Penalty Charge Inquiry
    # Scenario 4: Payment Failure Bank Glitch
    # Scenario 5: Penalty Waiver Request
    # Scenario 6: Follow-Up Call with Memory
    
    # Let's pre-define some special borrowers corresponding to the scenarios
    SPECIAL_BORROWERS = [
        # Scenario 1: Remaining EMI Inquiry
        {
            "borrower_id": "BORR_S1_EMI",
            "name": "Amit Sharma",
            "phone": "+919876543210",
            "loan_id": "LN_EMI_101",
            "loan_amount": 300000.0,
            "interest_rate": 12.0,
            "emi_amount": 10000.0, # 300,000 @ 12% for 36 months is roughly ~10,000
            "loan_start_date": "2024-01-10",
            "loan_end_date": "2027-01-10",
            "delinquency_status": "Current",
            "kyc_status": "Verified",
            "risk_score": 15,
            "preferred_language": "English"
        },
        # Scenario 2: Interest Paid Inquiry
        {
            "borrower_id": "BORR_S2_INT",
            "name": "Priya Verma",
            "phone": "+919876543211",
            "loan_id": "LN_INT_202",
            "loan_amount": 500000.0,
            "interest_rate": 10.0,
            "emi_amount": 15000.0,
            "loan_start_date": "2023-06-15",
            "loan_end_date": "2026-12-15",
            "delinquency_status": "Current",
            "kyc_status": "Verified",
            "risk_score": 10,
            "preferred_language": "Hindi"
        },
        # Scenario 3: Penalty Charge Inquiry
        {
            "borrower_id": "BORR_S3_PEN",
            "name": "Rahul Kumar",
            "phone": "+919876543212",
            "loan_id": "LN_PEN_303",
            "loan_amount": 150000.0,
            "interest_rate": 14.0,
            "emi_amount": 8000.0,
            "loan_start_date": "2025-09-05",
            "loan_end_date": "2027-09-05",
            "delinquency_status": "Delinquent (1-15 days)",
            "kyc_status": "Verified",
            "risk_score": 45,
            "preferred_language": "English"
        },
        # Scenario 4: Payment Failure Bank Glitch
        {
            "borrower_id": "BORR_S4_GLI",
            "name": "Sunita Patel",
            "phone": "+919876543213",
            "loan_id": "LN_GLI_404",
            "loan_amount": 250000.0,
            "interest_rate": 11.5,
            "emi_amount": 9500.0,
            "loan_start_date": "2025-02-05",
            "loan_end_date": "2028-02-05",
            "delinquency_status": "Delinquent (1-15 days)",
            "kyc_status": "Verified",
            "risk_score": 30,
            "preferred_language": "Hindi"
        },
        # Scenario 5: Penalty Waiver Request
        {
            "borrower_id": "BORR_S5_WAI",
            "name": "Sanjay Gupta",
            "phone": "+919876543214",
            "loan_id": "LN_WAI_505",
            "loan_amount": 400000.0,
            "interest_rate": 13.0,
            "emi_amount": 12000.0,
            "loan_start_date": "2024-05-20",
            "loan_end_date": "2027-05-20",
            "delinquency_status": "Delinquent (1-15 days)",
            "kyc_status": "Verified",
            "risk_score": 25,
            "preferred_language": "English"
        },
        # Scenario 6: Follow-Up Call with Memory
        {
            "borrower_id": "BORR_S6_MEM",
            "name": "Karan Singh",
            "phone": "+919876543215",
            "loan_id": "LN_MEM_606",
            "loan_amount": 200000.0,
            "interest_rate": 12.5,
            "emi_amount": 7500.0,
            "loan_start_date": "2024-11-01",
            "loan_end_date": "2027-11-01",
            "delinquency_status": "Delinquent (16-30 days)",
            "kyc_status": "Verified",
            "risk_score": 60,
            "preferred_language": "English"
        }
    ]
    
    borrowers_data = SPECIAL_BORROWERS.copy()
    
    # Generate remaining 94 borrowers to reach 100+ total
    for i in range(1, 96):
        b_id = f"BORR_{1000 + i}"
        name = f"{random.choice(FIRST_NAMES)} {random.choice(LAST_NAMES)}"
        phone = f"+91{random.randint(7000000000, 9999999999)}"
        loan_id = f"LN_{2000 + i}"
        
        loan_amount = float(random.choice([100000, 150000, 200000, 250000, 300000, 400000, 500000]))
        interest_rate = float(random.choice([9.5, 10.0, 11.0, 12.0, 13.0, 14.0, 15.0]))
        # Approximate monthly EMI
        tenure_months = random.choice([12, 24, 36, 48, 60])
        emi_amount = float(round((loan_amount * (1 + (interest_rate/100) * (tenure_months/12))) / tenure_months, -2))
        
        # Dates
        start_date = datetime.now() - timedelta(days=random.randint(100, 600))
        end_date = start_date + timedelta(days=tenure_months * 30.5)
        
        # Delinquency status distribution
        status_rand = random.random()
        if status_rand < 0.70:
            delinquency = "Current"
        elif status_rand < 0.85:
            delinquency = "Delinquent (1-15 days)"
        elif status_rand < 0.95:
            delinquency = "Delinquent (16-30 days)"
        else:
            delinquency = "Delinquent (30+ days)"
            
        kyc = random.choice(["Verified", "Verified", "Verified", "Pending"])
        risk = random.randint(5, 95)
        language = random.choice(["English", "English", "Hindi"])
        
        borrowers_data.append({
            "borrower_id": b_id,
            "name": name,
            "phone": phone,
            "loan_id": loan_id,
            "loan_amount": loan_amount,
            "interest_rate": interest_rate,
            "emi_amount": emi_amount,
            "loan_start_date": start_date.strftime("%Y-%m-%d"),
            "loan_end_date": end_date.strftime("%Y-%m-%d"),
            "delinquency_status": delinquency,
            "kyc_status": kyc,
            "risk_score": risk,
            "preferred_language": language
        })
        
    for b in borrowers_data:
        cursor.execute(
            """INSERT INTO borrowers (
                borrower_id, name, phone, loan_id, loan_amount, interest_rate, 
                emi_amount, loan_start_date, loan_end_date, delinquency_status, 
                kyc_status, risk_score, preferred_language
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                b["borrower_id"], b["name"], b["phone"], b["loan_id"], b["loan_amount"],
                b["interest_rate"], b["emi_amount"], b["loan_start_date"], b["loan_end_date"],
                b["delinquency_status"], b["kyc_status"], b["risk_score"], b["preferred_language"]
            )
        )
    conn.commit()
    print(f"Generated {len(borrowers_data)} Borrower profiles.")
    
    # 2. Generate Payment History (500+ records)
    payments_data = []
    
    for b in borrowers_data:
        b_id = b["borrower_id"]
        l_id = b["loan_id"]
        emi = b["emi_amount"]
        start_dt = datetime.strptime(b["loan_start_date"], "%Y-%m-%d")
        
        # Calculate number of installments paid based on how long the loan has run
        days_run = (datetime.now() - start_dt).days
        months_run = int(days_run // 30.5)
        
        # Loop over months run
        for m in range(months_run):
            pay_date = start_dt + timedelta(days=m * 30.5 + random.randint(-2, 2))
            
            # Setup specific behaviors for special scenario borrowers
            if b_id == "BORR_S3_PEN" and m == months_run - 1:
                # Last EMI is failed / late, creating a penalty
                payments_data.append({
                    "payment_id": f"PAY_PEN_{m}",
                    "borrower_id": b_id,
                    "loan_id": l_id,
                    "amount": emi,
                    "payment_date": pay_date.strftime("%Y-%m-%d"),
                    "status": "Failed",
                    "failure_reason": "Insufficient Balance",
                    "payment_method": "Auto-Debit"
                })
                continue
                
            if b_id == "BORR_S4_GLI" and m == months_run - 1:
                # Gateway failure on due date
                payments_data.append({
                    "payment_id": f"PAY_GLI_{m}",
                    "borrower_id": b_id,
                    "loan_id": l_id,
                    "amount": emi,
                    "payment_date": pay_date.strftime("%Y-%m-%d"),
                    "status": "Auto-Debit Failed",
                    "failure_reason": "Bank Gateway Timeout",
                    "payment_method": "Auto-Debit"
                })
                continue
                
            if b_id == "BORR_S5_WAI" and m == months_run - 1:
                # Technical glitch, late payment fee charged
                payments_data.append({
                    "payment_id": f"PAY_WAI_{m}",
                    "borrower_id": b_id,
                    "loan_id": l_id,
                    "amount": emi,
                    "payment_date": pay_date.strftime("%Y-%m-%d"),
                    "status": "Auto-Debit Failed",
                    "failure_reason": "Network Timeout",
                    "payment_method": "Auto-Debit"
                })
                continue
                
            if b_id == "BORR_S6_MEM" and m == months_run - 1:
                # Delayed payment missed
                payments_data.append({
                    "payment_id": f"PAY_MEM_{m}",
                    "borrower_id": b_id,
                    "loan_id": l_id,
                    "amount": emi,
                    "payment_date": pay_date.strftime("%Y-%m-%d"),
                    "status": "Failed",
                    "failure_reason": "Insufficient Balance",
                    "payment_method": "Auto-Debit"
                })
                continue
                
            # Normal distribution of success/failure for regular borrowers
            rand_val = random.random()
            
            if rand_val < 0.90:
                # Successful Payment
                payments_data.append({
                    "payment_id": f"PAY_{b_id}_{m}",
                    "borrower_id": b_id,
                    "loan_id": l_id,
                    "amount": emi,
                    "payment_date": pay_date.strftime("%Y-%m-%d"),
                    "status": "Success",
                    "failure_reason": None,
                    "payment_method": random.choice(["Auto-Debit", "Auto-Debit", "UPI", "Netbanking"])
                })
            elif rand_val < 0.94:
                # Failed due to insufficient balance
                payments_data.append({
                    "payment_id": f"PAY_{b_id}_{m}",
                    "borrower_id": b_id,
                    "loan_id": l_id,
                    "amount": emi,
                    "payment_date": pay_date.strftime("%Y-%m-%d"),
                    "status": "Failed",
                    "failure_reason": "Insufficient Balance",
                    "payment_method": "Auto-Debit"
                })
            elif rand_val < 0.97:
                # Auto-Debit Technical Failure
                payments_data.append({
                    "payment_id": f"PAY_{b_id}_{m}",
                    "borrower_id": b_id,
                    "loan_id": l_id,
                    "amount": emi,
                    "payment_date": pay_date.strftime("%Y-%m-%d"),
                    "status": "Auto-Debit Failed",
                    "failure_reason": random.choice(["Network Timeout", "Bank Server Down", "NACH Mandate Pending"]),
                    "payment_method": "Auto-Debit"
                })
            else:
                # Missed/Partial Payment
                payments_data.append({
                    "payment_id": f"PAY_{b_id}_{m}",
                    "borrower_id": b_id,
                    "loan_id": l_id,
                    "amount": emi * 0.5,
                    "payment_date": pay_date.strftime("%Y-%m-%d"),
                    "status": "Partial",
                    "failure_reason": "Partial payment by customer",
                    "payment_method": "UPI"
                })
                
    # Ensure we have at least 500 records. If not, add more random history
    while len(payments_data) < 550:
        b = random.choice(borrowers_data)
        pay_dt = datetime.now() - timedelta(days=random.randint(5, 360))
        payments_data.append({
            "payment_id": f"PAY_RAND_{uuid.uuid4().hex[:6]}",
            "borrower_id": b["borrower_id"],
            "loan_id": b["loan_id"],
            "amount": b["emi_amount"],
            "payment_date": pay_dt.strftime("%Y-%m-%d"),
            "status": random.choice(["Success", "Success", "Failed"]),
            "failure_reason": "Insufficient Balance" if random.random() > 0.8 else None,
            "payment_method": "UPI"
        })
        
    for p in payments_data:
        cursor.execute(
            """INSERT INTO payment_history (
                payment_id, borrower_id, loan_id, amount, payment_date, 
                status, failure_reason, payment_method
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                p["payment_id"], p["borrower_id"], p["loan_id"], p["amount"], p["payment_date"],
                p["status"], p["failure_reason"], p["payment_method"]
            )
        )
    conn.commit()
    print(f"Generated {len(payments_data)} Payment history records.")
    
    # 3. Generate Support Tickets (100+ records)
    tickets_data = []
    
    # Pre-populate specific ticket cases for Scenarios
    # Scenario 3: Penalty dispute
    tickets_data.append({
        "ticket_id": "TCK_PEN_303",
        "borrower_id": "BORR_S3_PEN",
        "title": "Dispute late fee charges",
        "description": "Borrower claims they should not be charged INR 500 since their balance was sufficient but bank transfer failed.",
        "category": "EMI Dispute",
        "status": "Open",
        "created_at": (datetime.now() - timedelta(days=2)).strftime("%Y-%m-%d %H:%M:%S"),
        "resolution_notes": None
    })
    # Scenario 5: Penalty waiver
    tickets_data.append({
        "ticket_id": "TCK_WAI_505",
        "borrower_id": "BORR_S5_WAI",
        "title": "Late fee waiver requested for bank glitch",
        "description": "Auto-debit failed due to network timeout. Customer requesting refund of late charges.",
        "category": "Penalty Waiver Request",
        "status": "Open",
        "created_at": (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d %H:%M:%S"),
        "resolution_notes": None
    })
    
    categories = ["EMI Dispute", "Settlement Request", "Foreclosure Inquiry", "Payment Failure Complaint", "Penalty Waiver Request"]
    
    for i in range(1, 105):
        b = random.choice(borrowers_data)
        category = random.choice(categories)
        status = random.choice(["Open", "In Progress", "Resolved", "Closed"])
        created = datetime.now() - timedelta(days=random.randint(5, 120))
        
        title = f"Ticket regarding {category}"
        description = f"Borrower {b['name']} called regarding a {category.lower()} on loan {b['loan_id']}."
        res_notes = "Resolved as per company terms." if status in ["Resolved", "Closed"] else None
        
        tickets_data.append({
            "ticket_id": f"TCK_{1000 + i}",
            "borrower_id": b["borrower_id"],
            "title": title,
            "description": description,
            "category": category,
            "status": status,
            "created_at": created.strftime("%Y-%m-%d %H:%M:%S"),
            "resolution_notes": res_notes
        })
        
    for t in tickets_data:
        cursor.execute(
            """INSERT INTO tickets (
                ticket_id, borrower_id, title, description, category, status, created_at, resolution_notes
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                t["ticket_id"], t["borrower_id"], t["title"], t["description"], t["category"], 
                t["status"], t["created_at"], t["resolution_notes"]
            )
        )
    conn.commit()
    print(f"Generated {len(tickets_data)} Support Tickets.")
    
    # 4. Generate Conversation History (100+ records)
    conversations_data = []
    
    # Preset for Scenario 6: First Call history where borrower makes a PTP commitment
    conversations_data.append({
        "conversation_id": "CONV_MEM_606_CALL1",
        "borrower_id": "BORR_S6_MEM",
        "timestamp": (datetime.now() - timedelta(days=5)).strftime("%Y-%m-%d %H:%M:%S"),
        "transcript": json.dumps([
            {"sender": "agent", "text": "Hello, this is Credit Servicing support. Am I speaking with Karan Singh?"},
            {"sender": "borrower", "text": "Yes, I am Karan. I'm calling about my overdue EMI payment."},
            {"sender": "agent", "text": "Thank you, Karan. I see your EMI of INR 7,500 due on the 1st was missed, and the auto-debit failed. Is everything alright?"},
            {"sender": "borrower", "text": "Actually, my salary is delayed. I will make the payment next Friday, which is June 12th."},
            {"sender": "agent", "text": "Understood. I have recorded your commitment to pay INR 7,500 by next Friday, June 12th. Please try to complete it then to avoid further delinquency fees."},
            {"sender": "borrower", "text": "Yes, I will do that. Thank you."}
        ]),
        "summary": "Borrower called to explain EMI delay. Committed to pay INR 7,500 by next Friday (June 12th) due to salary delay.",
        "sentiment": "Neutral",
        "outcome": "Logged Promise-to-Pay for 2026-06-12"
    })
    
    # Generate 100+ standard conversation records
    sentiments = ["Positive", "Neutral", "Negative"]
    outcomes = [
        "Informed remaining tenure", "Sent payment link", "Created waiver ticket", 
        "Escalated foreclosure to supervisor", "Scheduled callback", "Explained delinquency fees"
    ]
    
    for i in range(1, 105):
        b = random.choice(borrowers_data)
        ts = datetime.now() - timedelta(days=random.randint(10, 150))
        
        # Simple sample dialogue transcript
        dial = [
            {"sender": "agent", "text": f"Hello, thank you for calling. Am I speaking with {b['name']}?"},
            {"sender": "borrower", "text": "Yes, that's me."},
            {"sender": "agent", "text": "How can I help you today?"},
            {"sender": "borrower", "text": "I wanted to check my account balance and if my recent EMI got processed."},
            {"sender": "agent", "text": f"Let me pull up your account. Yes, your last EMI of INR {b['emi_amount']} was successfully paid. Your account is current."},
            {"sender": "borrower", "text": "Perfect, thanks for confirming."},
            {"sender": "agent", "text": "Is there anything else I can assist you with?"},
            {"sender": "borrower", "text": "No, that's all. Thank you."}
        ]
        
        conversations_data.append({
            "conversation_id": f"CONV_{1000 + i}",
            "borrower_id": b["borrower_id"],
            "timestamp": ts.strftime("%Y-%m-%d %H:%M:%S"),
            "transcript": json.dumps(dial),
            "summary": f"Borrower called to check EMI payment status. Confirmed payment of INR {b['emi_amount']}.",
            "sentiment": random.choice(sentiments),
            "outcome": random.choice(outcomes)
        })
        
    for c in conversations_data:
        cursor.execute(
            """INSERT INTO conversation_history (
                conversation_id, borrower_id, timestamp, transcript, summary, sentiment, outcome
            ) VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (
                c["conversation_id"], c["borrower_id"], c["timestamp"], c["transcript"], 
                c["summary"], c["sentiment"], c["outcome"]
            )
        )
    conn.commit()
    print(f"Generated {len(conversations_data)} Conversation logs.")
    
    # 5. Populate initial Memory state for Scenario 6
    # Let's populate the Memory table for BORR_S6_MEM so the agent retrieves it on call start
    cursor.execute(
        """
        INSERT INTO memory (borrower_id, promises, preferences, outstanding_issues, agent_success_paths, last_interaction)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (
            "BORR_S6_MEM",
            json.dumps([{
                "amount": 7500.0,
                "date": "2026-06-12",
                "reason": "Salary delayed",
                "status": "Pending",
                "created_at": (datetime.now() - timedelta(days=5)).strftime("%Y-%m-%d")
            }]),
            json.dumps({
                "communication_style": "Cooperative but financially constrained",
                "preferred_language": "English",
                "tone": "Reassuring, structured"
            }),
            json.dumps(["Late fee applied due to June 1st default"]),
            json.dumps(["Confirming salary date first leads to clear commitments"]),
            (datetime.now() - timedelta(days=5)).strftime("%Y-%m-%d %H:%M:%S")
        )
    )
    conn.commit()
    print("Populated initial memory state for memory demonstration borrower.")
    
    conn.close()
    print("Database seeding completed successfully.")

if __name__ == "__main__":
    generate_dataset()
