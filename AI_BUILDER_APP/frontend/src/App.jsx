import React, { useState, useEffect, useRef } from "react";
import {
    Play,
    CheckCircle,
    AlertTriangle,
    Clock,
    Award,
    Terminal,
    Layers,
    RotateCcw,
    History,
    Trash2,
    FileCode
} from "lucide-react";
import "./styles.css";

function App() {
    const [repoUrl, setRepoUrl] = useState("");
    const [loading, setLoading] = useState(false);
    const [logs, setLogs] = useState([]);
    const [results, setResults] = useState(null);
    const [score, setScore] = useState(0);
    const [isConnected, setIsConnected] = useState(false);
    const [history, setHistory] = useState([]);

    const wsRef = useRef(null);
    const terminalEndRef = useRef(null);

    const evaluatedRepoRef = useRef("");

    useEffect(() => {
        if (terminalEndRef.current) {
            terminalEndRef.current.scrollIntoView({ behavior: "smooth" });
        }
    }, [logs]);

    useEffect(() => {
        connectWebSocket();
        loadHistory();
        return () => {
            if (wsRef.current) wsRef.current.close();
        };
    }, []);

    const connectWebSocket = () => {
        console.log("🔌 Attempting connection to backend gateway...");
        const ws = new WebSocket("ws://localhost:8000/ws");
        wsRef.current = ws;

        ws.onopen = () => {
            console.log("✅ Stream pipe established successfully.");
            setIsConnected(true);
        };

        ws.onmessage = (event) => {
            try {
                const response = JSON.parse(event.data);
                if (response.type === "log") {
                    setLogs((prev) => [...prev, response.msg]);
                } else if (response.type === "result") {
                    const incomingResults = response.data.results || [];
                    const incomingScore = response.data.score || 0;

                    setResults(incomingResults);
                    setScore(incomingScore);
                    setLoading(false);

                    // Save both the score AND the detailed results array to history
                    fetchHistoryUpdate(incomingScore, evaluatedRepoRef.current, incomingResults);
                }
            } catch (err) {
                console.error("❌ Failed parsing transmission package:", err);
            }
        };

        ws.onerror = (error) => {
            console.error("💥 WebSocket communication fault:", error);
        };

        ws.onclose = () => {
            console.log("❌ Socket connection closed.");
            setIsConnected(false);
        };
    };

    const loadHistory = () => {
        try {
            const saved = localStorage.getItem("grader_history");
            if (saved) setHistory(JSON.parse(saved));
        } catch (e) {
            console.error("Failed loading local memory items", e);
        }
    };

    const fetchHistoryUpdate = (finalScore, activeUrl, finalResults) => {
        if (!activeUrl) return;

        try {
            const cleanUrl = activeUrl.trim().replace(/\.git$/, "");
            const match = cleanUrl.match(/github\.com\/([^/]+\/[^/?#]+)/);
            const repoName = match ? match[1] : cleanUrl;

            const newItem = {
                id: Date.now(),
                repo: repoName,
                url: activeUrl.trim(),
                score: finalScore,
                results: finalResults, // Storing the full agent output inside history object
                time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
            };

            setHistory((prevHistory) => {
                const filtered = prevHistory.filter(item => item.url.toLowerCase() !== activeUrl.trim().toLowerCase());
                const updated = [newItem, ...filtered].slice(0, 15);
                localStorage.setItem("grader_history", JSON.stringify(updated));
                return updated;
            });
        } catch (e) {
            console.error("Error writing to LocalStorage state ledger:", e);
        }
    };

    const clearHistory = () => {
        setHistory([]);
        localStorage.removeItem("grader_history");
    };

    const handleEvaluate = () => {
        if (!repoUrl.trim()) return;

        evaluatedRepoRef.current = repoUrl.trim();
        setLogs([]);
        setResults(null);
        setScore(0);
        setLoading(true);

        const payload = {
            repo_url: repoUrl.trim(),
            requirement: ""
        };

        if (!wsRef.current || wsRef.current.readyState !== WebSocket.OPEN) {
            console.log("🔄 Socket channel closed. Restructuring live stream connection...");
            const newWs = new WebSocket("ws://localhost:8000/ws");
            wsRef.current = newWs;

            newWs.onmessage = (event) => {
                const response = JSON.parse(event.data);
                if (response.type === "log") {
                    setLogs((prev) => [...prev, response.msg]);
                } else if (response.type === "result") {
                    const incomingResults = response.data.results || [];
                    const incomingScore = response.data.score || 0;
                    setResults(incomingResults);
                    setScore(incomingScore);
                    setLoading(false);
                    fetchHistoryUpdate(incomingScore, evaluatedRepoRef.current, incomingResults);
                }
            };

            newWs.onopen = () => {
                setIsConnected(true);
                newWs.send(JSON.stringify(payload));
            };

            newWs.onclose = () => setIsConnected(false);
        } else {
            wsRef.current.send(JSON.stringify(payload));
        }
    };

    // Handles clicking a past history item from the sidebar
    const handleHistoryItemClick = (item) => {
        if (loading) return; // Prevent switching while actively running an evaluation

        setRepoUrl(item.url);
        setScore(item.score);
        setLogs([]); // Clear execution stream logs since this is a historical view

        // Instantly load historical evaluation metrics into view without hitting backend
        if (item.results) {
            setResults(item.results);
        } else {
            setResults(null);
        }
    };

    return (
        <div className="app-container">
            {/* LEFT SIDEBAR PANEL */}
            <aside className="sidebar">
                <div className="sidebar-header">
                    <History size={18} className="icon-blue" />
                    <div className="sidebar-title-wrapper">
                        <h2>Recent Audits</h2>
                        <span className="audit-counter-badge">
                            Total: {history.length}
                        </span>
                    </div>
                    {history.length > 0 && (
                        <button onClick={clearHistory} className="btn-clear" title="Clear History">
                            <Trash2 size={14} />
                        </button>
                    )}
                </div>

                <div className="history-list">
                    {history.length === 0 ? (
                        <p className="no-history">No recent evaluations</p>
                    ) : (
                        history.map((item) => (
                            <div
                                key={item.id}
                                className="history-item"
                                onClick={() => handleHistoryItemClick(item)}
                            >
                                <span className="history-name" title={item.url}>{item.repo}</span>
                                <div className="history-meta">
                                    <span className={`badge-score ${item.score >= 70 ? 'good' : 'bad'}`}>
                                        Score: {item.score}
                                    </span>
                                    <span className="history-time"><Clock size={10} /> {item.time}</span>
                                </div>
                            </div>
                        ))
                    )}
                </div>
            </aside>

            {/* MAIN DASHBOARD */}
            <main className="main-content">
                <header className="top-banner">
                    <div className="logo-section">
                        <Layers className="logo-icon" />
                        <h1>AI Auto-Grader For Recruiters</h1>
                    </div>

                    <div className="connection-status">
                        {isConnected ? (
                            <span className="status-badge online">Connected</span>
                        ) : (
                            <button onClick={connectWebSocket} className="status-badge offline-btn">
                                <RotateCcw size={12} /> Reconnect Server
                            </button>
                        )}
                    </div>
                </header>

                <section className="control-card">
                    <div className="input-group">
                        <label>GitHub Repository Target Link</label>
                        <input
                            type="text"
                            placeholder="https://github.com/username/repository-name"
                            value={repoUrl}
                            onChange={(e) => setRepoUrl(e.target.value)}
                            disabled={loading}
                        />
                    </div>

                    <button
                        className={`btn-primary ${loading ? "disabled" : ""}`}
                        onClick={handleEvaluate}
                        disabled={loading || !repoUrl.trim()}
                    >
                        {loading ? (
                            <>
                                <span className="spinner"></span> Agent Ecosystem Auditing...
                            </>
                        ) : (
                            <>
                                <Play size={16} fill="currentColor" /> Grade Candidate Repository
                            </>
                        )}
                    </button>
                </section>

                {/* TERMINAL STREAM OUTPUT */}
                {logs.length > 0 && (
                    <section className="terminal-card">
                        <div className="card-header">
                            <Terminal size={16} />
                            <h3>Live Agent Execution Stream Logs</h3>
                        </div>
                        <div className="terminal-screen">
                            {logs.map((log, index) => (
                                <div key={index} className="terminal-line">
                                    <span className="term-prefix">&gt;</span> {log}
                                </div>
                            ))}
                            <div ref={terminalEndRef} />
                        </div>
                    </section>
                )}

                {/* METRIC EVALUATION RESULTS */}
                {results && (
                    <section className="results-container">
                        <div className="score-summary-card">
                            <div className="score-ring">
                                <Award className="award-icon" />
                                <div className="score-numbers">
                                    <span className="big-score">{score}</span>
                                    <span className="score-max">/100</span>
                                </div>
                            </div>
                            <div className="score-text">
                                <h2>Evaluation Matrix Complete</h2>
                                <p>Multi-agent micro-audits finished verification checks.</p>
                            </div>
                        </div>

                        <h3 className="section-title"><FileCode size={18} /> Detailed Agent Verification Ledger</h3>
                        <div className="agent-grid">
                            {results.map((res, idx) => (
                                <div key={idx} className={`agent-card border-${res.status || 'success'}`}>
                                    <div className="agent-card-header">
                                        <h4>{res.agent}</h4>
                                        <span className={`status-pill pill-${res.status || 'success'}`}>
                                            {res.status === "error" ? <AlertTriangle size={12} /> : <CheckCircle size={12} />}
                                            {(res.status || "success").toUpperCase()}
                                        </span>
                                    </div>
                                    <p className="agent-output-text">{res.output}</p>
                                </div>
                            ))}
                        </div>
                    </section>
                )}
            </main>
        </div>
    );
}

export default App;