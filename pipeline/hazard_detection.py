"""
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
