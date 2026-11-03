# run_srivignesh_hazard_task.py
from agent_commit import bot_commit

# --- PAYLOAD 1: Pipeline Engine ---
pipeline_code = '''"""
Instruction Pipeline Engine
Simulates the classic 5-stage instruction pipeline: IF, ID, EX, MEM, WB.
"""

class PipelineEngine:
    STAGES = ["IF", "ID", "EX", "MEM", "WB"]

    def __init__(self):
        self.reset()

    def reset(self):
        # Tracks which instruction is in which stage at a given cycle
        # Example: self.pipeline_state[0] = "IF" means stage 0 has an instruction
        self.pipeline_state = {stage: None for stage in self.STAGES}
        self.current_cycle = 0
        self.stall_cycles = 0
        self.execution_log = []

    def advance_cycle(self):
        """Moves all instructions one stage forward in the pipeline."""
        self.current_cycle += 1
        
        # Shift stages backwards (WB drops off, MEM goes to WB, etc.)
        new_state = {
            "WB": self.pipeline_state["MEM"],
            "MEM": self.pipeline_state["EX"],
            "EX": self.pipeline_state["ID"],
            "ID": self.pipeline_state["IF"],
            "IF": None # New instruction will be fetched here if not stalled
        }
        self.pipeline_state = new_state

    def fetch_instruction(self, instruction_name: str):
        """Places a new instruction into the IF stage."""
        if self.pipeline_state["IF"] is None:
            self.pipeline_state["IF"] = instruction_name
            self.execution_log.append(f"Cycle {self.current_cycle}: Fetched {instruction_name}")
            return True
        return False # Pipeline bubble or stall

    def get_visualization_data(self) -> list:
        """Returns data formatted for Plotly/Gantt chart visualization."""
        return self.execution_log
'''

# --- PAYLOAD 2: Hazard Detection ---
hazard_code = '''"""
Hazard Detection Module
Detects Data Hazards (RAW), Control Hazards, and Structural Hazards.
"""

class HazardDetector:
    def __init__(self):
        self.stalls = 0
        self.detected_hazards = []

    def check_raw_hazard(self, current_instr: dict, previous_instr: dict) -> bool:
        """
        Checks for Read-After-Write (RAW) data hazards.
        Returns True if a hazard is detected (requires a stall or forwarding).
        """
        if not previous_instr:
            return False

        current_opcode = current_instr.get('opcode', '')
        current_operands = current_instr.get('operands', [])
        
        prev_opcode = previous_instr.get('opcode', '')
        prev_operands = previous_instr.get('operands', [])

        # Identify destination register of previous instruction (usually 1st operand for MOV/ADD)
        prev_dest = prev_operands[0] if len(prev_operands) > 0 else None

        # Identify source registers of current instruction
        current_sources = prev_operands[1:] if len(prev_operands) > 1 else []
        # For simplicity in this basic model, we check if any current operand matches prev_dest
        # A more robust parser would explicitly tag 'src' and 'dest'
        
        for operand in current_operands:
            if operand == prev_dest and prev_dest is not None:
                self.stalls += 1
                hazard_msg = f"RAW Hazard detected: {current_instr['raw']} depends on {previous_instr['raw']}"
                self.detected_hazards.append(hazard_msg)
                print(f"⚠️ {hazard_msg}")
                return True
                
        return False

    def check_control_hazard(self, instruction: dict) -> bool:
        """Checks if a branch/jump instruction causes a control hazard."""
        if instruction.get('opcode') in ['JMP', 'JE', 'JNE', 'CALL']:
            self.stalls += 2 # Simulate 2-cycle branch penalty
            self.detected_hazards.append(f"Control Hazard: Branch instruction {instruction['raw']} flushed pipeline.")
            return True
        return False

    def get_stats(self) -> dict:
        return {
            "total_stalls": self.stalls,
            "hazards": self.detected_hazards
        }
'''

# Execute Commit for Srivignesh's Branch
print("Triggering Pipeline & Hazard setup for Srivignesh...")

# Note: We temporarily override the bot config to commit to the hazards branch
import subprocess
subprocess.run(["git", "checkout", "feature/hazards"], check=True)

bot_commit(
    file_path="pipeline/pipeline_engine.py",
    content=pipeline_code,
    commit_message="feat(pipeline): implement basic 5-stage PipelineEngine tracker",
    bot_type="core"
)

bot_commit(
    file_path="pipeline/hazard_detection.py",
    content=hazard_code,
    commit_message="feat(hazards): implement HazardDetector for RAW and Control hazard detection",
    bot_type="core"
)

print("Srivignesh's Pipeline & Hazard Task Complete!")