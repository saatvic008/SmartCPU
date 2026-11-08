# run_final_integration.py
from agent_commit import bot_commit

# --- PAYLOAD: Final SmartCPU Dashboard ---
final_app_code = '''"""
SmartCPU Interactive Dashboard - Final Version
Integrates CPU Controller, Pipeline Visualization, Cache, and Hazards.
"""
import streamlit as st
import pandas as pd
from core.instruction_parser import InstructionParser
from core.cpu_controller import CPUController
from visualization.pipeline_chart import generate_pipeline_gantt

st.set_page_config(page_title="SmartCPU Simulator", layout="wide", page_icon="🖥️")
st.title("🖥️ SmartCPU - Final Interactive Architecture Simulator")

# Initialize Session State
if 'cpu' not in st.session_state:
    st.session_state.cpu = CPUController()

# Sidebar Controls
st.sidebar.header("⚙️ Execution Controls")
assembly_code = st.sidebar.text_area(
    "Enter Assembly Instructions:", 
    height=300, 
    value="MOV R1, 10\\nMOV R2, 20\\nADD R3, R1, R2\\nSUB R4, R3, R1\\nSTORE R4, 100\\nLOAD R5, 100\\nLOAD R6, 100"
)

col1, col2 = st.sidebar.columns(2)
run_btn = col1.button("▶️ Execute All", type="primary")
reset_btn = col2.button("🔄 Reset CPU")

if reset_btn:
    st.session_state.cpu.reset()
    st.rerun()

# Execution Engine
if run_btn:
    parser = InstructionParser()
    instructions = parser.parse_program(assembly_code)
    st.session_state.cpu.execute_program(instructions)

# Get current state
state = st.session_state.cpu.get_state()

# Main Dashboard Layout
st.subheader("📊 CPU Registers")
st.json(state["registers"])

st.subheader("📈 Pipeline Visualization (Gantt Chart)")
if state["pipeline_log"]:
    fig = generate_pipeline_gantt(state["pipeline_log"])
    st.plotly_chart(fig, use_container_width=True)
else:
    st.info("Execute instructions to see the pipeline chart.")

col1, col2 = st.columns(2)

with col1:
    st.subheader("💾 Cache Memory Stats & Lines")
    cache_stats = state["cache_stats"]
    st.metric(label="Cache Hits", value=cache_stats['hits'])
    st.metric(label="Cache Misses", value=cache_stats['misses'])
    st.metric(label="Hit Ratio", value=f"{cache_stats['hit_ratio']}%")
    st.metric(label="Policy", value=cache_stats.get('policy', 'LRU'))
    
    st.write("**Current Cache Lines:**")
    if hasattr(st.session_state.cpu.memory, 'get_cache_lines_for_ui'):
        st.dataframe(pd.DataFrame(st.session_state.cpu.memory.get_cache_lines_for_ui()))

with col2:
    st.subheader("⚠️ Hazard & Forwarding Logs")
    hazard_stats = state["hazard_stats"]
    st.metric(label="Total Stalls", value=hazard_stats['total_stalls'])
    st.metric(label="Data Forwarding Count", value=hazard_stats['data_forwarding_count'])
    
    if hazard_stats['forwarding_log']:
        st.write("**Forwarding Actions:**")
        for log in hazard_stats['forwarding_log']:
            st.success(log)
            
    if hazard_stats['hazards']:
        st.write("**Detected Hazards:**")
        for log in hazard_stats['hazards']:
            st.warning(log)

st.subheader("📝 Execution Log")
for log in state["execution_log"]:
    st.text(log)
'''

# Execute Bot Commit
print("Triggering UI/Test Bot for Final Dashboard Integration...")
bot_commit(
    file_path="app.py",
    content=final_app_code,
    commit_message="feat(ui): final dashboard integration with pipeline chart, cache lines, and hazard logs",
    bot_type="ui"
)

print("Final Integration Complete!")