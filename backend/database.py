import sqlite3
import os
import json

DB_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "database.db")

def get_connection():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_connection()
    cursor = conn.cursor()
    
    # 1. Borrowers table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS borrowers (
            borrower_id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            phone TEXT NOT NULL,
            loan_id TEXT NOT NULL,
            loan_amount REAL NOT NULL,
            interest_rate REAL NOT NULL,
            emi_amount REAL NOT NULL,
            loan_start_date TEXT NOT NULL,
            loan_end_date TEXT NOT NULL,
            delinquency_status TEXT NOT NULL,
            kyc_status TEXT NOT NULL,
            risk_score INTEGER NOT NULL,
            preferred_language TEXT NOT NULL
        )
    """)
    
    # 2. Payment History table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS payment_history (
            payment_id TEXT PRIMARY KEY,
            borrower_id TEXT NOT NULL,
            loan_id TEXT NOT NULL,
            amount REAL NOT NULL,
            payment_date TEXT NOT NULL,
            status TEXT NOT NULL,
            failure_reason TEXT,
            payment_method TEXT NOT NULL,
            FOREIGN KEY (borrower_id) REFERENCES borrowers(borrower_id)
        )
    """)
    
    # 3. Tickets table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tickets (
            ticket_id TEXT PRIMARY KEY,
            borrower_id TEXT NOT NULL,
            title TEXT NOT NULL,
            description TEXT NOT NULL,
            category TEXT NOT NULL,
            status TEXT NOT NULL,
            created_at TEXT NOT NULL,
            resolution_notes TEXT,
            FOREIGN KEY (borrower_id) REFERENCES borrowers(borrower_id)
        )
    """)
    
    # 4. Knowledge Base table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS kb_documents (
            doc_id TEXT PRIMARY KEY,
            title TEXT NOT NULL,
            category TEXT NOT NULL,
            content TEXT NOT NULL
        )
    """)
    
    # 5. Conversation History table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS conversation_history (
            conversation_id TEXT PRIMARY KEY,
            borrower_id TEXT NOT NULL,
            timestamp TEXT NOT NULL,
            transcript TEXT NOT NULL, -- JSON list
            summary TEXT NOT NULL,
            sentiment TEXT NOT NULL,
            outcome TEXT NOT NULL,
            FOREIGN KEY (borrower_id) REFERENCES borrowers(borrower_id)
        )
    """)
    
    # 6. Memory table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS memory (
            borrower_id TEXT PRIMARY KEY,
            promises TEXT, -- JSON string
            preferences TEXT, -- JSON string
            outstanding_issues TEXT, -- JSON string
            agent_success_paths TEXT, -- JSON string
            last_interaction TEXT,
            FOREIGN KEY (borrower_id) REFERENCES borrowers(borrower_id)
        )
    """)
    
    # 7. Workflow Automation logs
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS workflow_logs (
            log_id TEXT PRIMARY KEY,
            timestamp TEXT NOT NULL,
            action_type TEXT NOT NULL,
            payload TEXT NOT NULL,
            webhook_url TEXT,
            status TEXT NOT NULL,
            response TEXT
        )
    """)
    
    conn.commit()
    conn.close()

# API functions to connect and read/write
def get_borrower(borrower_id):
    conn = get_connection()
    row = conn.execute("SELECT * FROM borrowers WHERE borrower_id = ?", (borrower_id,)).fetchone()
    conn.close()
    return dict(row) if row else None

def get_borrower_by_phone(phone):
    conn = get_connection()
    row = conn.execute("SELECT * FROM borrowers WHERE phone = ?", (phone,)).fetchone()
    conn.close()
    return dict(row) if row else None

def get_all_borrowers():
    conn = get_connection()
    rows = conn.execute("SELECT * FROM borrowers").fetchall()
    conn.close()
    return [dict(r) for r in rows]

def get_payment_history(borrower_id):
    conn = get_connection()
    rows = conn.execute(
        "SELECT * FROM payment_history WHERE borrower_id = ? ORDER BY payment_date DESC", 
        (borrower_id,)
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]

def get_tickets(borrower_id):
    conn = get_connection()
    rows = conn.execute(
        "SELECT * FROM tickets WHERE borrower_id = ? ORDER BY created_at DESC", 
        (borrower_id,)
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]

def create_ticket(ticket_id, borrower_id, title, description, category, status, created_at):
    conn = get_connection()
    conn.execute(
        "INSERT INTO tickets (ticket_id, borrower_id, title, description, category, status, created_at) VALUES (?, ?, ?, ?, ?, ?, ?)",
        (ticket_id, borrower_id, title, description, category, status, created_at)
    )
    conn.commit()
    conn.close()

def get_kb_documents():
    conn = get_connection()
    rows = conn.execute("SELECT * FROM kb_documents").fetchall()
    conn.close()
    return [dict(r) for r in rows]

def get_conversations(borrower_id):
    conn = get_connection()
    rows = conn.execute(
        "SELECT * FROM conversation_history WHERE borrower_id = ? ORDER BY timestamp DESC", 
        (borrower_id,)
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]

def add_conversation(conversation_id, borrower_id, timestamp, transcript_json, summary, sentiment, outcome):
    conn = get_connection()
    conn.execute(
        "INSERT INTO conversation_history (conversation_id, borrower_id, timestamp, transcript, summary, sentiment, outcome) VALUES (?, ?, ?, ?, ?, ?, ?)",
        (conversation_id, borrower_id, timestamp, transcript_json, summary, sentiment, outcome)
    )
    conn.commit()
    conn.close()

def get_memory(borrower_id):
    conn = get_connection()
    row = conn.execute("SELECT * FROM memory WHERE borrower_id = ?", (borrower_id,)).fetchone()
    conn.close()
    if row:
        res = dict(row)
        res['promises'] = json.loads(res['promises']) if res['promises'] else []
        res['preferences'] = json.loads(res['preferences']) if res['preferences'] else {}
        res['outstanding_issues'] = json.loads(res['outstanding_issues']) if res['outstanding_issues'] else []
        res['agent_success_paths'] = json.loads(res['agent_success_paths']) if res['agent_success_paths'] else []
        return res
    return {
        "borrower_id": borrower_id,
        "promises": [],
        "preferences": {},
        "outstanding_issues": [],
        "agent_success_paths": [],
        "last_interaction": None
    }

def update_memory(borrower_id, promises, preferences, outstanding_issues, agent_success_paths, last_interaction):
    conn = get_connection()
    conn.execute(
        """
        INSERT INTO memory (borrower_id, promises, preferences, outstanding_issues, agent_success_paths, last_interaction)
        VALUES (?, ?, ?, ?, ?, ?)
        ON CONFLICT(borrower_id) DO UPDATE SET
            promises = excluded.promises,
            preferences = excluded.preferences,
            outstanding_issues = excluded.outstanding_issues,
            agent_success_paths = excluded.agent_success_paths,
            last_interaction = excluded.last_interaction
        """,
        (
            borrower_id,
            json.dumps(promises),
            json.dumps(preferences),
            json.dumps(outstanding_issues),
            json.dumps(agent_success_paths),
            last_interaction
        )
    )
    conn.commit()
    conn.close()

def add_workflow_log(log_id, timestamp, action_type, payload_json, webhook_url, status, response):
    conn = get_connection()
    conn.execute(
        "INSERT INTO workflow_logs (log_id, timestamp, action_type, payload, webhook_url, status, response) VALUES (?, ?, ?, ?, ?, ?, ?)",
        (log_id, timestamp, action_type, payload_json, webhook_url, status, response)
    )
    conn.commit()
    conn.close()

def get_workflow_logs():
    conn = get_connection()
    rows = conn.execute("SELECT * FROM workflow_logs ORDER BY timestamp DESC LIMIT 50").fetchall()
    conn.close()
    return [dict(r) for r in rows]

def execute_custom_query(query, params=()):
    conn = get_connection()
    rows = conn.execute(query, params).fetchall()
    conn.close()
    return [dict(r) for r in rows]
