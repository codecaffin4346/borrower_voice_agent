import sys
import os
import json

# Ensure backend directory is in python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import database
import context_engine
import diagnosis_layer
import memory_engine
import rag_engine
import orchestrator

# Reconfigure stdout to support UTF-8 printing on Windows
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")


def run_tests():
    print("==================================================")
    print("RUNNING AGENTIC PIPELINE INTEGRATION TESTS")
    print("==================================================")
    
    # Ensure database is freshly seeded
    import generate_data
    generate_data.generate_dataset()
    
    # Test Scenario 1: Remaining EMI Inquiry
    print("\n--- Test Scenario 1: Remaining EMI Inquiry ---")
    b_id = "BORR_S1_EMI"
    orchestrator.reset_session(b_id)
    start_res = orchestrator.get_session(b_id)
    print(f"Agent Greeting: {start_res['turns'][0]['text']}")
    
    interact_res = orchestrator.interact_call(b_id, "How many EMIs are remaining on my loan?")
    print(f"User Asked: How many EMIs are remaining on my loan?")
    print(f"Agent Response: {interact_res['response_text']}")
    assert "EMI" in interact_res['response_text'] or "payments" in interact_res['response_text'].lower()
    print("Scenario 1 Passed.")
    
    # Test Scenario 2: Interest Paid Inquiry
    print("\n--- Test Scenario 2: Interest Paid Inquiry ---")
    b_id = "BORR_S2_INT"
    orchestrator.reset_session(b_id)
    orchestrator.get_session(b_id)
    
    interact_res = orchestrator.interact_call(b_id, "How much interest have I paid so far?")
    print(f"User Asked: How much interest have I paid so far?")
    print(f"Agent Response: {interact_res['response_text']}")
    assert "interest" in interact_res['response_text'].lower()
    print("Scenario 2 Passed.")
    
    # Test Scenario 3: Penalty Charge Inquiry
    print("\n--- Test Scenario 3: Penalty Charge Inquiry ---")
    b_id = "BORR_S3_PEN"
    orchestrator.reset_session(b_id)
    orchestrator.get_session(b_id)
    
    interact_res = orchestrator.interact_call(b_id, "Why was a penalty charged on my account?")
    print(f"User Asked: Why was a penalty charged on my account?")
    print(f"Agent Response: {interact_res['response_text']}")
    assert "penalty" in interact_res['response_text'].lower() or "charge" in interact_res['response_text'].lower() or "fee" in interact_res['response_text'].lower()
    print("Scenario 3 Passed.")
    
    # Test Scenario 4: Payment Failure Due to Bank Glitch
    print("\n--- Test Scenario 4: Payment Failure Due to Bank Glitch ---")
    b_id = "BORR_S4_GLI"
    orchestrator.reset_session(b_id)
    orchestrator.get_session(b_id)
    
    interact_res = orchestrator.interact_call(b_id, "My payment failed even though I had enough balance.")
    print(f"User Asked: My payment failed even though I had enough balance.")
    print(f"Agent Response: {interact_res['response_text']}")
    print(f"Actions Triggered: {interact_res['actions_triggered']}")
    print("Scenario 4 Passed.")
    
    # Test Scenario 5: Penalty Waiver Request
    print("\n--- Test Scenario 5: Penalty Waiver Request ---")
    b_id = "BORR_S5_WAI"
    orchestrator.reset_session(b_id)
    orchestrator.get_session(b_id)
    
    interact_res = orchestrator.interact_call(b_id, "Can my penalty be waived because the payment failure was caused by the bank?")
    print(f"User Asked: Can my penalty be waived because the payment failure was caused by the bank?")
    print(f"Agent Response: {interact_res['response_text']}")
    print(f"Actions Triggered: {interact_res['actions_triggered']}")
    # Assert waiver was executed in actions
    actions = [a["action"] for a in interact_res['actions_triggered']]
    assert "waive_penalty" in actions
    print("Scenario 5 Passed.")
    
    # Test Scenario 6: Follow-Up Call With Memory
    print("\n--- Test Scenario 6: Follow-Up Call With Memory ---")
    b_id = "BORR_S6_MEM"
    
    # Verify that initial session start retrieves memory and greets accordingly
    orchestrator.reset_session(b_id)
    start_res = orchestrator.get_session(b_id)
    greeting = start_res['turns'][0]['text']
    print(f"Agent Memory-Aware Greeting: {greeting}")
    assert "Friday" in greeting or "salary" in greeting or "पिछली बातचीत" in greeting
    
    interact_res = orchestrator.interact_call(b_id, "Yes, I got my salary and I'm ready to pay now.")
    print(f"User Answered: Yes, I got my salary and I'm ready to pay now.")
    print(f"Agent Response: {interact_res['response_text']}")
    
    print("Scenario 6 Passed.")
    
    # Test RAG retrieval directly
    print("\n--- Testing RAG Retrieval ---")
    hits = rag_engine.retrieve_policy_documents("foreclosure fee", top_k=2)
    print(f"RAG query: 'foreclosure fee'")
    for h in hits:
        print(f"  - [{h['doc_id']}] {h['title']} (Score: {h['score']})")
    assert len(hits) > 0
    print("RAG test Passed.")
    
    print("\n==================================================")
    print("ALL CORE BACKEND SYSTEM INTEGRATION TESTS PASSED!")
    print("==================================================")

if __name__ == "__main__":
    run_tests()
