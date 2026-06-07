import React, { useState, useEffect, useRef } from 'react';
import './App.css';

const API_BASE = 'http://127.0.0.1:8000';

// Simple SVG Icons
const Icons = {
  Phone: () => (
    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M22 16.92v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07 19.5 19.5 0 0 1-6-6 19.79 19.79 0 0 1-3.07-8.67A2 2 0 0 1 4.11 2h3a2 2 0 0 1 2 1.72 12.84 12.84 0 0 0 .7 2.81 2 2 0 0 1-.45 2.11L8.09 9.91a16 16 0 0 0 6 6l1.27-1.27a2 2 0 0 1 2.11-.45 12.84 12.84 0 0 0 2.81.7A2 2 0 0 1 22 16.92z"></path></svg>
  ),
  PhoneOff: () => (
    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M10.68 13.31a16 16 0 0 0 3.41 2.6l1.27-1.27a2 2 0 0 1 2.11-.45 12.84 12.84 0 0 0 2.81.7A2 2 0 0 1 22 16.92v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07 19.42 19.42 0 0 1-3.33-2.67m-2.67-3.34a19.79 19.79 0 0 1-3.07-8.63A2 2 0 0 1 4.11 2h3a2 2 0 0 1 2 1.72 12.84 12.84 0 0 0 .7 2.81 2 2 0 0 1-.45 2.11L8.09 9.91m-4.2-4.2L2 22"></path></svg>
  ),
  Mic: () => (
    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M12 2a3 3 0 0 0-3 3v7a3 3 0 0 0 6 0V5a3 3 0 0 0-3-3z"></path><path d="M19 10v2a7 7 0 0 1-14 0v-2"></path><line x1="12" y1="19" x2="12" y2="22"></line></svg>
  ),
  MicOff: () => (
    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><line x1="1" y1="1" x2="23" y2="23"></line><path d="M9 9v3a3 3 0 0 0 5.12 2.12M15 9.34V5a3 3 0 0 0-5.94-.6"></path><path d="M17 11.5a6 6 0 0 1-4.7 5.9"></path><path d="M5 10v2a7 7 0 0 0 7 7"></path><line x1="12" y1="19" x2="12" y2="22"></line></svg>
  ),
  Send: () => (
    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><line x1="22" y1="2" x2="11" y2="13"></line><polygon points="22 2 15 22 11 13 2 9 22 2"></polygon></svg>
  ),
  Database: () => (
    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><ellipse cx="12" cy="5" rx="9" ry="3"></ellipse><path d="M3 5v14c0 1.66 4 3 9 3s9-1.34 9-3V5"></path><path d="M3 12c0 1.66 4 3 9 3s9-1.34 9-3"></path></svg>
  ),
  ShieldAlert: () => (
    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"></path><line x1="12" y1="8" x2="12" y2="12"></line><line x1="12" y1="16" x2="12.01" y2="16"></line></svg>
  ),
  Sparkles: () => (
    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M12 3v1m0 16v1m9-9h-1M4 12H3m15.364-6.364l-.707.707M6.343 17.657l-.707.707m0-12.728l.707.707m11.32 11.32l.707-.707M12 8a4 4 0 1 0 0 8 4 4 0 0 0 0-8z"></path></svg>
  ),
  Settings: () => (
    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><circle cx="12" cy="12" r="3"></circle><path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 1 1-2.83 2.83l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-4 0v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 1 1-2.83-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1 0-4h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 1 1 2.83-2.83l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 4 0v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 1 1 2.83 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 0 4h-.09a1.65 1.65 0 0 0-1.51 1z"></path></svg>
  ),
  Refresh: () => (
    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M23 4v6h-6M1 20v-6h6"></path><path d="M3.51 9a9 9 0 0 1 14.85-3.36L23 10M1 14l4.64 4.36A9 9 0 0 0 20.49 15"></path></svg>
  )
};

function App() {
  const [borrowers, setBorrowers] = useState([]);
  const [selectedBorrowerId, setSelectedBorrowerId] = useState('');
  const [activeCall, setActiveCall] = useState(false);
  const [isVoiceEnabled, setIsVoiceEnabled] = useState(true);
  const [isRecording, setIsRecording] = useState(false);
  
  // Call turns and internal reasoning states
  const [turns, setTurns] = useState([]);
  const [inputText, setInputText] = useState('');
  const [context, setContext] = useState(null);
  const [diagnosis, setDiagnosis] = useState(null);
  const [ragCitations, setRagCitations] = useState([]);
  const [actionsTriggered, setActionsTriggered] = useState([]);
  const [activeTab, setActiveTab] = useState('context'); // 'context', 'diagnosis', 'rag', 'memory'
  
  // Sidebar data
  const [workflowLogs, setWorkflowLogs] = useState([]);
  const [analytics, setAnalytics] = useState(null);
  const [toastMessage, setToastMessage] = useState('');
  const [jsonView, setJsonView] = useState(false);
  
  // Speech objects
  const recognitionRef = useRef(null);
  const transcriptEndRef = useRef(null);

  // 6 Demo Scenarios Presets
  const DEMO_PRESETS = [
    {
      id: "BORR_S1_EMI",
      title: "Scenario 1: Remaining EMIs",
      text: "How many EMIs are remaining on my loan?",
      desc: "Queries remaining loan tenure."
    },
    {
      id: "BORR_S2_INT",
      title: "Scenario 2: Interest Paid",
      text: "How much interest have I paid so far?",
      desc: "Calculates reducing interest paid."
    },
    {
      id: "BORR_S3_PEN",
      title: "Scenario 3: Late Penalty Inquiry",
      text: "Why was a penalty charged on my account?",
      desc: "Asks why a late charge was levied."
    },
    {
      id: "BORR_S4_GLI",
      title: "Scenario 4: Bank Timeout Glitch",
      text: "My payment failed even though I had enough balance.",
      desc: "Gateway verify timeout, waiver ready."
    },
    {
      id: "BORR_S5_WAI",
      title: "Scenario 5: Penalty Waiver",
      text: "Can my penalty be waived because the payment failure was caused by the bank?",
      desc: "Triggers automatic late fee waiver."
    },
    {
      id: "BORR_S6_MEM",
      title: "Scenario 6: Call 2 Memory",
      text: "Yes, I got my salary and I'm ready to pay now.",
      desc: "Greets remembering Friday delay."
    }
  ];

  // Fetch initial system data
  useEffect(() => {
    fetchBorrowers();
    fetchAnalytics();
    fetchWorkflowLogs();
    initSpeechRecognition();
    
    // Poll logs occasionally
    const interval = setInterval(() => {
      if (activeCall) {
        fetchWorkflowLogs();
      }
    }, 4000);
    return () => clearInterval(interval);
  }, [activeCall]);

  useEffect(() => {
    if (selectedBorrowerId) {
      fetchContext(selectedBorrowerId);
    }
  }, [selectedBorrowerId]);

  useEffect(() => {
    // Scroll chat window to bottom on new message
    if (transcriptEndRef.current) {
      transcriptEndRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  }, [turns]);

  const fetchBorrowers = async () => {
    try {
      const res = await fetch(`${API_BASE}/api/borrowers`);
      const data = await res.json();
      setBorrowers(data);
      if (data.length > 0) {
        setSelectedBorrowerId(data[0].borrower_id);
      }
    } catch (e) {
      console.error("Error fetching borrowers", e);
    }
  };

  const fetchContext = async (id) => {
    try {
      const res = await fetch(`${API_BASE}/api/borrowers/${id}/context`);
      const data = await res.json();
      setContext(data);
    } catch (e) {
      console.error("Error fetching context", e);
    }
  };

  const fetchAnalytics = async () => {
    try {
      const res = await fetch(`${API_BASE}/api/analytics`);
      const data = await res.json();
      setAnalytics(data);
    } catch (e) {
      console.error("Error fetching analytics", e);
    }
  };

  const fetchWorkflowLogs = async () => {
    try {
      const res = await fetch(`${API_BASE}/api/workflow/logs`);
      const data = await res.json();
      setWorkflowLogs(data);
    } catch (e) {
      console.error("Error fetching workflow logs", e);
    }
  };

  // Web Speech API: Initialize Speech Recognition
  const initSpeechRecognition = () => {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (SpeechRecognition) {
      const rec = new SpeechRecognition();
      rec.continuous = false;
      rec.interimResults = false;
      rec.lang = 'en-IN'; // Indian English, supports Hindi-ish pronunciations well
      
      rec.onstart = () => {
        setIsRecording(true);
      };
      
      rec.onresult = (event) => {
        const transcript = event.results[0][0].transcript;
        setInputText(transcript);
        // Automatically submit spoken transcript
        sendInteraction(transcript);
      };
      
      rec.onerror = (e) => {
        console.error("Speech recognition error", e);
        setIsRecording(false);
      };
      
      rec.onend = () => {
        setIsRecording(false);
      };
      
      recognitionRef.current = rec;
    } else {
      console.warn("Web Speech API not supported in this browser.");
    }
  };

  const toggleRecording = () => {
    if (!activeCall) return;
    
    if (isRecording) {
      recognitionRef.current?.stop();
    } else {
      window.speechSynthesis.cancel(); // Mute ongoing TTS
      recognitionRef.current?.start();
    }
  };

  // Sync Speech Recognition language dynamically when context updates
  useEffect(() => {
    if (recognitionRef.current && context) {
      const langCode = context.loan?.preferred_language === 'Hindi' ? 'hi-IN' : 'en-IN';
      recognitionRef.current.lang = langCode;
      console.log(`Speech Recognition language synced to: ${langCode}`);
    }
  }, [context]);

  // Web Speech API: Text-to-Speech (TTS)
  const speakText = (text, language = 'English') => {
    if (!isVoiceEnabled) return;
    
    window.speechSynthesis.cancel(); // Stop current speech
    
    const utterance = new SpeechSynthesisUtterance(text);
    utterance.rate = 1.0;
    
    // Attempt language matching
    if (language === 'Hindi') {
      utterance.lang = 'hi-IN';
    } else {
      utterance.lang = 'en-IN';
    }
    
    // Choose appropriate local voice
    const voices = window.speechSynthesis.getVoices();
    let matchedVoice = null;
    
    if (language === 'Hindi') {
      // Find explicitly Hindi voice (hi-IN, hi, or name containing Hindi)
      matchedVoice = voices.find(v => v.lang.startsWith('hi') || v.name.toLowerCase().includes('hindi'));
    } else {
      // Find Indian English first, then fallback to any English voice
      matchedVoice = voices.find(v => v.lang === 'en-IN') || voices.find(v => v.lang.startsWith('en'));
    }
    
    if (matchedVoice) {
      utterance.voice = matchedVoice;
    }
    
    window.speechSynthesis.speak(utterance);
  };

  // Start Call
  const handleDial = async () => {
    if (activeCall) return;
    
    try {
      const res = await fetch(`${API_BASE}/api/call/start`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ borrower_id: selectedBorrowerId })
      });
      const data = await res.json();
      
      setTurns(data.session_transcript);
      setContext(data.context);
      setActiveCall(true);
      
      // Reset details panel
      setDiagnosis(null);
      setRagCitations([]);
      setActionsTriggered([]);
      
      // Speak greeting
      speakText(data.response_text, data.context?.loan?.preferred_language);
    } catch (e) {
      console.error("Error starting call", e);
    }
  };

  // Hang Up
  const handleHangUp = async () => {
    if (!activeCall) return;
    
    try {
      await fetch(`${API_BASE}/api/call/reset`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ borrower_id: selectedBorrowerId })
      });
      
      setActiveCall(false);
      setIsRecording(false);
      recognitionRef.current?.stop();
      window.speechSynthesis.cancel();
      
      // Refresh backend states
      fetchAnalytics();
      fetchContext(selectedBorrowerId);
      showNotification("Call ended. Transactions saved to ledger.");
    } catch (e) {
      console.error("Error resetting call", e);
    }
  };

  // Send interaction transcript
  const sendInteraction = async (textToSend) => {
    const query = textToSend || inputText;
    if (!query.trim()) return;
    
    // Optimistic user turn addition
    setTurns(prev => [...prev, { sender: 'borrower', text: query }]);
    setInputText('');
    
    try {
      const res = await fetch(`${API_BASE}/api/call/interact`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ borrower_id: selectedBorrowerId, text: query })
      });
      const data = await res.json();
      
      setTurns(data.session_transcript);
      setContext(data.context);
      setDiagnosis(data.diagnosis);
      setRagCitations(data.rag_citations);
      
      if (data.actions_triggered && data.actions_triggered.length > 0) {
        setActionsTriggered(data.actions_triggered);
        // Highlight tool calls via notifications
        data.actions_triggered.forEach(act => {
          showNotification(`Tool Triggered: ${act.details}`);
        });
      }
      
      // Speak response
      speakText(data.response_text, data.context?.loan?.preferred_language);
    } catch (e) {
      console.error("Error in interaction", e);
    }
  };

  // Reset entire database to default
  const handleSystemReset = async () => {
    if (window.confirm("Are you sure you want to restore the SQLite database to its default seeded state?")) {
      try {
        const res = await fetch(`${API_BASE}/api/reset-db`, { method: 'POST' });
        const data = await res.json();
        
        setActiveCall(false);
        setTurns([]);
        setContext(null);
        setDiagnosis(null);
        setRagCitations([]);
        setActionsTriggered([]);
        
        await fetchBorrowers();
        await fetchAnalytics();
        await fetchWorkflowLogs();
        
        showNotification("Database re-seeded successfully!");
      } catch (e) {
        console.error("System reset failed", e);
      }
    }
  };

  // Presets trigger helper
  const runPresetScenario = async (preset) => {
    // Set borrower
    setSelectedBorrowerId(preset.id);
    await fetchContext(preset.id);
    
    // Auto-dial
    setTimeout(async () => {
      // Direct post start call
      try {
        const res = await fetch(`${API_BASE}/api/call/start`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ borrower_id: preset.id })
        });
        const data = await res.json();
        
        setTurns(data.session_transcript);
        setContext(data.context);
        setActiveCall(true);
        setDiagnosis(null);
        setRagCitations([]);
        setActionsTriggered([]);
        
        speakText(data.response_text, data.context?.loan?.preferred_language);
        
        // Auto type/speak user query in 3 seconds
        setTimeout(() => {
          setInputText(preset.text);
        }, 1200);
      } catch (e) {
        console.error(e);
      }
    }, 400);
  };

  const showNotification = (msg) => {
    setToastMessage(msg);
    setTimeout(() => {
      setToastMessage('');
    }, 4000);
  };

  return (
    <div className="dashboard-container">
      {/* Header */}
      <header className="dashboard-header">
        <div className="header-title-container">
          <div className="logo-glow" />
          <h1>CredResolve Servicing AI — Inbound Voice Agent Console</h1>
        </div>
        <div className="header-actions">
          <button className="btn-reset" onClick={handleSystemReset}>
            <span style={{ marginRight: '6px' }}><Icons.Refresh /></span> Reset System Database
          </button>
        </div>
      </header>

      {/* Main Layout Grid */}
      <main className="dashboard-grid">
        
        {/* Left Column: Call Simulator & Presets */}
        <section className="dashboard-column" style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
          
          {/* Dialer Simulator Panel */}
          <div className="card-panel">
            <h2 className="panel-title"><Icons.Phone /> Voice Call Simulator</h2>
            
            <div className="borrower-selector-container">
              <label className="selector-label">1. Choose Borrower Profile</label>
              <select 
                className="custom-select" 
                value={selectedBorrowerId} 
                onChange={(e) => setSelectedBorrowerId(e.target.value)}
                disabled={activeCall}
              >
                {borrowers.map(b => (
                  <option key={b.borrower_id} value={b.borrower_id}>
                    {b.name} ({b.borrower_id === "BORR_S6_MEM" ? "Scenario 6 Memory" : b.delinquency_status})
                  </option>
                ))}
              </select>
            </div>

            {/* Simulated Phone Widget */}
            <div className={`phone-widget ${activeCall ? 'active-call-pulse' : ''}`}>
              <div className="phone-header">
                <span>4G LTE</span>
                <div className="signal-bars">
                  <div className="signal-bar" />
                  <div className="signal-bar" />
                  <div className="signal-bar" />
                  <div className="signal-bar" />
                </div>
              </div>
              
              <div className="phone-avatar-container">
                <div className={`phone-avatar ${activeCall ? 'active-call' : ''}`}>
                  <span style={{ fontSize: '2.5rem' }}>👤</span>
                </div>
                <div className="borrower-name-display">
                  {context?.name || 'No Borrower Loaded'}
                </div>
                <div className={`call-status-label ${activeCall ? 'active' : 'disconnected'}`}>
                  {activeCall ? 'Call Active' : 'Disconnected'}
                </div>
              </div>

              {/* Animated waveform visualizer */}
              <div className="waveform-container">
                <div className="wave-bar" />
                <div className="wave-bar" />
                <div className="wave-bar" />
                <div className="wave-bar" />
                <div className="wave-bar" />
                <div className="wave-bar" />
                <div className="wave-bar" />
                <div className="wave-bar" />
                <div className="wave-bar" />
                <div className="wave-bar" />
              </div>

              {/* Action Buttons */}
              <div style={{ display: 'flex', gap: '1.5rem' }}>
                {!activeCall ? (
                  <button className="btn-dial" onClick={handleDial}>
                    <Icons.Phone />
                  </button>
                ) : (
                  <button className="btn-hangup" onClick={handleHangUp}>
                    <Icons.PhoneOff />
                  </button>
                )}
              </div>
            </div>

            {/* Interaction controls */}
            <div className="call-controls-box">
              <div className="speech-toggle-container">
                <span>Enable Browser Audio (STT / TTS)</span>
                <label className="switch-control">
                  <input 
                    type="checkbox" 
                    checked={isVoiceEnabled} 
                    onChange={(e) => setIsVoiceEnabled(e.target.checked)}
                  />
                  <span className="switch-slider" />
                </label>
              </div>

              {/* Transcript list */}
              <div className="transcript-box">
                {turns.length === 0 && (
                  <div style={{ color: 'var(--text-muted)', fontSize: '0.8rem', textAlign: 'center', marginTop: '3rem' }}>
                    Dial a call to stream the interaction transcripts.
                  </div>
                )}
                {turns.map((t, idx) => (
                  <div key={idx} className={`transcript-message ${t.sender === 'agent' ? 'agent' : 'borrower'}`}>
                    <strong>{t.sender === 'agent' ? 'AI Agent' : 'Borrower'}:</strong> {t.text}
                  </div>
                ))}
                <div ref={transcriptEndRef} />
              </div>

              {/* Text Input Row */}
              <div className="input-row">
                <input 
                  type="text" 
                  className="voice-input-field" 
                  placeholder={isRecording ? "Listening..." : "Type custom response..."}
                  value={inputText}
                  onChange={(e) => setInputText(e.target.value)}
                  onKeyDown={(e) => e.key === 'Enter' && sendInteraction()}
                  disabled={!activeCall}
                />
                
                {isVoiceEnabled && (
                  <button 
                    className={`btn-mic-record ${isRecording ? 'recording' : ''}`} 
                    onClick={toggleRecording}
                    disabled={!activeCall}
                  >
                    {isRecording ? <Icons.Mic /> : <Icons.Mic />}
                  </button>
                )}
                
                <button className="btn-send-chat" onClick={() => sendInteraction()} disabled={!activeCall}>
                  <Icons.Send />
                </button>
              </div>
            </div>
          </div>

          {/* Preset Demo Scenarios */}
          <div className="card-panel">
            <h2 className="panel-title">⭐ Demo Scenario Presets</h2>
            <div className="scenarios-grid">
              {DEMO_PRESETS.map((preset, idx) => (
                <button key={idx} className="btn-scenario" onClick={() => runPresetScenario(preset)}>
                  <strong>{preset.title}</strong>
                  <div style={{ fontSize: '0.75rem', opacity: 0.7, marginTop: '2px' }}>{preset.desc}</div>
                </button>
              ))}
            </div>
          </div>

        </section>

        {/* Center Column: Internal Reasoning Console */}
        <section className="card-panel" style={{ flex: 1 }}>
          <h2 className="panel-title"><Icons.Sparkles /> Multi-Agent Reasoning Console</h2>
          
          <div className="reasoning-tabs">
            <button 
              className={`btn-tab ${activeTab === 'context' ? 'active' : ''}`} 
              onClick={() => setActiveTab('context')}
            >
              Context Engine
            </button>
            <button 
              className={`btn-tab ${activeTab === 'diagnosis' ? 'active' : ''}`} 
              onClick={() => setActiveTab('diagnosis')}
            >
              Diagnosis Layer
            </button>
            <button 
              className={`btn-tab ${activeTab === 'rag' ? 'active' : ''}`} 
              onClick={() => setActiveTab('rag')}
            >
              RAG Citations
            </button>
            <button 
              className={`btn-tab ${activeTab === 'memory' ? 'active' : ''}`} 
              onClick={() => setActiveTab('memory')}
            >
              Memory Evolution
            </button>
          </div>

          {/* Tab Content 1: Context Engine */}
          {activeTab === 'context' && context && (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem', flex: 1 }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <span className="selector-label">Aggregated Unified Profile</span>
                <button 
                  style={{ background: 'none', border: 'none', color: 'var(--color-primary)', fontSize: '0.8rem', cursor: 'pointer' }}
                  onClick={() => setJsonView(!jsonView)}
                >
                  {jsonView ? "Switch to Cards View" : "View Raw JSON Payload"}
                </button>
              </div>

              {jsonView ? (
                <pre className="json-view-container">{JSON.stringify(context, null, 2)}</pre>
              ) : (
                <div className="context-section-box">
                  <div className="context-mini-panel">
                    <span className="mini-panel-header">CRM Customer Record</span>
                    <div className="context-row">
                      <span className="context-label">Borrower ID</span>
                      <span className="context-value">{context.borrower_id}</span>
                    </div>
                    <div className="context-row">
                      <span className="context-label">Name</span>
                      <span className="context-value">{context.name}</span>
                    </div>
                    <div className="context-row">
                      <span className="context-label">Phone</span>
                      <span className="context-value">{context.phone}</span>
                    </div>
                    <div className="context-row">
                      <span className="context-label">KYC Status</span>
                      <span className="context-value">{context.loan?.kyc_status}</span>
                    </div>
                    <div className="context-row">
                      <span className="context-label">Preferred Lang</span>
                      <span className="context-value">{context.loan?.preferred_language}</span>
                    </div>
                  </div>

                  <div className="context-mini-panel">
                    <span className="mini-panel-header">Core Lending Details</span>
                    <div className="context-row">
                      <span className="context-label">Loan Account</span>
                      <span className="context-value">{context.loan?.loan_id}</span>
                    </div>
                    <div className="context-row">
                      <span className="context-label">Principal Amount</span>
                      <span className="context-value">INR {context.loan?.loan_amount}</span>
                    </div>
                    <div className="context-row">
                      <span className="context-label">Interest Rate</span>
                      <span className="context-value">{context.loan?.interest_rate}% p.a.</span>
                    </div>
                    <div className="context-row">
                      <span className="context-label">Monthly EMI</span>
                      <span className="context-value">INR {context.loan?.emi_amount}</span>
                    </div>
                    <div className="context-row">
                      <span className="context-label">Remaining EMIs</span>
                      <span className="context-value">{context.loan?.breakdown?.estimated_remaining_emis} months</span>
                    </div>
                  </div>

                  <div className="context-mini-panel">
                    <span className="mini-panel-header">Aggregated Financial Ledger</span>
                    <div className="context-row">
                      <span className="context-label">Total Principal Paid</span>
                      <span className="context-value">INR {context.loan?.breakdown?.total_principal_paid}</span>
                    </div>
                    <div className="context-row">
                      <span className="context-label">Total Interest Paid</span>
                      <span className="context-value">INR {context.loan?.breakdown?.total_interest_paid}</span>
                    </div>
                    <div className="context-row">
                      <span className="context-label">Outstanding Bal</span>
                      <span className="context-value" style={{ color: 'var(--color-neon-blue)' }}>
                        INR {context.loan?.breakdown?.outstanding_principal}
                      </span>
                    </div>
                  </div>

                  <div className="context-mini-panel">
                    <span className="mini-panel-header">Operational Flags</span>
                    <div className="context-row">
                      <span className="context-label">Delinquency Tier</span>
                      <span className={`context-value ${context.loan?.delinquency_status !== 'Current' ? 'status-delinquent' : 'status-current'}`}>
                        {context.loan?.delinquency_status}
                      </span>
                    </div>
                    <div className="context-row">
                      <span className="context-label">Late Penalties</span>
                      <span className="context-value" style={{ color: context.operational?.outstanding_penalty > 0 ? 'var(--color-danger)' : 'var(--text-primary)' }}>
                        INR {context.operational?.outstanding_penalty}
                      </span>
                    </div>
                    <div className="context-row">
                      <span className="context-label">Recent Failures</span>
                      <span className="context-value">{context.operational?.recent_payment_failures?.length || 0} attempts</span>
                    </div>
                  </div>
                </div>
              )}
            </div>
          )}

          {activeTab === 'context' && !context && (
            <div style={{ textAlign: 'center', padding: '6rem 0', color: 'var(--text-muted)' }}>
              Select a borrower profile and start the call to inspect the Context Engine payload.
            </div>
          )}

          {/* Tab Content 2: Diagnosis Layer */}
          {activeTab === 'diagnosis' && diagnosis && (
            <div className="diagnosis-block">
              <span className="selector-label">Intent Analysis & Gaps Checklist</span>
              
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1.5rem' }}>
                
                {/* Gaps Checklist */}
                <div>
                  <h3 style={{ fontSize: '0.9rem', marginBottom: '0.75rem', color: 'var(--text-primary)' }}>Information Gaps / Unknowns</h3>
                  <div className="gaps-list">
                    {diagnosis.gaps.length === 0 ? (
                      <div className="badge-item verified" style={{ color: 'var(--color-success)' }}>
                        <div className="badge-icon" /> All required profile information has been collected.
                      </div>
                    ) : (
                      diagnosis.gaps.map((gap, idx) => (
                        <div key={idx} className="badge-item gap">
                          <div className="badge-icon" /> Missing: {gap}
                        </div>
                      ))
                    )}
                  </div>
                </div>

                {/* Verified facts */}
                <div>
                  <h3 style={{ fontSize: '0.9rem', marginBottom: '0.75rem', color: 'var(--text-primary)' }}>Verified Facts</h3>
                  <div className="knowns-list">
                    <div className="badge-item verified">
                      <div className="badge-icon" /> Borrower ID: {selectedBorrowerId}
                    </div>
                    <div className="badge-item verified">
                      <div className="badge-icon" /> Account Risk Level: {diagnosis.knowns?.risk_level}
                    </div>
                    <div className="badge-item verified">
                      <div className="badge-icon" /> Delinquency status: {diagnosis.knowns?.loan_status}
                    </div>
                    {diagnosis.knowns?.actual_bank_glitch_verified && (
                      <div className="badge-item verified" style={{ borderColor: 'var(--color-neon-blue)' }}>
                        <div className="badge-icon" style={{ backgroundColor: 'var(--color-neon-blue)' }} /> 
                        Bank Glitch Confirmed: {diagnosis.knowns?.glitch_reason} on {diagnosis.knowns?.glitch_date}
                      </div>
                    )}
                  </div>
                </div>
              </div>

              {/* Prioritized Agenda */}
              <div style={{ marginTop: '1rem' }}>
                <h3 style={{ fontSize: '0.9rem', marginBottom: '0.75rem', color: 'var(--text-primary)' }}>Prioritized Next Agenda Questions</h3>
                {diagnosis.prioritized_questions.length === 0 ? (
                  <p style={{ fontSize: '0.85rem', color: 'var(--text-secondary)' }}>No outstanding gaps. Ready for settlement or checkout link.</p>
                ) : (
                  <ol style={{ paddingLeft: '1.25rem', fontSize: '0.85rem', color: 'var(--text-secondary)', display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
                    {diagnosis.prioritized_questions.map((pq, idx) => (
                      <li key={idx}>
                        <strong>Ask: {pq.gap}</strong>
                        <div style={{ color: 'var(--color-neon-blue)', marginTop: '2px', fontStyle: 'italic' }}>"{pq.question}"</div>
                      </li>
                    ))}
                  </ol>
                )}
              </div>

              {/* Eligibility Checkbox flags */}
              <div style={{ marginTop: '1rem' }}>
                <h3 style={{ fontSize: '0.9rem', marginBottom: '0.75rem', color: 'var(--text-primary)' }}>Policy-Based Eligibility Matrix</h3>
                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '0.5rem' }}>
                  <div className="badge-item" style={{ borderColor: diagnosis.eligibility?.eligible_for_penalty_waiver ? 'var(--color-success)' : 'var(--border-color)' }}>
                    <input type="checkbox" checked={diagnosis.eligibility?.eligible_for_penalty_waiver} readOnly />
                    <span style={{ fontSize: '0.8rem', color: diagnosis.eligibility?.eligible_for_penalty_waiver ? '#fff' : 'var(--text-muted)' }}>
                      Late Fee Waiver Eligible
                    </span>
                  </div>
                  <div className="badge-item" style={{ borderColor: diagnosis.eligibility?.eligible_for_instant_payment_link ? 'var(--color-success)' : 'var(--border-color)' }}>
                    <input type="checkbox" checked={diagnosis.eligibility?.eligible_for_instant_payment_link} readOnly />
                    <span style={{ fontSize: '0.8rem', color: diagnosis.eligibility?.eligible_for_instant_payment_link ? '#fff' : 'var(--text-muted)' }}>
                      Instant Payment Checkout Link
                    </span>
                  </div>
                  <div className="badge-item" style={{ borderColor: diagnosis.eligibility?.eligible_for_human_escalation ? 'var(--color-success)' : 'var(--border-color)' }}>
                    <input type="checkbox" checked={diagnosis.eligibility?.eligible_for_human_escalation} readOnly />
                    <span style={{ fontSize: '0.8rem', color: diagnosis.eligibility?.eligible_for_human_escalation ? '#fff' : 'var(--text-muted)' }}>
                      Human Supervisor Escalation
                    </span>
                  </div>
                  <div className="badge-item" style={{ borderColor: diagnosis.eligibility?.eligible_for_settlement ? 'var(--color-success)' : 'var(--border-color)' }}>
                    <input type="checkbox" checked={diagnosis.eligibility?.eligible_for_settlement} readOnly />
                    <span style={{ fontSize: '0.8rem', color: diagnosis.eligibility?.eligible_for_settlement ? '#fff' : 'var(--text-muted)' }}>
                      Eligible for One-Time Settlement (OTS)
                    </span>
                  </div>
                </div>
              </div>
            </div>
          )}

          {activeTab === 'diagnosis' && !diagnosis && (
            <div style={{ textAlign: 'center', padding: '6rem 0', color: 'var(--text-muted)' }}>
              Initiate call and submit a message to stream live Diagnosis checklist.
            </div>
          )}

          {/* Tab Content 3: RAG policy retrieval */}
          {activeTab === 'rag' && ragCitations.length > 0 && (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
              <span className="selector-label">Knowledge Base Matches (Grounded RAG)</span>
              {ragCitations.map((doc, idx) => (
                <div key={idx} className="rag-citation-card">
                  <div className="rag-card-header">
                    <span className="rag-card-title">{doc.title} ({doc.category})</span>
                    <span className="rag-card-score">Score: {doc.score}</span>
                  </div>
                  <div className="rag-card-content">
                    {doc.content}
                  </div>
                </div>
              ))}
            </div>
          )}

          {activeTab === 'rag' && ragCitations.length === 0 && (
            <div style={{ textAlign: 'center', padding: '6rem 0', color: 'var(--text-muted)' }}>
              Policies retrieved from RAG will be cited here in real-time.
            </div>
          )}

          {/* Tab Content 4: Memory & Learn */}
          {activeTab === 'memory' && context && (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
              
              {/* Borrower active memory parameters */}
              <div>
                <span className="selector-label">Extracted Borrower Memory</span>
                <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem', marginTop: '0.5rem' }}>
                  <div className="badge-item">
                    <strong>Payment Promises (PTP):</strong>
                    {context.memory?.promises?.length === 0 ? (
                      <span style={{ color: 'var(--text-muted)', marginLeft: '10px' }}>No active promises logged</span>
                    ) : (
                      context.memory.promises.map((p, i) => (
                        <span key={i} style={{ color: 'var(--color-neon-blue)', marginLeft: '10px' }}>
                          INR {p.amount} due on {p.date} ({p.status})
                        </span>
                      ))
                    )}
                  </div>
                  <div className="badge-item">
                    <strong>Borrower Communication Preference:</strong>
                    <span style={{ color: 'var(--text-primary)', marginLeft: '10px' }}>
                      Style: {context.memory?.preferences?.communication_style || 'Not Set'} | Lang: {context.memory?.preferences?.preferred_language || 'Not Set'}
                    </span>
                  </div>
                  <div className="badge-item">
                    <strong>Agent Successful Resolution Path:</strong>
                    <span style={{ color: 'var(--color-success)', marginLeft: '10px' }}>
                      {context.memory?.agent_success_paths?.join(', ') || 'Gathering resolution trails'}
                    </span>
                  </div>
                </div>
              </div>

              {/* Call 1 vs Call 2 memory comparison */}
              <div style={{ marginTop: '0.5rem' }}>
                <span className="selector-label">Scenario 6: Call 1 vs Call 2 Memory Evolution</span>
                <div className="memory-evolution-grid" style={{ marginTop: '0.5rem' }}>
                  <div className="memory-evolution-card">
                    <div className="mem-card-title">📞 First Interaction (Call 1)</div>
                    <div className="mem-card-desc">
                      Borrower states: <em>"My salary is delayed. I will make the payment next Friday."</em>
                      <br /><br />
                      <strong>Result:</strong> Agent logs PTP commitment to the Memory table and ends call.
                    </div>
                  </div>
                  
                  <div className="memory-evolution-card" style={{ borderColor: selectedBorrowerId === 'BORR_S6_MEM' ? 'var(--color-success)' : 'var(--border-color)' }}>
                    <div className="mem-card-title">📞 Second Interaction (Call 2)</div>
                    <div className="mem-card-desc">
                      <strong>AI Memory Recall:</strong> Greetings are automatically customized on Call Start.
                      <br /><br />
                      <em>"During our previous conversation, you mentioned that you expected your salary on Friday... Were you able to complete the payment?"</em>
                    </div>
                  </div>
                </div>
              </div>

            </div>
          )}

          {activeTab === 'memory' && !context && (
            <div style={{ textAlign: 'center', padding: '6rem 0', color: 'var(--text-muted)' }}>
              Dial a call to view memory metrics.
            </div>
          )}

        </section>

        {/* Right Column: CRM Tagging, Support Tickets & Action Logs */}
        <section className="dashboard-column" style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
          
          {/* CRM & Core Banking State */}
          <div className="card-panel">
            <h2 className="panel-title"><Icons.Database /> Aggregated CRM Profile</h2>
            <div className="crm-profile-box">
              <div className="crm-row">
                <span className="crm-label">Auto-Debit (NACH) Mandate</span>
                <span className="crm-value" style={{ color: context?.loan?.delinquency_status === 'Current' ? 'var(--color-success)' : 'var(--color-warning)' }}>
                  {context?.loan?.delinquency_status === 'Current' ? 'Active' : 'Suspended - Failure'}
                </span>
              </div>
              <div className="crm-row">
                <span className="crm-label">Payment Link Status</span>
                <span className="crm-value">
                  {actionsTriggered.some(a => a.action === 'generate_payment_link') ? 'Generated (Razorpay)' : 'Pending'}
                </span>
              </div>
              <div className="crm-row">
                <span className="crm-label">Borrower risk score</span>
                <span className="crm-value" style={{ color: context?.loan?.risk_score > 60 ? 'var(--color-danger)' : (context?.loan?.risk_score > 30 ? 'var(--color-warning)' : 'var(--color-success)') }}>
                  {context?.loan?.risk_score || 0} / 100
                </span>
              </div>
              <div className="crm-row">
                <span className="crm-label">KYC Verification</span>
                <span className="crm-value">{context?.loan?.kyc_status || 'Unverified'}</span>
              </div>
            </div>
            
            {/* System KPIs */}
            <div className="metrics-row">
              <div className="metric-mini-card">
                <span className="metric-card-label">Resolution Rate</span>
                <span className="metric-card-val" style={{ color: 'var(--color-success)' }}>
                  {analytics ? `${Math.round((analytics.tickets.resolved / (analytics.tickets.open + analytics.tickets.resolved || 1)) * 100)}%` : '85%'}
                </span>
              </div>
              <div className="metric-mini-card">
                <span className="metric-card-label">Avg Risk Score</span>
                <span className="metric-card-val">
                  {analytics ? analytics.average_risk_score : '34.5'}
                </span>
              </div>
            </div>
          </div>

          {/* Support Ticket Queue */}
          <div className="card-panel" style={{ flex: 1, minHeight: '160px' }}>
            <h2 className="panel-title"><Icons.ShieldAlert /> Customer Support Tickets</h2>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem', maxHeight: '180px', overflowY: 'auto', paddingRight: '0.25rem' }}>
              {context?.interaction_history?.tickets.length === 0 ? (
                <div style={{ color: 'var(--text-muted)', fontSize: '0.75rem', textAlign: 'center', marginTop: '1rem' }}>
                  No active support tickets logged.
                </div>
              ) : (
                context?.interaction_history?.tickets.map((t, idx) => (
                  <div key={idx} className="workflow-log-item">
                    <div className="wf-item-header">
                      <span>[{t.category}] {t.title}</span>
                      <span className={t.status === 'Resolved' ? 'wf-tag-success' : ''}>{t.status}</span>
                    </div>
                    <div style={{ color: 'var(--text-muted)', fontSize: '0.7rem' }}>
                      Created: {t.created_at}
                    </div>
                  </div>
                ))
              )}
            </div>
          </div>

          {/* Workflow logs (n8n/Zapier) */}
          <div className="card-panel" style={{ flex: 1, minHeight: '180px' }}>
            <h2 className="panel-title"><Icons.Settings /> n8n / Workflow Automation Logs</h2>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem', maxHeight: '180px', overflowY: 'auto', paddingRight: '0.25rem' }}>
              {workflowLogs.length === 0 ? (
                <div style={{ color: 'var(--text-muted)', fontSize: '0.75rem', textAlign: 'center', marginTop: '2.5rem' }}>
                  No webhooks triggered yet.
                </div>
              ) : (
                workflowLogs.map((log, idx) => (
                  <div key={idx} className="workflow-log-item">
                    <div className="wf-item-header">
                      <strong>Webhook Triggered: {log.action_type}</strong>
                      <span className="wf-tag-success">{log.status}</span>
                    </div>
                    <div style={{ color: 'var(--text-muted)', fontSize: '0.65rem' }}>
                      URL: {log.webhook_url} | {log.timestamp}
                    </div>
                    <div className="wf-item-body">
                      {log.payload}
                    </div>
                  </div>
                ))
              )}
            </div>
          </div>

        </section>

      </main>

      {/* Floating alert notifications */}
      {toastMessage && (
        <div className="toast-tool-alert">
          <span className="toast-alert-icon-sparkle">✨</span>
          <span className="toast-alert-text">{toastMessage}</span>
        </div>
      )}
    </div>
  );
}

export default App;
