"""
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
