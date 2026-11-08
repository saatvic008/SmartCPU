# fix_hazard.py
import os

# The correct code for hazard_detection.py
correct_code = '''"""
Hazard Detection Module - Upgraded by Srivignesh
Detects Hazards and implements Data Forwarding (Bypassing) logic.
"""

class HazardDetector:
    def __init__(self):
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
        # We skip the first operand of current_instr because that is the destination register
        for operand in current_operands[1:]: 
            if operand == prev_dest and prev_dest is not None:
                result["hazard"] = True
                
                # DATA FORWARDING LOGIC (Bypassing)
                if previous_instr.get('opcode') in ['ADD', 'SUB', 'AND', 'OR', 'XOR']:
                    result["forward"] = True
                    self.forwarding_count += 1
                    msg = f"Forwarding: {current_instr['raw']} gets data directly from ALU output of {previous_instr['raw']}"
                    self.forwarding_log.append(msg)
                else:
                    # Load-Use Hazard: Must stall
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
        """Checks if a hardware resource is being used by two stages at once."""
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
'''

# Write the file
file_path = "pipeline/hazard_detection.py"
with open(file_path, 'w') as f:
    f.write(correct_code)

print(f"Fixed {file_path} successfully!")

# Now commit it
import subprocess
subprocess.run(["git", "add", file_path])
subprocess.run(["git", "commit", "-m", "fix(hazards): ensure HazardDetector initializes stalls and forwarding counters"])
subprocess.run(["git", "push"])
print("Committed and pushed fix!")