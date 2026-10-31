"""
SmartCPU Interactive Dashboard
Built with Streamlit.
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
    value="MOV R1, 10\nMOV R2, 20\nADD R3, R1, R2\nSUB R4, R3, R1"
)

col1, col2 = st.sidebar.columns(2)
run_btn = col1.button("▶️ Execute All", type="primary")
reset_btn = col2.button("🔄 Reset CPU")

if reset_btn:
    st.session_state.registers.reset()
    st.session_state.memory.reset()
    st.rerun()

# Execution Engine (Simplified for UI Demo)
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
            elif op == 'ADD':
                v1 = st.session_state.registers.read(ops[1])
                v2 = st.session_state.registers.read(ops[2])
                res = alu.execute('ADD', v1, v2)
                st.session_state.registers.write(ops[0], res)
                execution_log.append(f"Executed: {instr['raw']} -> Result: {res}")
            elif op == 'SUB':
                v1 = st.session_state.registers.read(ops[1])
                v2 = st.session_state.registers.read(ops[2])
                res = alu.execute('SUB', v1, v2)
                st.session_state.registers.write(ops[0], res)
                execution_log.append(f"Executed: {instr['raw']} -> Result: {res}")
        except Exception as e:
            execution_log.append(f"Error in {instr['raw']}: {str(e)}")

# Main Dashboard Layout
st.subheader("📊 CPU Registers")
reg_data = st.session_state.registers.get_all()
st.json(reg_data)

st.subheader("📝 Execution Log")
if run_btn:
    for log in execution_log:
        st.text(log)
