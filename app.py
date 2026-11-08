"""
SmartCPU - Premium Architecture Workbench
"""
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from core.instruction_parser import InstructionParser
from core.cpu_controller import CPUController
from visualization.pipeline_chart import generate_pipeline_gantt

st.set_page_config(page_title="SmartCPU Workbench", layout="wide", page_icon="CPU", initial_sidebar_state="expanded")

CSS = """
<style>
    :root { --bg-primary: #0d1117; --bg-secondary: #161b22; --bg-tertiary: #21262d; --text-primary: #c9d1d9; --text-secondary: #8b949e; --accent-blue: #58a6ff; --accent-green: #3fb950; --font-mono: 'SFMono-Regular', Consolas, monospace; }
    .stApp { background-color: var(--bg-primary); color: var(--text-primary); }
    section[data-testid="stSidebar"] { background-color: var(--bg-secondary); border-right: 1px solid #30363d; }
    h1, h2, h3 { color: var(--accent-blue); font-weight: 600; }
    h1 { font-size: 1.8rem; border-bottom: 1px solid #30363d; padding-bottom: 10px; }
    div[data-testid="stMetricValue"] { font-size: 1.8rem !important; color: var(--text-primary) !important; font-family: var(--font-mono); }
    div[data-testid="stMetricLabel"] { color: var(--text-secondary) !important; font-size: 0.8rem; text-transform: uppercase; }
    button[data-baseweb="tab"] { background-color: transparent; color: var(--text-secondary); border: none; border-bottom: 2px solid transparent; }
    button[data-baseweb="tab"][aria-selected="true"] { color: var(--accent-blue); border-bottom: 2px solid var(--accent-blue); }
    .stDataFrame { background-color: var(--bg-secondary); border-radius: 6px; }
    code, pre { font-family: var(--font-mono) !important; background-color: var(--bg-tertiary) !important; color: var(--accent-green) !important; }
    .arch-diagram { display: flex; justify-content: space-between; align-items: center; background: var(--bg-secondary); padding: 20px; border-radius: 8px; border: 1px solid #30363d; margin: 20px 0; }
    .arch-stage { text-align: center; padding: 10px 15px; background: var(--bg-tertiary); border-radius: 4px; border: 1px solid var(--accent-blue); color: var(--accent-blue); font-weight: bold; font-family: var(--font-mono); }
    .arch-arrow { color: var(--text-secondary); font-size: 1.5rem; }
</style>
"""
st.markdown(CSS, unsafe_allow_html=True)

if 'cpu' not in st.session_state: st.session_state.cpu = CPUController()

with st.sidebar:
    st.markdown("### SMARTCPU")
    st.caption("Architecture & Performance Workbench")
    st.divider()
    st.markdown("#### Simulation Control")
    assembly_code = st.text_area("Assembly Program", height=300, value="MOV R1, 10\nMOV R2, 20\nADD R3, R1, R2\nSUB R4, R3, R1\nSTORE R4, 100\nLOAD R5, 100\nLOAD R6, 100", label_visibility="collapsed")
    col1, col2 = st.columns(2)
    run_btn = col1.button("Run", type="primary", use_container_width=True)
    reset_btn = col2.button("Reset", use_container_width=True)
    st.divider()
    st.caption("v2.0.0 | Engineering Build")

if run_btn:
    parser = InstructionParser()
    instructions = parser.parse_program(assembly_code)
    if instructions: st.session_state.cpu.execute_program(instructions)
    else: st.error("Invalid assembly syntax.")

if reset_btn:
    st.session_state.cpu.reset()
    st.rerun()

state = st.session_state.cpu.get_state()
st.title("CPU Architecture & Performance Analytics")
tab1, tab2, tab3, tab4, tab5 = st.tabs(["Overview", "Pipeline", "Memory", "Hazards", "Trace"])

with tab1:
    kpi1, kpi2, kpi3, kpi4, kpi5, kpi6 = st.columns(6)
    total_cycles = state["total_cycles"]
    total_instr = state["total_instructions"]
    cpi = total_cycles / total_instr if total_instr > 0 else 0
    ipc = 1 / cpi if cpi > 0 else 0
    kpi1.metric("Instructions", total_instr); kpi2.metric("Clock Cycles", total_cycles)
    kpi3.metric("CPI", f"{cpi:.2f}"); kpi4.metric("IPC", f"{ipc:.2f}")
    kpi5.metric("Stalls", state["hazard_stats"]["total_stalls"]); kpi6.metric("Cache Hit Ratio", f"{state['cache_stats']['hit_ratio']}%")
    st.markdown("### Register File State")
    reg_df = pd.DataFrame([{"Register": k, "Value (Hex)": f"0x{v:08X}", "Value (Dec)": v} for k, v in state["registers"].items()])
    st.dataframe(reg_df, use_container_width=True, hide_index=True, height=250)
    st.markdown("### Microarchitecture Datapath")
    st.markdown("""<div class="arch-diagram"><div class="arch-stage">IF<br><span style="font-size:0.7rem;color:#8b949e">Fetch</span></div><div class="arch-arrow">></div><div class="arch-stage">ID<br><span style="font-size:0.7rem;color:#8b949e">Decode</span></div><div class="arch-arrow">></div><div class="arch-stage">EX<br><span style="font-size:0.7rem;color:#8b949e">ALU/Forward</span></div><div class="arch-arrow">></div><div class="arch-stage">MEM<br><span style="font-size:0.7rem;color:#8b949e">Cache/RAM</span></div><div class="arch-arrow">></div><div class="arch-stage">WB<br><span style="font-size:0.7rem;color:#8b949e">Write Back</span></div></div>""", unsafe_allow_html=True)

with tab2:
    st.markdown("### Pipeline Execution Timeline")
    if state["pipeline_schedule"]:
        fig = generate_pipeline_gantt(state["pipeline_schedule"])
        st.plotly_chart(fig, use_container_width=True)
        eff_col1, eff_col2 = st.columns(2)
        eff_col1.metric("Ideal Cycles (No Hazards)", total_instr + 4)
        eff_col2.metric("Actual Cycles", total_cycles)
    else: st.info("Run a simulation to view pipeline data.")

with tab3:
    st.markdown("### Cache Hierarchy Statistics")
    m_col1, m_col2, m_col3 = st.columns(3)
    m_col1.metric("Policy", state["cache_stats"].get("policy", "LRU"))
    m_col2.metric("Hits / Misses", f"{state['cache_stats']['hits']} / {state['cache_stats']['misses']}")
    m_col3.metric("Hit Ratio", f"{state['cache_stats']['hit_ratio']}%")
    st.markdown("### Cache Line State (LRU)")
    if state["cache_lines"]: st.dataframe(pd.DataFrame(state["cache_lines"]), use_container_width=True, hide_index=True)
    st.markdown("### Memory Access Trace")
    if state["memory_trace"]: st.dataframe(pd.DataFrame(state["memory_trace"]), use_container_width=True, hide_index=True)

with tab4:
    st.markdown("### Hazard Analysis Center")
    h_col1, h_col2 = st.columns(2)
    h_col1.metric("Data Forwarding Ops", state["hazard_stats"]["data_forwarding_count"])
    h_col2.metric("Pipeline Stalls", state["hazard_stats"]["total_stalls"])
    st.markdown("#### Forwarding Log (Resolved Dependencies)")
    if state["hazard_stats"]["forwarding_log"]:
        for log in state["hazard_stats"]["forwarding_log"]: st.success(f"Resolved: {log}")
    st.markdown("#### Detected Hazards (Stalls & Control)")
    if state["hazard_stats"]["hazards"]:
        for h in state["hazard_stats"]["hazards"]:
            if h["type"] == "CRITICAL": st.error(f"{h['type']}: {h['msg']}")
            else: st.warning(f"{h['type']}: {h['msg']}")

with tab5:
    st.markdown("### Instruction Execution Trace")
    if state["execution_log"]:
        df_trace = pd.DataFrame(state["execution_log"])
        st.dataframe(df_trace, use_container_width=True, hide_index=True, height=500)
