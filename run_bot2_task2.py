# run_bot2_task2.py
from agent_commit import bot_commit

# --- PAYLOAD: Upgraded Streamlit Dashboard ---
app_v2_code = '''"""
SmartCPU Interactive Dashboard - Version 2
Integrates Memory, Cache, and improved UI.
"""
import streamlit as st
from core.registers import RegisterFile
from core.alu import ALU
from core.instruction_parser import InstructionParser
from core.memory import MemorySystem

st.set_page_config(page_title="SmartCPU Simulator", layout="wide", page_icon="🖥️")
st.title("🖥️ SmartCPU - Interactive Architecture Simulator")

# Initialize Session State
if 'registers' not in st.session_state:
    st.session_state.registers = RegisterFile()
if 'memory' not in st.session_state:
    st.session_state.memory = MemorySystem()

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
    st.session_state.registers.reset()
    st.session_state.memory.reset()
    st.rerun()

# Execution Engine
if run_btn:
    st.session_state.registers.reset()
    st.session_state.memory.reset()
    
    parser = InstructionParser()
    alu = ALU()
    instructions = parser.parse_program(assembly_code)
    
    execution_log = []
    for instr in instructions:
        op = instr['opcode']
        ops = instr['operands']
        try:
            if op == 'MOV':
                st.session_state.registers.write(ops[0], int(ops[1]))
                execution_log.append(f"Executed: {instr['raw']}")
            elif op in ['ADD', 'SUB', 'AND', 'OR', 'XOR']:
                v1 = st.session_state.registers.read(ops[1])
                v2 = st.session_state.registers.read(ops[2])
                res = alu.execute(op, v1, v2)
                st.session_state.registers.write(ops[0], res)
                execution_log.append(f"Executed: {instr['raw']} -> Result: {res}")
            elif op == 'STORE':
                val = st.session_state.registers.read(ops[0])
                st.session_state.memory.write(int(ops[1]), val)
                execution_log.append(f"Executed: {instr['raw']} (Memory Write)")
            elif op == 'LOAD':
                val = st.session_state.memory.read(int(ops[1]))
                st.session_state.registers.write(ops[0], val)
                execution_log.append(f"Executed: {instr['raw']} -> Loaded: {val}")
        except Exception as e:
            execution_log.append(f"Error in {instr['raw']}: {str(e)}")

# Main Dashboard Layout
col1, col2, col3 = st.columns(3)

with col1:
    st.subheader("📊 CPU Registers")
    reg_data = st.session_state.registers.get_all()
    st.json(reg_data)

with col2:
    st.subheader("💾 Cache Memory Stats")
    cache_stats = st.session_state.memory.get_stats()
    st.metric(label="Cache Hits", value=cache_stats['hits'])
    st.metric(label="Cache Misses", value=cache_stats['misses'])
    st.metric(label="Hit Ratio", value=f"{cache_stats['hit_ratio']}%")

with col3:
    st.subheader("📝 Execution Log")
    if run_btn:
        for log in execution_log:
            st.text(log)
'''

# Execute Bot 2 Commit
print("Triggering UI/Test Bot for Dashboard V2...")
bot_commit(
    file_path="app.py",
    content=app_v2_code,
    commit_message="feat(ui): upgrade dashboard to V2 with Cache stats and Memory integration",
    bot_type="ui"
)

print("Bot 2 Task 2 Complete. Check GitHub!")