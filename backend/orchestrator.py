import os
import json
import re
from datetime import datetime, timedelta
import database
import context_engine
import diagnosis_layer
import memory_engine
import rag_engine

# Attempt to import Gemini SDK
try:
    import google.generativeai as genai
    HAS_GEMINI_SDK = True
except ImportError:
    HAS_GEMINI_SDK = False

# Load dotenv if present
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

if HAS_GEMINI_SDK and GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
    print("Gemini API configured successfully.")
else:
    print("Gemini API key not found or SDK not installed. Operating in high-fidelity Mock Agent mode.")

# Global active sessions dictionary to keep track of calls in progress
# Session keys: borrower_id -> { turns: [...], start_time: ... }
ACTIVE_SESSIONS = {}

def get_session(borrower_id: str):
    if borrower_id not in ACTIVE_SESSIONS:
        # Fetch initial context to understand preferred language
        ctx = context_engine.get_unified_borrower_context(borrower_id)
        lang = ctx.get("loan", {}).get("preferred_language", "English")
        
        # Initial greeting based on borrower context and language
        name = ctx.get("name", "Borrower")
        delinquent = ctx.get("loan", {}).get("delinquency_status", "Current") != "Current"
        
        # Scenario 6: Follow-up Call with Memory
        promises = ctx.get("memory", {}).get("promises", [])
        pending_ptps = [p for p in promises if p.get("status") == "Pending"]
        
        greeting = f"Hello {name}, thank you for calling Credit Servicing. How can I assist you today?"
        
        if lang == "Hindi":
            greeting = f"नमस्ते {name}, क्रेडिट सर्विसिंग में कॉल करने के लिए धन्यवाद। आज मैं आपकी क्या सहायता कर सकता हूँ?"
            
        if pending_ptps:
            last_ptp = pending_ptps[-1]
            # Formulate memory-aware greeting
            if lang == "Hindi":
                greeting = f"नमस्ते {name}। पिछली बातचीत में आपने बताया था कि शुक्रवार को वेतन मिलने पर आप EMI भुगतान करेंगे। क्या आपका भुगतान पूरा हो पाया?"
            else:
                greeting = f"Hello {name}. During our previous conversation, you mentioned that you expected your salary on Friday and planned to make the EMI payment afterward. Were you able to complete the payment?"
        elif delinquent:
            outstanding = ctx.get("loan", {}).get("emi_amount", 0.0)
            if lang == "Hindi":
                greeting = f"नमस्ते {name}, मैं देख पा रहा हूँ कि आपका INR {outstanding} का भुगतान बकाया है। क्या आप इस संबंध में कॉल कर रहे हैं?"
            else:
                greeting = f"Hello {name}, I noticed your EMI payment of INR {outstanding} is currently overdue. Are you calling regarding this?"
        
        ACTIVE_SESSIONS[borrower_id] = {
            "turns": [{"sender": "agent", "text": greeting}],
            "start_time": datetime.now()
        }
    return ACTIVE_SESSIONS[borrower_id]

def reset_session(borrower_id: str):
    if borrower_id in ACTIVE_SESSIONS:
        del ACTIVE_SESSIONS[borrower_id]

def trigger_n8n_webhook(action_type: str, payload: dict) -> dict:
    """
    Simulates sending a webhook trigger to n8n/Zapier/Make.
    If a WORKFLOW_WEBHOOK_URL is set in environment, it does a real POST.
    Otherwise, logs to the database and returns success.
    """
    webhook_url = os.environ.get("WORKFLOW_WEBHOOK_URL")
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_id = f"WF_LOG_{uuid_short()}"
    
    payload_str = json.dumps(payload)
    print(f"Triggering Workflow Automation [{action_type}] webhook...")
    
    if webhook_url:
        import urllib.request
        try:
            req = urllib.request.Request(
                webhook_url,
                data=payload_str.encode('utf-8'),
                headers={'Content-Type': 'application/json'}
            )
            with urllib.request.urlopen(req, timeout=5) as response:
                resp_text = response.read().decode('utf-8')
            database.add_workflow_log(log_id, timestamp, action_type, payload_str, webhook_url, "Success", resp_text)
            return {"status": "Success", "details": f"Dispatched to external webhook: {resp_text}"}
        except Exception as e:
            database.add_workflow_log(log_id, timestamp, action_type, payload_str, webhook_url, "Failed", str(e))
            return {"status": "Failed", "details": f"Error posting to webhook: {str(e)}"}
    else:
        # Simulated success log
        database.add_workflow_log(log_id, timestamp, action_type, payload_str, "Simulated_n8n_Endpoint", "Success", "Webhook Simulated Successfully")
        return {"status": "Success", "details": "Logged locally to workflow simulator dashboard"}

def execute_agent_tools(borrower_id: str, action_list: list) -> list:
    """
    Executes tools requested by the Agent (e.g. ticket creation, payments, callbacks).
    """
    executed_results = []
    
    for action in action_list:
        a_type = action.get("type")
        
        if a_type == "generate_payment_link":
            # Generate simulated sandbox Stripe/Razorpay link
            pay_id = f"PAY_LINK_{uuid_short()}"
            link = f"https://sandbox.razorpay.com/pay/{pay_id}?amount={action.get('amount', 5000)}"
            
            # Record workflow webhook trigger for payment link dispatch
            trigger_res = trigger_n8n_webhook("Send Payment Link", {
                "borrower_id": borrower_id,
                "payment_id": pay_id,
                "link": link,
                "amount": action.get("amount")
            })
            
            executed_results.append({
                "action": "generate_payment_link",
                "status": "Success",
                "details": f"Generated Razorpay link: {link}",
                "workflow_status": trigger_res["status"]
            })
            
        elif a_type == "create_ticket":
            t_id = f"TCK_AUTO_{uuid_short()}"
            database.create_ticket(
                ticket_id=t_id,
                borrower_id=borrower_id,
                title=action.get("title", "Service Ticket"),
                description=action.get("description", "Agent created support ticket."),
                category=action.get("category", "General Query"),
                status="Open",
                created_at=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            )
            
            # Send notification webhook
            trigger_res = trigger_n8n_webhook("Create Ticket Alert", {
                "ticket_id": t_id,
                "borrower_id": borrower_id,
                "title": action.get("title"),
                "category": action.get("category")
            })
            
            executed_results.append({
                "action": "create_ticket",
                "status": "Success",
                "details": f"Created ticket {t_id} under category '{action.get('category')}'",
                "workflow_status": trigger_res["status"]
            })
            
        elif a_type == "schedule_callback":
            # Log callback trigger
            trigger_res = trigger_n8n_webhook("Schedule Callback", {
                "borrower_id": borrower_id,
                "time": action.get("time", "Tomorrow morning")
            })
            
            executed_results.append({
                "action": "schedule_callback",
                "status": "Success",
                "details": f"Scheduled callback for {action.get('time', 'next business hours')}",
                "workflow_status": trigger_res["status"]
            })
            
        elif a_type == "waive_penalty":
            # Waive fee: update delinquency status, clear penalty, and log a ticket
            conn = database.get_connection()
            # Clear delinquency status to 'Current'
            conn.execute(
                "UPDATE borrowers SET delinquency_status = 'Current' WHERE borrower_id = ?", 
                (borrower_id,)
            )
            # Find and set failed payments to settled or waived in mock
            conn.execute(
                "UPDATE payment_history SET status = 'Success' WHERE borrower_id = ? AND status IN ('Failed', 'Auto-Debit Failed')", 
                (borrower_id,)
            )
            conn.commit()
            conn.close()
            
            # Log ticket
            t_id = f"TCK_WAI_{uuid_short()}"
            database.create_ticket(
                ticket_id=t_id,
                borrower_id=borrower_id,
                title="Automatic Fee Waiver Approved",
                description="Late payment charges waived due to verified bank-side technical glitch.",
                category="Penalty Waiver Request",
                status="Resolved",
                created_at=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            )
            
            # Update memory outstanding issues
            mem = database.get_memory(borrower_id)
            database.update_memory(
                borrower_id=borrower_id,
                promises=mem.get("promises", []),
                preferences=mem.get("preferences", {}),
                outstanding_issues=[],
                agent_success_paths=mem.get("agent_success_paths", []) + ["Penalty auto-waived based on bank proof"],
                last_interaction=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            )
            
            executed_results.append({
                "action": "waive_penalty",
                "status": "Success",
                "details": "Waived penalty charges. Updated database records."
            })
            
    return executed_results

def run_mock_agent(context: dict, diagnosis: dict, rag_docs: list, user_text: str) -> dict:
    """
    High-fidelity Rule-Based & Template Agent simulating Gemini responses.
    Accurately handles all 6 mandatory demo scenarios.
    """
    name = context.get("name", "Borrower")
    loan_id = context.get("loan", {}).get("loan_id", "")
    emi = context.get("loan", {}).get("emi_amount", 0.0)
    outstanding_bal = context.get("loan", {}).get("breakdown", {}).get("outstanding_principal", 0.0)
    interest_paid = context.get("loan", {}).get("breakdown", {}).get("total_interest_paid", 0.0)
    principal_paid = context.get("loan", {}).get("breakdown", {}).get("total_principal_paid", 0.0)
    remaining_emis = context.get("loan", {}).get("breakdown", {}).get("estimated_remaining_emis", 0)
    end_date = context.get("loan", {}).get("loan_end_date", "")
    penalty = context.get("operational", {}).get("outstanding_penalty", 0.0)
    lang = context.get("loan", {}).get("preferred_language", "English")
    
    extracted_memory = {}
    actions = []
    sentiment = "Neutral"
    
    # Analyze text sentiment
    user_text_lc = user_text.lower()
    if any(k in user_text_lc for k in ["angry", "bad", "worst", "ridiculous", "charge", "unfair", "stupid"]):
        sentiment = "Angry"
    elif any(k in user_text_lc for k in ["thank", "great", "nice", "appreciate", "helpful"]):
        sentiment = "Positive"
        
    # Scenario detection
    keywords = diagnosis["keywords_extracted"]
    
    # 1. Remaining EMIs Inquiry
    if keywords["asked_remaining_emi"]:
        if lang == "Hindi":
            response = f"अमित जी, आपके लोन खाता {loan_id} पर वर्तमान में लगभग {remaining_emis} EMI बकाया हैं। आपकी अंतिम EMI {end_date} को देय है।"
        else:
            response = f"Sure {name}, for your loan account {loan_id}, you have approximately {remaining_emis} EMIs remaining. The final scheduled payment date is {end_date}."
            
    # 2. Interest Paid Inquiry
    elif keywords["asked_interest_paid"]:
        if lang == "Hindi":
            response = f"प्रिया जी, आपने अब तक कुल ₹{principal_paid} मूलधन (Principal) और ₹{interest_paid} ब्याज (Interest) का भुगतान किया है। आपका शेष बकाया मूलधन ₹{outstanding_bal} है।"
        else:
            response = f"Yes {name}, based on your payment records, you have paid a total of INR {principal_paid} towards the principal amount and INR {interest_paid} in interest. Your remaining outstanding principal balance is INR {outstanding_bal}."
            
    # 4 & 5. Payment Failure Glitch / Penalty Waiver
    elif keywords["claimed_bank_glitch"] or keywords["asked_waiver"]:
        is_verified = diagnosis["knowns"]["actual_bank_glitch_verified"]
        
        if is_verified:
            if lang == "Hindi":
                response = f"संजय जी, मैंने आपके पेमेंट लॉग की जांच की है। आपका ऑटो-डेबिट भुगतान 'नेटवर्क टाइमआउट' के कारण विफल हुआ था, जबकि आपके बैंक खाते में पर्याप्त राशि थी। चूंकि यह तकनीकी खराबी थी, हम आपकी लेट फीस हटाने के लिए पात्र हैं। मैंने आपके पंजीकृत मोबाइल नंबर पर नई पेमेंट लिंक भेज दी है। क्या आप भुगतान करने में सक्षम हैं?"
            else:
                response = f"Thank you for confirming, {name}. I checked our payment gateway logs and verified a 'Bank Gateway Timeout' occurred on your transaction on the due date. Since this is a technical bank-side glitch, you are fully eligible for a waiver. I will waive the INR 500 penalty, generate a fresh payment link for INR {emi}, and submit a ticket. Would you like me to send the payment link now?"
                
            actions = [
                {"type": "waive_penalty"},
                {"type": "generate_payment_link", "amount": emi}
            ]
        else:
            # Not verified or insufficient logs
            if lang == "Hindi":
                response = f"सुनीता जी, हमारे पास बैंक खराबी का कोई रिकॉर्ड नहीं दिख रहा है। हालांकि, मैं इस संबंध में एक सपोर्ट टिकट बना देता हूँ ताकि हमारी टीम इसकी समीक्षा कर सके। क्या आप लेट फीस हटाने के लिए अपने बैंक स्टेटमेंट की कॉपी साझा कर सकती हैं?"
            else:
                response = f"I understand your concern, {name}. However, our records show the auto-debit failed due to insufficient balance. I can create a dispute ticket to have our credit department review this if you can provide a bank statement showing sufficient funds on the due date. Shall I raise the support ticket?"
                
            actions = [
                {"type": "create_ticket", "title": "Late fee dispute - claimed bank glitch", "category": "EMI Dispute", "description": f"Borrower {name} claims auto-debit failed due to bank error. Requesting waiver review."}
            ]
            
    # 3. Penalty Charge Inquiry
    elif keywords["asked_penalty_reason"]:
        if lang == "Hindi":
            response = f"राहुल जी, आपके खाते पर ₹{penalty} का विलंब शुल्क चार्ज किया गया है। यह 1 तारीख को देय EMI के ऑटो-डेबिट बाउंस होने के कारण लगा है। हमारी पॉलिसी के अनुसार, नियत तिथि के 3 दिनों के बाद भुगतान न होने पर ₹500 का चार्ज लागू होता है।"
        else:
            response = f"I see {name}. A penalty charge of INR {penalty} was levied on your account because your auto-debit transaction due on the 1st of this month failed. According to company policy, any EMI unpaid 3 days after the due date incurs a standard late charge of INR 500."
            
    # 6. Commitment / PTP response (e.g. Next Friday, delay reason)
    elif keywords["provided_promise_date"] or keywords["claimed_salary_delay"]:
        promise_date = keywords["provided_promise_date"] or "Friday"
        # Map weekday names to actual calendar dates
        today = datetime.now()
        target_date = today + timedelta(days=5) # Default next week representation
        
        if "friday" in promise_date.lower():
            # Find next Friday
            days_ahead = 4 - today.weekday()
            if days_ahead <= 0: # Already past Friday
                days_ahead += 7
            target_date = today + timedelta(days=days_ahead)
            
        date_str = target_date.strftime("%Y-%m-%d")
        
        if lang == "Hindi":
            response = f"ठीक है करन जी, मैंने दर्ज कर लिया है कि आप {date_str} तक ₹{emi} का भुगतान करेंगे। कृपया इस तिथि तक भुगतान पूरा करना सुनिश्चित करें ताकि आपकी लेट फीस और न बढ़े।"
        else:
            response = f"Understood {name}. I have recorded your commitment to make the payment of INR {emi} by next Friday, {date_str}, due to a salary delay. Please complete it by then to prevent further delinquency flags. I will also schedule a follow-up call."
            
        actions = [
            {"type": "schedule_callback", "time": date_str}
        ]
        
        extracted_memory = {
            "promises": [{
                "amount": emi,
                "date": date_str,
                "reason": "Salary delayed",
                "status": "Pending",
                "created_at": today.strftime("%Y-%m-%d")
            }],
            "preferences": {
                "communication_style": "Cooperative but salary dependent",
                "preferred_language": lang
            }
        }
        
    # Standard general queries
    else:
        if lang == "Hindi":
            response = f"मैं आपकी कैसे सहायता कर सकता हूँ? क्या आप अपने EMI की स्थिति या लोन की अवधि जानना चाहते हैं?"
        else:
            response = f"I can assist you with your EMI status, loan balance, foreclosure inquiries, or late fee waivers. What would you like to check today?"
            
    return {
        "response_text": response,
        "actions": actions,
        "extracted_memory": extracted_memory,
        "sentiment": sentiment
    }

def run_gemini_agent(context: dict, diagnosis: dict, rag_docs: list, user_text: str) -> dict:
    """
    Orchestrates the LLM execution using Gemini's API.
    Injects context, diagnosis indicators, and RAG policies as grounding.
    """
    model = genai.GenerativeModel('gemini-2.5-flash', generation_config={"response_mime_type": "application/json"})
    
    # Build a comprehensive system prompt grounding the model
    system_prompt = f"""
    You are a professional, polite, and result-oriented Inbound Voice Agent for Credit Servicing.
    Your objective is to help the borrower resolve their loan issues while safeguarding the lender's interest and adhering strictly to company policies.
    
    CRITICAL POLICY RULES:
    1. Foreclosure: Allowed after 6 months. Charges are 0% for floating loans and 4% for fixed rate loans.
    2. Late Fee: Applied after a 3-day grace period. Late charge is INR 500. Penal interest is 2% per month (calculated daily).
    3. Penalty Waiver: Eligible ONLY if payment failure was verified as a technical glitch on lender/bank side (Network Timeout, Gateway Timeout, Server Down) OR if the borrower has a clean payment history. Otherwise, deny waiver and suggest raising a dispute ticket for review if they supply a bank statement.
    4. Promise-to-Pay (PTP): Commitments must specify an exact date (not exceeding 10 days) and amount.
    5. Conversational Style: Keep your answers CONCISE, clear, and audio-friendly. Do not speak in long paragraphs. Use bullet points or short sentences. Address the user by their name. Speak in the user's preferred language ({context.get('loan', {}).get('preferred_language')}).
    
    INPUT DATA:
    
    - Borrower Context: {json.dumps(context)}
    
    - Internal Diagnosis: {json.dumps(diagnosis)}
    
    - Retrieved Policy Documents (RAG Grounding):
    {json.dumps(rag_docs)}
    
    - User input: "{user_text}"
    
    You must output a JSON object with the following schema:
    {{
        "response_text": "A concise response to speak back to the borrower (in their preferred language)",
        "actions": [
            {{
                "type": "generate_payment_link",
                "amount": 1000.0
            }},
            {{
                "type": "create_ticket",
                "title": "Dispute details",
                "category": "Penalty Waiver Request",
                "description": "Detail description"
            }},
            {{
                "type": "schedule_callback",
                "time": "YYYY-MM-DD"
            }},
            {{
                "type": "waive_penalty"
            }}
        ],
        "extracted_memory": {{
            "promises": [
                {{
                    "amount": 7500.0,
                    "date": "2026-06-12",
                    "reason": "Salary delayed",
                    "status": "Pending",
                    "created_at": "2026-06-06"
                }}
            ],
            "preferences": {{
                "communication_style": "Reason for delay stated",
                "preferred_language": "English"
            }}
        }},
        "sentiment": "Neutral/Positive/Negative/Angry"
    }}
    """
    
    try:
        response = model.generate_content(system_prompt)
        res_text = response.text
        
        # Clean JSON wrappers if LLM returned them
        if "```json" in res_text:
            res_text = re.search(r"```json\s*(.*?)\s*```", res_text, re.DOTALL).group(1)
        elif "```" in res_text:
            res_text = re.search(r"```\s*(.*?)\s*```", res_text, re.DOTALL).group(1)
            
        data = json.loads(res_text.strip())
        return data
    except Exception as e:
        print(f"Gemini API invocation error: {str(e)}. Falling back to high-fidelity mock agent.")
        return run_mock_agent(context, diagnosis, rag_docs, user_text)

def interact_call(borrower_id: str, user_text: str) -> dict:
    """
    Main call interaction pipeline:
    1. Retrieves unified context and memory.
    2. Runs Diagnosis Layer.
    3. Runs RAG Search over Knowledge Base.
    4. Routes to Gemini / Mock Agent to generate response and tool suggestions.
    5. Executes tool actions (ticketing, webhook dispatch).
    6. Updates short and long-term Memory tables.
    7. Appends dialogue turns.
    """
    session = get_session(borrower_id)
    session_turns = session["turns"]
    
    # Append user turn
    user_turn = {"sender": "borrower", "text": user_text}
    session_turns.append(user_turn)
    
    # 1 & 2. Get Context & Diagnosis
    ctx = context_engine.get_unified_borrower_context(borrower_id)
    diagnosis = diagnosis_layer.diagnose_session(ctx, session_turns)
    
    # 3. RAG Retrieval
    rag_docs = rag_engine.retrieve_policy_documents(user_text, top_k=2)
    
    # 4. Generate response via LLM or Mock
    if HAS_GEMINI_SDK and GEMINI_API_KEY:
        agent_output = run_gemini_agent(ctx, diagnosis, rag_docs, user_text)
    else:
        agent_output = run_mock_agent(ctx, diagnosis, rag_docs, user_text)
        
    response_text = agent_output.get("response_text", "")
    actions_to_take = agent_output.get("actions", [])
    extracted_mem = agent_output.get("extracted_memory", {})
    sentiment = agent_output.get("sentiment", "Neutral")
    
    # 5. Execute tool actions
    executed_tools_log = execute_agent_tools(borrower_id, actions_to_take)
    
    # 6. Update Memory Engine
    if extracted_mem:
        promises = extracted_mem.get("promises", [])
        if promises:
            for p in promises:
                memory_engine.record_ptp_promise(borrower_id, p["date"], p["amount"], p.get("reason", "Salary delayed"))
        
        prefs = extracted_mem.get("preferences", {})
        if prefs:
            memory_engine.update_preferences_and_paths(borrower_id, new_preferences=prefs)
            
    # Record success path logs if relevant
    for t in executed_tools_log:
        if t["action"] == "waive_penalty":
            memory_engine.update_preferences_and_paths(borrower_id, new_success_path="Waived penalty charge on verified bank timeout glitch")
        elif t["action"] == "generate_payment_link":
            memory_engine.update_preferences_and_paths(borrower_id, new_success_path="Generated Stripe payment checkout link for EMI collection")
            
    # Append agent turn
    agent_turn = {"sender": "agent", "text": response_text}
    session_turns.append(agent_turn)
    
    # Finalize session if hang-up (represented by empty text or finished intent, but we do it continuously for the demo state)
    # We will compute outcome and summary dynamically based on current turn
    summary = f"Interaction regarding loan support. Borrower sentiment: {sentiment}."
    outcome = "Addressed borrower inquiry."
    if executed_tools_log:
        outcome = f"Executed actions: " + ", ".join([f["action"] for f in executed_tools_log])
        
    memory_engine.finalize_call_session(borrower_id, session_turns, summary, sentiment, outcome)
    
    # Return everything needed by the frontend console to display internal reasoning
    return {
        "response_text": response_text,
        "sentiment": sentiment,
        "context": context_engine.get_unified_borrower_context(borrower_id), # Refresh context with new updates
        "diagnosis": diagnosis,
        "rag_citations": rag_docs,
        "actions_triggered": executed_tools_log,
        "session_transcript": session_turns
    }

def uuid_short():
    import uuid
    return uuid.uuid4().hex[:6]
