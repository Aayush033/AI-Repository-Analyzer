import streamlit as st
import sys
import os
import asyncio
import datetime
import json
import os
import uuid


# This ensures zero changes are needed for your internal backend files.
current_dir = os.path.dirname(os.path.abspath(__file__))
backend_path = os.path.join(current_dir, "backend")
if backend_path not in sys.path:
    sys.path.append(backend_path)

from core.graph import run_workflow


HISTORY_FILE = ".analyzer_history.json"

def load_persistent_history():
    if os.path.exists(HISTORY_FILE):
        try:
            with open(HISTORY_FILE, "r") as f:
                data = json.load(f)
                for item in data:
                    if "id" not in item:
                        item["id"] = str(uuid.uuid4())
                return data
        except Exception:
            return []
    return []

def save_persistent_history(history_list):
    try:
        with open(HISTORY_FILE, "w") as f:
            json.dump(history_list, f, indent=4)
    except Exception as e:
        st.error(f"Failed to persist historical ledger records: {e}")

st.set_page_config(
    page_title="AI Repo Analyzer", 
    page_icon="🔬", 
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
    <style>
        footer { display: none !important; visibility: hidden !important; }
        #MainMenu { display: none !important; visibility: hidden !important; }
        .stDeployButton { display: none !important; }
        
        [data-testid="stHeader"] { 
            background-color: transparent !important; 
            box-shadow: none !important;
        }
        
        [data-testid="collapsedControl"] {
            top: 70px !important; 
            background-color: #ffffff !important; 
            border-radius: 50% !important; 
            box-shadow: 0 4px 6px rgba(0,0,0,0.1) !important; 
            z-index: 999999 !important; 
        }
        
        .block-container {
            padding-top: 1.5rem !important;
            padding-bottom: 1rem !important;
        }

        [data-testid="stSidebarHeader"] {
            padding-top: 0.5rem !important;
            padding-bottom: 0rem !important;
        }
        [data-testid="stSidebarUserContent"] {
            padding-top: 0rem !important;
        }
        
        [data-testid="stSidebar"] {
            background: radial-gradient(circle at top left, #1e293b 0%, #020617 100%) !important;
            border-right: 1px solid #1e293b !important;
        }
        
        [data-testid="stSidebar"] h3 {
            color: #ffffff !important;
            font-weight: 700 !important;
            letter-spacing: 0.5px;
            margin-top: 0px !important;
            margin-bottom: 15px !important;
        }
        [data-testid="stSidebar"] p, [data-testid="stSidebar"] div {
            color: #cbd5e1;
        }
        
        [data-testid="stSidebar"] .stButton > button {
            background-color: #1e293b !important;
            color: #f8fafc !important;
            border: 1px solid #334155 !important;
            border-radius: 8px !important;
            white-space: pre-line !important;
            text-align: left !important;
            transition: all 0.2s ease;
        }
        
        [data-testid="stSidebar"] .stButton > button:hover {
            background-color: #334155 !important;
            border-color: #475569 !important;
            color: #ffffff !important;
        }

        [data-testid="stSidebar"] div[data-testid="stPopover"] > button {
            background-color: transparent !important;
            border: 1px solid transparent !important;
            color: #cbd5e1 !important;
            padding: 0 !important;
            height: 100% !important;
            min-height: 48px !important; 
            display: flex !important;
            justify-content: center !important;
            align-items: center !important;
            border-radius: 8px !important;
            box-shadow: none !important;
        }
        [data-testid="stSidebar"] div[data-testid="stPopover"] > button:hover {
            background-color: rgba(255, 255, 255, 0.1) !important;
            color: #ffffff !important;
        }
        [data-testid="stSidebar"] div[data-testid="stPopover"] > button p {
            font-size: 22px !important;
            font-weight: bold !important;
        }

        .stApp { 
            background-color: #eef2ff; 
        }
        
        .ledger-card {
            background-color: #ffffff;
            border: 1px solid #e2e8f0;
            border-radius: 12px;
            padding: 20px;
            margin-bottom: 16px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.05);
            transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);
        }
        
        .ledger-card:hover {
            transform: translateY(-4px);
            box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.1), 0 8px 10px -6px rgba(0, 0, 0, 0.1);
            border-color: #cbd5e1;
        }
        
        .agent-name { font-size: 16px; font-weight: 700; color: #1e293b; margin-bottom: 6px; }
        .status-success { color: #16a34a; font-weight: 700; font-size: 13px; text-transform: uppercase; margin-bottom: 8px; }
        .status-error { color: #dc2626; font-weight: 700; font-size: 13px; text-transform: uppercase; margin-bottom: 8px; }
        .status-warning { color: #d97706; font-weight: 700; font-size: 13px; text-transform: uppercase; margin-bottom: 8px; }
        .desc-text { color: #475569; font-size: 14px; line-height: 1.6; font-family: inherit; }
        
        .matrix-banner {
            background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
            color: #ffffff;
            border-radius: 12px;
            padding: 24px;
            margin-bottom: 24px;
            display: flex;
            align-items: center;
        }
        .matrix-score { font-size: 36px; font-weight: 800; color: #fbbf24; margin-right: 20px; }

        /* 👑 PREMIUM RUNTIME DISPLAY PANELS CSS */
        .runtime-container {
            background-color: #0f172a;
            border: 2px solid #3b82f6;
            border-radius: 12px;
            padding: 24px;
            margin-bottom: 28px;
            color: #f8fafc;
        }
        .runtime-title { font-size: 18px; font-weight: 700; color: #3b82f6; margin-bottom: 16px; display: flex; align-items: center; }
        .runtime-pill { padding: 4px 10px; border-radius: 6px; font-size: 12px; font-weight: bold; margin-left: 12px; text-transform: uppercase;}
        .pill-active { background-color: #16a34a; color: #ffffff; }
        .pill-inactive { background-color: #dc2626; color: #ffffff; }
        
        .sub-terminal {
            background-color: #020617;
            border: 1px solid #1e293b;
            border-radius: 6px;
            padding: 14px;
            font-family: 'Courier New', Courier, monospace;
            font-size: 13px;
            color: #38bdf8;
            margin-bottom: 14px;
            white-space: pre-wrap;
        }
    </style>
""", unsafe_allow_html=True)

class StreamlitWSProxy:
    def __init__(self, placeholder_element):
        self.placeholder = placeholder_element
        self.log_lines = []

    async def send_json(self, data: dict):
        if data.get("type") == "log":
            msg = data.get("msg", "")
            self.log_lines.append(msg)
            self.placeholder.code("\n".join(self.log_lines), language="bash")

if "history" not in st.session_state:
    st.session_state.history = load_persistent_history()
if "active_view" not in st.session_state:
    st.session_state.active_view = st.session_state.history[0] if st.session_state.history else None
if "is_running" not in st.session_state:
    st.session_state.is_running = False

with st.sidebar:
    st.markdown("### 🕰️ Recent Audits")
    if not st.session_state.history:
        st.info("No execution histories tracked yet.")
    
    sorted_history = sorted(
        st.session_state.history, 
        key=lambda x: x.get("pinned", False), 
        reverse=True
    )
    
    for idx, run in enumerate(sorted_history):
        sb_col1, sb_col2 = st.columns([6, 1.2]) 
        
        with sb_col1:
            pin_prefix = "📌 " if run.get("pinned", False) else "📁 "
            btn_label = f"{pin_prefix}{run['display_name']}\nScore: {run['score']}/100 | ⏱️ {run['time']}"
            
            if st.button(btn_label, key=f"hist_item_{run['id']}", use_container_width=True):
                st.session_state.active_view = run
                st.rerun()
                
        with sb_col2:
            with st.popover("⋮", key=f"popover_{run['id']}"):
                if st.button("🔗 Share conversation", key=f"share_{run['id']}", use_container_width=True):
                    st.toast(f"Link copied for: {run['display_name']}")
                
                pin_label = "📍 Unpin item" if run.get("pinned", False) else "📌 Pin item"
                if st.button(pin_label, key=f"pin_{run['id']}", use_container_width=True):
                    run["pinned"] = not run.get("pinned", False)
                    save_persistent_history(st.session_state.history)
                    st.rerun()
                
                with st.form(key=f"rename_form_{run['id']}", clear_on_submit=True):
                    new_title = st.text_input("✏️ Rename Target", value=run['display_name'])
                    if st.form_submit_button("Apply Rename"):
                        if new_title.strip():
                            run['display_name'] = new_title.strip()
                            save_persistent_history(st.session_state.history)
                            st.rerun()
                
                if st.button("🗑️ Delete permanently", key=f"del_{run['id']}", use_container_width=True):
                    st.session_state.history = [item for item in st.session_state.history if item["id"] != run["id"]]
                    save_persistent_history(st.session_state.history)
                    if st.session_state.active_view and st.session_state.active_view["id"] == run["id"]:
                        st.session_state.active_view = st.session_state.history[0] if st.session_state.history else None
                    st.rerun()

st.title("🔬 AI Auto-Grader For Recruiters")

def lock_ui_state():
    st.session_state.is_running = True

col1, col2 = st.columns([3, 1])
with col1:
    url_input = st.text_input(
        "GitHub Repository Target Link", 
        placeholder="https://github.com/username/repository", 
        disabled=st.session_state.is_running,
        label_visibility="collapsed"
    )
with col2:
    calculate_btn = st.button(
        "▶ Grade Candidate Repository", 
        type="primary", 
        use_container_width=True, 
        disabled=st.session_state.is_running, 
        on_click=lock_ui_state
    )

if st.session_state.is_running:
    if not url_input.strip():
        st.warning("Please specify a valid repository path before activating evaluation engines.")
        st.session_state.is_running = False
        st.rerun()
        
    st.markdown("#### Live Agent Execution Stream Logs")
    stream_placeholder = st.empty()
    ws_proxy = StreamlitWSProxy(stream_placeholder)
    
    try:
        analysis_requirement = "Comprehensive system profile metric scan"
        backend_response = asyncio.run(run_workflow(analysis_requirement, url_input, ws_proxy))
        clean_name = url_input.split("github.com/")[-1].replace(".git", "")
        
        execution_record = {
            "id": str(uuid.uuid4()),
            "display_name": clean_name,
            "score": backend_response.get("score", 0),
            "runtime": backend_response.get("runtime", 0.0),
            "time": datetime.datetime.now().strftime("%I:%M %p"),
            "pinned": False,
            "agent_ledgers": backend_response.get("results", [])
        }
        st.session_state.history.insert(0, execution_record)
        save_persistent_history(st.session_state.history)
        st.session_state.active_view = execution_record
        
    except Exception as network_error:
        st.error(f"Execution boundary fault occurred within orchestrator core loops: {network_error}")
    finally:
        stream_placeholder.empty()
        st.session_state.is_running = False
        st.rerun()


if st.session_state.active_view and not st.session_state.is_running:
    current_report = st.session_state.active_view
    
    st.markdown(f"""
        <div class="matrix-banner">
            <div class="matrix-score">{current_report['score']}/100</div>
            <div>
                <strong style="font-size: 20px; display: block;">Evaluation Matrix Complete</strong>
                <span style="color: #94a3b8; font-size: 14px;">Multi-agent micro-audits finished verification checks against structural patterns. Execution completed in {current_report['runtime']}s.</span>
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    # Separate the checklist agents from our specialized Live Runtime Agent
    all_ledgers = current_report["agent_ledgers"]
    runtime_data = next((l for l in all_ledgers if l.get("agent") == "⚡ Live Environment & Execution Analytics"), None)
    static_ledgers = [l for l in all_ledgers if l.get("agent") != "⚡ Live Environment & Execution Analytics"]
    
    # STAGE ONE: DISPLAY RUNTIME EXECUTION ANALYTICS (Plugs in below the score banner)
    if runtime_data:
        state_str = runtime_data.get("working_state", "UNKNOWN")
        pill_class = "pill-active" if "RUNNING" in state_str else "pill-inactive"
        
        # Kept strictly flush-left to satisfy markdown compiler blocks
        st.markdown(f"""
<div class="runtime-container">
<div class="runtime-title">
⚡ Live Sandbox Environment & Runtime Diagnostics
<span class="runtime-pill {pill_class}">{state_str}</span>
</div>
<div style="font-size:14px; margin-bottom:8px; font-weight:bold; color:#94a3b8;">⚙️ COMPILATION & INTEGRITY MATRIX</div>
<div class="sub-terminal">{runtime_data.get('compilation', '')}</div>

<div style="font-size:14px; margin-bottom:8px; font-weight:bold; color:#94a3b8;">🧪 AUTOMATED TEST SUITE RUNNER OUTPUT</div>
<div class="sub-terminal" style="color:#a7f3d0;">{runtime_data.get('tests', '')}</div>

<div style="font-size:14px; margin-bottom:8px; font-weight:bold; color:#60a5fa;">🧠 GEMINI ELITE ARCHITECT CODE REVIEW</div>
<div style="background-color:#1e293b; border-radius:6px; padding:16px; font-size:14px; line-height:1.6; color:#e2e8f0; border-left:4px solid #3b82f6;">
{runtime_data.get('architecture', '')}
</div>
</div>
""", unsafe_allow_html=True)
        
    # STAGE TWO: DISPLAY STANDARD RULES LEDGERS
    st.markdown("### 📋 Detailed Agent Verification Checklist")
    for ledger in static_ledgers:
        agent_title = ledger.get("agent", "Unknown Agent")
        agent_raw_status = ledger.get("status", "error").lower()
        agent_output_text = ledger.get("output", "")
        
        if agent_raw_status == "success":
            status_css, status_label = "status-success", "SUCCESS"
        elif agent_raw_status == "warning":
            status_css, status_label = "status-warning", "WARNING"
        else:
            status_css, status_label = "status-error", "ERROR"
            
        st.markdown(f"""
        <div class="ledger-card">
            <div class="agent-name">{agent_title}</div>
            <div class="{status_css}">{status_label}</div>
            <div class="desc-text">{agent_output_text}</div>
        </div>
        """, unsafe_allow_html=True)