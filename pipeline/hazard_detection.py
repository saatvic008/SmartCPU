"""
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
