# run_bot2_task1.py
from agent_commit import bot_commit

# --- PAYLOAD 1: Streamlit Dashboard ---
app_code = '''"""
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
    value="MOV R1, 10\\nMOV R2, 20\\nADD R3, R1, R2\\nSUB R4, R3, R1\\n# Bot Test"
    
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
'''

# --- PAYLOAD 2: ALU Unit Tests ---
test_alu_code = '''"""
Unit Tests for ALU Module.
"""
import unittest
import sys
import os

# Add parent directory to path to import core modules
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from core.alu import ALU

class TestALU(unittest.TestCase):
    def test_addition(self):
        self.assertEqual(ALU.execute('ADD', 10, 20), 30)
        
    def test_subtraction(self):
        self.assertEqual(ALU.execute('SUB', 30, 10), 20)
        
    def test_bitwise_and(self):
        self.assertEqual(ALU.execute('AND', 0b1010, 0b1100), 0b1000)

if __name__ == '__main__':
    unittest.main()
'''

# --- PAYLOAD 3: Register Unit Tests ---
test_reg_code = '''"""
Unit Tests for Register File Module.
"""
import unittest
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from core.registers import RegisterFile

class TestRegisters(unittest.TestCase):
    def setUp(self):
        self.reg_file = RegisterFile()
        
    def test_initial_values(self):
        self.assertEqual(self.reg_file.read('R0'), 0)
        
    def test_write_and_read(self):
        self.reg_file.write('R1', 42)
        self.assertEqual(self.reg_file.read('R1'), 42)

if __name__ == '__main__':
    unittest.main()
'''

# Execute Bot 2 Commits
print("Triggering UI/Test Bot...")

bot_commit(
    file_path="app.py",
    content=app_code,
    commit_message="feat(ui): implement initial Streamlit dashboard with execution controls",
    bot_type="ui"
)

bot_commit(
    file_path="tests/test_alu.py",
    content=test_alu_code,
    commit_message="test(core): add unit tests for ALU operations",
    bot_type="ui"
)

bot_commit(
    file_path="tests/test_registers.py",
    content=test_reg_code,
    commit_message="test(core): add unit tests for RegisterFile",
    bot_type="ui"
)

print("Bot 2 Task 1 Complete. Check GitHub!")