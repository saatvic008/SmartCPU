"""
Hazard Detection Module - Upgraded by Srivignesh
Detects Hazards and implements Data Forwarding (Bypassing) logic.
"""

class HazardDetector:
    def _init_(self):
        self.stalls = 0
        self.forwarding_count = 0
        self.detected_hazards = []
        self.forwarding_log = []

    def check_raw_hazard(self, current_instr: dict, previous_instr: dict) -> dict:
        """
        Checks for Read-After-Write (RAW) data hazards.
        Returns a dict indicating if a stall is needed or if forwarding can be used.
        """
        result = {"hazard": False, "stall": 0, "forward": False}
        
        if not previous_instr:
            return result

        current_operands = current_instr.get('operands', [])
        prev_operands = previous_instr.get('operands', [])
        prev_dest = prev_operands[0] if len(prev_operands) > 0 else None

        # Check if current instruction reads from the previous instruction's destination
        for operand in current_operands[1:]: # Skip destination register of current instr
            if operand == prev_dest and prev_dest is not None:
                result["hazard"] = True
                
                # DATA FORWARDING LOGIC (Bypassing)
                # If the previous instruction was an ALU operation (ADD, SUB, etc.), 
                # we can forward the result directly to the EX stage of the current instruction.
                if previous_instr.get('opcode') in ['ADD', 'SUB', 'AND', 'OR', 'XOR']:
                    result["forward"] = True
                    self.forwarding_count += 1
                    msg = f"Forwarding: {current_instr['raw']} gets data directly from ALU output of {previous_instr['raw']}"
                    self.forwarding_log.append(msg)
                else:
                    # If it was a LOAD instruction, we MUST stall for 1 cycle (Load-Use Hazard)
                    result["stall"] = 1
                    self.stalls += 1
                    msg = f"Load-Use Hazard: {current_instr['raw']} must wait for {previous_instr['raw']}"
                    self.detected_hazards.append(msg)
                    
        return result

    def check_control_hazard(self, instruction: dict) -> bool:
        """Checks if a branch/jump instruction causes a control hazard."""
        if instruction.get('opcode') in ['JMP', 'JE', 'JNE', 'CALL']:
            self.stalls += 2 # Simulate 2-cycle branch penalty
            self.detected_hazards.append(f"Control Hazard: Branch {instruction['raw']} flushed pipeline.")
            return True
        return False

    def check_structural_hazard(self, resource_in_use: bool) -> bool:
        """Checks if a hardware resource (like memory) is being used by two stages at once."""
        if resource_in_use:
            self.stalls += 1
            self.detected_hazards.append("Structural Hazard: Resource conflict detected.")
            return True
        return False

    def get_stats(self) -> dict:
        return {
            "total_stalls": self.stalls,
            "data_forwarding_count": self.forwarding_count,
            "hazards": self.detected_hazards,
            "forwarding_log": self.forwarding_log
        }