# run_premium_overhaul.py
from agent_commit import bot_commit
import os

# --- 1. HAZARD DETECTION (FIXED LOGIC) ---
hazard_code = '''"""
Hazard Detection Module - Premium Edition
Accurately classifies RAW, Load-Use, and Control hazards.
"""

class HazardDetector:
    def __init__(self):
        self.stalls = 0
        self.forwarding_count = 0
        self.detected_hazards = []
        self.forwarding_log = []

    def check_raw_hazard(self, current_instr: dict, previous_instr: dict) -> dict:
        result = {"hazard": False, "stall": 0, "forward": False, "type": None}
        
        if not previous_instr:
            return result

        current_operands = current_instr.get('operands', [])
        prev_operands = previous_instr.get('operands', [])
        prev_dest = prev_operands[0] if len(prev_operands) > 0 else None

        # Check dependencies (skip destination register of current instruction)
        for operand in current_operands[1:]: 
            if operand == prev_dest and prev_dest is not None:
                result["hazard"] = True
                prev_opcode = previous_instr.get('opcode')
                
                # LOAD-USE HAZARD: Requires 1 cycle stall
                if prev_opcode == 'LOAD':
                    result["stall"] = 1
                    result["type"] = "Load-Use Hazard"
                    self.stalls += 1
                    msg = f"Load-Use Hazard: {current_instr['raw']} must wait for memory read in {previous_instr['raw']}"
                    self.detected_hazards.append({"type": "CRITICAL", "msg": msg})
                
                # RAW DEPENDENCY: Resolved via Data Forwarding (No Stall)
                elif prev_opcode in ['ADD', 'SUB', 'AND', 'OR', 'XOR', 'MOV']:
                    result["forward"] = True
                    result["type"] = "RAW Dependency (Forwarded)"
                    self.forwarding_count += 1
                    msg = f"Data Forwarding: {current_instr['raw']} receives result directly from {previous_instr['raw']}"
                    self.forwarding_log.append(msg)
                    
        return result

    def check_control_hazard(self, instruction: dict) -> bool:
        if instruction.get('opcode') in ['JMP', 'JE', 'JNE', 'CALL']:
            self.stalls += 2
            self.detected_hazards.append({"type": "WARNING", "msg": f"Control Hazard: Branch {instruction['raw']} causes 2-cycle penalty."})
            return True
        return False

    def get_stats(self) -> dict:
        return {
            "total_stalls": self.stalls,
            "data_forwarding_count": self.forwarding_count,
            "hazards": self.detected_hazards,
            "forwarding_log": self.forwarding_log
        }
'''

# --- 2. CPU CONTROLLER (ENHANCED LOGGING) ---
controller_code = '''"""
CPU Controller Module - Premium Edition
Orchestrates execution and generates structured pipeline schedules.
"""
from core.registers import RegisterFile
from core.alu import ALU
from core.memory import MemorySystem
from pipeline.pipeline_engine import PipelineEngine
from pipeline.hazard_detection import HazardDetector

class CPUController:
    def __init__(self):
        self.registers = RegisterFile()
        self.alu = ALU()
        self.memory = MemorySystem()
        self.pipeline = PipelineEngine()
        self.hazard_detector = HazardDetector()
        
        self.execution_log = []
        self.pipeline_schedule = [] # Structured data for Gantt chart
        self.memory_trace = []      # Structured data for Memory tab

    def reset(self):
        self.registers.reset()
        self.memory.reset()
        self.pipeline.reset()
        self.hazard_detector = HazardDetector()
        self.execution_log = []
        self.pipeline_schedule = []
        self.memory_trace = []

    def execute_program(self, instructions: list):
        self.reset()
        prev_instr = None
        current_cycle = 0
        
        for instr in instructions:
            # 1. Hazard Check
            hazard_result = self.hazard_detector.check_raw_hazard(instr, prev_instr)
            is_control_hazard = self.hazard_detector.check_control_hazard(instr)
            
            # 2. Handle Stalls
            stalls = hazard_result.get("stall", 0)
            if is_control_hazard: stalls += 2
            
            for _ in range(stalls):
                current_cycle += 1
                self.pipeline_schedule.append({
                    "Instruction": instr['raw'], "Stage": "STALL", 
                    "Start": current_cycle, "Finish": current_cycle + 1, "Status": "Stall"
                })

            # 3. Pipeline Stages (IF, ID, EX, MEM, WB)
            stages = ["IF", "ID", "EX", "MEM", "WB"]
            instr_start_cycle = current_cycle
            
            for i, stage in enumerate(stages):
                current_cycle += 1
                status = "Forwarded" if (stage == "EX" and hazard_result.get("forward")) else "Normal"
                
                self.pipeline_schedule.append({
                    "Instruction": instr['raw'], "Stage": stage,
                    "Start": current_cycle - 1, "Finish": current_cycle, "Status": status
                })

            # 4. Functional Execution
            self._execute_instruction(instr, current_cycle)
            prev_instr = instr

    def _execute_instruction(self, instr: dict, cycle: int):
        op = instr['opcode']
        ops = instr['operands']
        log_entry = {"Cycle": cycle, "PC": cycle-1, "Instruction": instr['raw'], "Op": op, "Result": "-"}
        
        try:
            if op == 'MOV':
                val = int(ops[1])
                self.registers.write(ops[0], val)
                log_entry["Result"] = f"R{ops[0][-1]} <- {val}"
            elif op in ['ADD', 'SUB', 'AND', 'OR', 'XOR']:
                v1 = self.registers.read(ops[1])
                v2 = self.registers.read(ops[2])
                res = self.alu.execute(op, v1, v2)
                self.registers.write(ops[0], res)
                log_entry["Result"] = f"R{ops[0][-1]} <- {res}"
            elif op == 'STORE':
                val = self.registers.read(ops[0])
                self.memory.write(int(ops[1]), val)
                log_entry["Result"] = f"MEM[{ops[1]}] <- {val}"
                self.memory_trace.append({"Cycle": cycle, "Instr": instr['raw'], "Addr": ops[1], "Value": val, "Type": "STORE", "Cache": "Write-Through"})
            elif op == 'LOAD':
                val = self.memory.read(int(ops[1]))
                self.registers.write(ops[0], val)
                log_entry["Result"] = f"R{ops[0][-1]} <- {val}"
                hit = "Hit" if self.memory.cache_hits > 0 else "Miss" # Simplified for trace
                self.memory_trace.append({"Cycle": cycle, "Instr": instr['raw'], "Addr": ops[1], "Value": val, "Type": "LOAD", "Cache": hit})
        except Exception as e:
            log_entry["Result"] = f"Error: {str(e)}"
            
        self.execution_log.append(log_entry)

    def get_state(self):
        return {
            "registers": self.registers.get_all(),
            "cache_stats": self.memory.get_stats(),
            "cache_lines": self.memory.get_cache_lines_for_ui() if hasattr(self.memory, 'get_cache_lines_for_ui') else [],
            "execution_log": self.execution_log,
            "pipeline_schedule": self.pipeline_schedule,
            "hazard_stats": self.hazard_detector.get_stats(),
            "memory_trace": self.memory_trace,
            "total_cycles": max([s["Finish"] for s in self.pipeline_schedule]) if self.pipeline_schedule else 0,
            "total_instructions": len(self.execution_log)
        }
'''

# --- 3. PIPELINE CHART (ENHANCED GANTT) ---
chart_code = '''"""
Pipeline Visualization Module - Premium Edition
Generates professional Gantt charts using Plotly Graph Objects.
"""
import plotly.graph_objects as go
import pandas as pd

def generate_pipeline_gantt(schedule: list) -> go.Figure:
    if not schedule:
        fig = go.Figure()
        fig.update_layout(title="No Pipeline Data", template="plotly_dark", height=300)
        return fig

    df = pd.DataFrame(schedule)
    
    # Color mapping
    color_map = {
        "IF": "#1f77b4", "ID": "#ff7f0e", "EX": "#2ca02c", 
        "MEM": "#d62728", "WB": "#9467bd", "STALL": "#7f7f7f"
    }

    fig = go.Figure()

    # Get unique instructions in order
    instructions = list(dict.fromkeys(df["Instruction"].tolist()))
    
    for instr in instructions:
        instr_data = df[df["Instruction"] == instr]
        for _, row in instr_data.iterrows():
            stage = row["Stage"]
            color = color_map.get(stage, "#ffffff")
            
            # Highlight hazards
            opacity = 0.4 if row["Status"] == "Stall" else 1.0
            
            fig.add_trace(go.Bar(
                name=stage,
                y=[instr],
                x=[row["Finish"] - row["Start"]],
                base=[row["Start"]],
                orientation='h',
                marker_color=color,
                opacity=opacity,
                hovertemplate=f"<b>{instr}</b><br>Stage: {stage}<br>Cycle: {row['Start']} to {row['Finish']}<br>Status: {row['Status']}<extra></extra>"
            ))

    fig.update_layout(
        title="Pipeline Execution Timeline",
        xaxis_title="Clock Cycles",
        yaxis_title="Instructions",
        template="plotly_dark",
        height=max(300, len(instructions) * 40 + 50),
        barmode='overlay',
        showlegend=True,
        legend_title="Pipeline Stage",
        xaxis=dict(tickmode='linear', tick0=1, dtick=1),
        margin=dict(l=150, r=20, t=40, b=40) # Space for long instruction names
    )
    
    # Clean up legend (show each stage only once)
    seen = set()
    for trace in fig.data:
        if trace.name in seen:
            trace.showlegend = False
        else:
            seen.add(trace.name)

    return fig
'''

# --- 4. PREMIUM APP.PY (THE WORKBENCH) ---
app_code = '''"""
SmartCPU - Premium Architecture Workbench
Industry-standard UI/UX with modular rendering.
"""
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from core.instruction_parser import InstructionParser
from core.cpu_controller import CPUController
from visualization.pipeline_chart import generate_pipeline_gantt

# --- DESIGN SYSTEM & CSS ---
st.set_page_config(page_title="SmartCPU Workbench", layout="wide", page_icon="⚛️", initial_sidebar_state="expanded")

CSS = """
<style>
    :root {
        --bg-primary: #0d1117;
        --bg-secondary: #161b22;
        --bg-tertiary: #21262d;
        --text-primary: #c9d1d9;
        --text-secondary: #8b949e;
        --accent-blue: #58a6ff;
        --accent-green: #3fb950;
        --accent-amber: #d29922;
        --accent-red: #f85149;
        --font-mono: 'SFMono-Regular', Consolas, 'Liberation Mono', Menlo, monospace;
    }
    .stApp { background-color: var(--bg-primary); color: var(--text-primary); font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; }
    section[data-testid="stSidebar"] { background-color: var(--bg-secondary); border-right: 1px solid #30363d; }
    h1, h2, h3 { color: var(--accent-blue); font-weight: 600; letter-spacing: -0.5px; }
    h1 { font-size: 1.8rem; border-bottom: 1px solid #30363d; padding-bottom: 10px; margin-bottom: 20px; }
    h2 { font-size: 1.4rem; margin-top: 20px; }
    h3 { font-size: 1.1rem; color: var(--text-secondary); text-transform: uppercase; letter-spacing: 1px; font-size: 0.8rem; }
    
    /* Metrics */
    div[data-testid="stMetricValue"] { font-size: 1.8rem !important; color: var(--text-primary) !important; font-family: var(--font-mono); }
    div[data-testid="stMetricLabel"] { color: var(--text-secondary) !important; font-size: 0.8rem; text-transform: uppercase; }
    
    /* Tabs */
    button[data-baseweb="tab"] { background-color: transparent; color: var(--text-secondary); border: none; border-bottom: 2px solid transparent; border-radius: 0; font-weight: 500; }
    button[data-baseweb="tab"][aria-selected="true"] { color: var(--accent-blue); border-bottom: 2px solid var(--accent-blue); background-color: transparent; }
    div[data-testid="stHorizontalBlock"] { background-color: var(--bg-secondary); border: 1px solid #30363d; border-radius: 6px; padding: 15px; margin-bottom: 15px; }
    
    /* Dataframes & Code */
    .stDataFrame { background-color: var(--bg-secondary); border-radius: 6px; }
    code, pre { font-family: var(--font-mono) !important; background-color: var(--bg-tertiary) !important; color: var(--accent-green) !important; border-radius: 4px; }
    
    /* Custom Architecture Diagram */
    .arch-diagram { display: flex; justify-content: space-between; align-items: center; background: var(--bg-secondary); padding: 20px; border-radius: 8px; border: 1px solid #30363d; margin: 20px 0; }
    .arch-stage { text-align: center; padding: 10px 15px; background: var(--bg-tertiary); border-radius: 4px; border: 1px solid var(--accent-blue); color: var(--accent-blue); font-weight: bold; font-family: var(--font-mono); }
    .arch-arrow { color: var(--text-secondary); font-size: 1.5rem; }
</style>
"""
st.markdown(CSS, unsafe_allow_html=True)

# --- STATE MANAGEMENT ---
if 'cpu' not in st.session_state:
    st.session_state.cpu = CPUController()

# --- SIDEBAR: CONTROL CENTER ---
with st.sidebar:
    st.markdown("### ⚛️ SMARTCPU")
    st.caption("Architecture & Performance Workbench")
    st.divider()
    
    st.markdown("#### Simulation Control")
    assembly_code = st.text_area(
        "Assembly Program", 
        height=300, 
        value="MOV R1, 10\\nMOV R2, 20\\nADD R3, R1, R2\\nSUB R4, R3, R1\\nSTORE R4, 100\\nLOAD R5, 100\\nLOAD R6, 100",
        label_visibility="collapsed"
    )
    
    col1, col2 = st.columns(2)
    run_btn = col1.button("▶ Run", type="primary", use_container_width=True)
    reset_btn = col2.button("↺ Reset", use_container_width=True)
    
    st.divider()
    st.markdown("#### Sample Programs")
    if st.button("Load Fibonacci", use_container_width=True):
        st.session_state.sample_code = "MOV R1, 0\\nMOV R2, 1\\nADD R3, R1, R2\\nMOV R1, R2\\nMOV R2, R3"
        st.rerun()
    if st.button("Load Cache Test", use_container_width=True):
        st.session_state.sample_code = "STORE R1, 0\\nSTORE R2, 4\\nLOAD R3, 0\\nLOAD R4, 4\\nLOAD R5, 0"
        st.rerun()

    if hasattr(st.session_state, 'sample_code'):
        assembly_code = st.session_state.sample_code

    st.divider()
    st.caption("v2.0.0 | Engineering Build")

# --- EXECUTION LOGIC ---
if run_btn:
    parser = InstructionParser()
    instructions = parser.parse_program(assembly_code)
    if instructions:
        st.session_state.cpu.execute_program(instructions)
    else:
        st.error("Invalid assembly syntax.")

if reset_btn:
    st.session_state.cpu.reset()
    st.rerun()

state = st.session_state.cpu.get_state()

# --- MAIN WORKSPACE ---
st.title("CPU Architecture & Performance Analytics")

tab1, tab2, tab3, tab4, tab5 = st.tabs(["📊 Overview", "📈 Pipeline", "💾 Memory", "⚠️ Hazards", "📝 Trace"])

# TAB 1: OVERVIEW
with tab1:
    # KPI Cards
    kpi1, kpi2, kpi3, kpi4, kpi5, kpi6 = st.columns(6)
    total_cycles = state["total_cycles"]
    total_instr = state["total_instructions"]
    cpi = total_cycles / total_instr if total_instr > 0 else 0
    ipc = 1 / cpi if cpi > 0 else 0
    
    kpi1.metric("Instructions", total_instr)
    kpi2.metric("Clock Cycles", total_cycles)
    kpi3.metric("CPI", f"{cpi:.2f}")
    kpi4.metric("IPC", f"{ipc:.2f}")
    kpi5.metric("Stalls", state["hazard_stats"]["total_stalls"])
    kpi6.metric("Cache Hit Ratio", f"{state['cache_stats']['hit_ratio']}%")

    st.markdown("### Register File State")
    reg_df = pd.DataFrame([{"Register": k, "Value (Hex)": f"0x{v:08X}", "Value (Dec)": v} for k, v in state["registers"].items()])
    st.dataframe(reg_df, use_container_width=True, hide_index=True, height=250)

    st.markdown("### Microarchitecture Datapath")
    st.markdown("""
    <div class="arch-diagram">
        <div class="arch-stage">IF<br><span style="font-size:0.7rem;color:#8b949e">Fetch</span></div>
        <div class="arch-arrow">→</div>
        <div class="arch-stage">ID<br><span style="font-size:0.7rem;color:#8b949e">Decode</span></div>
        <div class="arch-arrow">→</div>
        <div class="arch-stage">EX<br><span style="font-size:0.7rem;color:#8b949e">ALU/Forward</span></div>
        <div class="arch-arrow">→</div>
        <div class="arch-stage">MEM<br><span style="font-size:0.7rem;color:#8b949e">Cache/RAM</span></div>
        <div class="arch-arrow">→</div>
        <div class="arch-stage">WB<br><span style="font-size:0.7rem;color:#8b949e">Write Back</span></div>
    </div>
    """, unsafe_allow_html=True)

# TAB 2: PIPELINE
with tab2:
    st.markdown("### Pipeline Execution Timeline")
    if state["pipeline_schedule"]:
        fig = generate_pipeline_gantt(state["pipeline_schedule"])
        st.plotly_chart(fig, use_container_width=True)
        
        st.markdown("#### Pipeline Efficiency")
        eff_col1, eff_col2 = st.columns(2)
        eff_col1.metric("Ideal Cycles (No Hazards)", total_instr + 4)
        eff_col2.metric("Actual Cycles", total_cycles)
    else:
        st.info("Run a simulation to view pipeline data.")

# TAB 3: MEMORY
with tab3:
    st.markdown("### Cache Hierarchy Statistics")
    m_col1, m_col2, m_col3 = st.columns(3)
    m_col1.metric("Policy", state["cache_stats"].get("policy", "LRU"))
    m_col2.metric("Hits / Misses", f"{state['cache_stats']['hits']} / {state['cache_stats']['misses']}")
    m_col3.metric("Hit Ratio", f"{state['cache_stats']['hit_ratio']}%")

    st.markdown("### Cache Line State (LRU)")
    if state["cache_lines"]:
        st.dataframe(pd.DataFrame(state["cache_lines"]), use_container_width=True, hide_index=True)
    else:
        st.warning("Cache not initialized.")

    st.markdown("### Memory Access Trace")
    if state["memory_trace"]:
        st.dataframe(pd.DataFrame(state["memory_trace"]), use_container_width=True, hide_index=True)
    else:
        st.info("No memory operations performed.")

# TAB 4: HAZARDS
with tab4:
    st.markdown("### Hazard Analysis Center")
    h_col1, h_col2 = st.columns(2)
    h_col1.metric("Data Forwarding Ops", state["hazard_stats"]["data_forwarding_count"])
    h_col2.metric("Pipeline Stalls", state["hazard_stats"]["total_stalls"])

    st.markdown("#### Forwarding Log (Resolved Dependencies)")
    if state["hazard_stats"]["forwarding_log"]:
        for log in state["hazard_stats"]["forwarding_log"]:
            st.success(f"✅ **Resolved:** {log}")
    else:
        st.caption("No forwarding required.")

    st.markdown("#### Detected Hazards (Stalls & Control)")
    if state["hazard_stats"]["hazards"]:
        for h in state["hazard_stats"]["hazards"]:
            if h["type"] == "CRITICAL":
                st.error(f"🛑 **{h['type']}:** {h['msg']}")
            else:
                st.warning(f"⚠️ **{h['type']}:** {h['msg']}")
    else:
        st.caption("No pipeline stalls detected.")

# TAB 5: TRACE
with tab5:
    st.markdown("### Instruction Execution Trace")
    if state["execution_log"]:
        df_trace = pd.DataFrame(state["execution_log"])
        st.dataframe(df_trace, use_container_width=True, hide_index=True, height=500)
    else:
        st.info("No execution data available.")
'''

# --- EXECUTE BOT COMMITS ---
print("🚀 Initiating Premium Workbench Overhaul...")

bot_commit("pipeline/hazard_detection.py", hazard_code, "refactor(hazards): implement accurate Load-Use vs RAW classification", "core")
bot_commit("core/cpu_controller.py", controller_code, "refactor(core): add structured pipeline schedule and memory trace logging", "core")
bot_commit("visualization/pipeline_chart.py", chart_code, "refactor(viz): upgrade Gantt chart with Plotly Graph Objects and legend cleanup", "core")
bot_commit("app.py", app_code, "feat(ui): complete premium workbench overhaul with design system and 5-tab layout", "ui")

print("✅ Premium Overhaul Complete. Run 'streamlit run app.py' to launch.")