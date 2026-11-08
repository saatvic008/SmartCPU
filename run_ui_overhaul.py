# run_ui_overhaul.py
from agent_commit import bot_commit

ui_code = '''"""
SmartCPU - Industry Standard Dashboard
Features: Tabbed Interface, Custom CSS, Professional Layout.
"""
import streamlit as st
import pandas as pd
from core.instruction_parser import InstructionParser
from core.cpu_controller import CPUController
from visualization.pipeline_chart import generate_pipeline_gantt

# --- 1. Page Config & Custom CSS ---
st.set_page_config(
    page_title="SmartCPU Pro", 
    layout="wide", 
    page_icon="🖥️",
    initial_sidebar_state="expanded"
)

# Inject Custom CSS for a "Cyber/Tech" look
st.markdown("""
<style>
    /* Main Background */
    .stApp {
        background-color: #0e1117;
        color: #fafafa;
    }
    /* Sidebar Styling */
    section[data-testid="stSidebar"] {
        background-color: #161b22;
        border-right: 1px solid #30363d;
    }
    /* Headers */
    h1, h2, h3 {
        color: #58a6ff;
        font-family: 'Segoe UI', sans-serif;
    }
    /* Metrics */
    div[data-testid="stMetricValue"] {
        font-size: 2rem !important;
        color: #3fb950 !important;
    }
    /* Tabs */
    button[data-baseweb="tab"] {
        background-color: #21262d;
        color: #c9d1d9;
        border-radius: 5px 5px 0 0;
    }
    button[data-baseweb="tab"][aria-selected="true"] {
        background-color: #0d1117;
        color: #58a6ff;
        font-weight: bold;
    }
    /* Code/Log Blocks */
    .stCodeBlock, div.stCode {
        background-color: #161b22;
        border: 1px solid #30363d;
    }
</style>
""", unsafe_allow_html=True)

# --- 2. Initialization ---
if 'cpu' not in st.session_state:
    st.session_state.cpu = CPUController()

# --- 3. Sidebar (Control Panel) ---
with st.sidebar:
    st.title("⚙️ Control Panel")
    st.markdown("---")
    
    assembly_code = st.text_area(
        "Assembly Input", 
        height=250, 
        value="MOV R1, 10\\nMOV R2, 20\\nADD R3, R1, R2\\nSUB R4, R3, R1\\nSTORE R4, 100\\nLOAD R5, 100\\nLOAD R6, 100",
        label_visibility="collapsed"
    )
    
    col1, col2 = st.columns(2)
    run_btn = col1.button("▶ Run", type="primary", use_container_width=True)
    reset_btn = col2.button("↺ Reset", use_container_width=True)

    st.markdown("---")
    st.caption("SmartCPU v2.0 | Powered by Streamlit")

# --- 4. Execution Logic ---
if run_btn:
    parser = InstructionParser()
    instructions = parser.parse_program(assembly_code)
    st.session_state.cpu.execute_program(instructions)

if reset_btn:
    st.session_state.cpu.reset()
    st.rerun()

state = st.session_state.cpu.get_state()

# --- 5. Main Dashboard (Tabbed Interface) ---
st.title("🖥️ SmartCPU Architecture Simulator")

tab1, tab2, tab3, tab4 = st.tabs(["📊 Overview", "📈 Pipeline", "💾 Memory", "⚠️ Hazards"])

# TAB 1: Overview (Registers & Key Metrics)
with tab1:
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.subheader("General Purpose Registers")
        st.json(state["registers"])
        
    with col2:
        st.subheader("Performance Metrics")
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Total Cycles", len(state["pipeline_log"]))
        m2.metric("Cache Hit Ratio", f"{state['cache_stats']['hit_ratio']}%")
        m3.metric("Pipeline Stalls", state["hazard_stats"]["total_stalls"])
        m4.metric("Forwarding Ops", state["hazard_stats"]["data_forwarding_count"])

# TAB 2: Pipeline Visualization
with tab2:
    st.subheader("Instruction Pipeline Execution (Gantt Chart)")
    if state["pipeline_log"]:
        fig = generate_pipeline_gantt(state["pipeline_log"])
        # Make chart taller and cleaner
        fig.update_layout(height=500, margin=dict(l=20, r=20, t=40, b=20))
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Run instructions to generate pipeline data.")

# TAB 3: Memory Hierarchy
with tab3:
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Cache Statistics")
        stats = state["cache_stats"]
        st.metric("Cache Policy", stats.get('policy', 'LRU'))
        st.metric("Hits", stats['hits'])
        st.metric("Misses", stats['misses'])
        
    with col2:
        st.subheader("Cache Line State")
        if hasattr(st.session_state.cpu.memory, 'get_cache_lines_for_ui'):
            df = pd.DataFrame(st.session_state.cpu.memory.get_cache_lines_for_ui())
            st.dataframe(df, use_container_width=True, hide_index=True)

# TAB 4: System Logs & Hazards
with tab4:
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("⚠️ Hazard Detection Log")
        h_stats = state["hazard_stats"]
        if h_stats['forwarding_log']:
            for log in h_stats['forwarding_log']:
                st.success(f"✅ {log}")
        if h_stats['hazards']:
            for log in h_stats['hazards']:
                st.warning(f"⚠️ {log}")
        if not h_stats['forwarding_log'] and not h_stats['hazards']:
            st.info("No hazards detected. Pipeline running smoothly.")

    with col2:
        st.subheader("📝 Execution Trace")
        log_text = "\\n".join(state["execution_log"])
        st.code(log_text, language="assembly")
'''

print("Triggering UI Overhaul...")
bot_commit(
    file_path="app.py",
    content=ui_code,
    commit_message="feat(ui): complete UI overhaul with tabs, custom CSS, and professional layout",
    bot_type="ui"
)
print("UI Overhaul Complete!")