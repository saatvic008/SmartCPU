"""
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
        self.pipeline_schedule = []
        self.memory_trace = []

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
            hazard_result = self.hazard_detector.check_raw_hazard(instr, prev_instr)
            is_control_hazard = self.hazard_detector.check_control_hazard(instr)
            
            stalls = hazard_result.get("stall", 0)
            if is_control_hazard: stalls += 2
            
            for _ in range(stalls):
                current_cycle += 1
                self.pipeline_schedule.append({
                    "Instruction": instr['raw'], "Stage": "STALL", 
                    "Start": current_cycle, "Finish": current_cycle + 1, "Status": "Stall"
                })

            stages = ["IF", "ID", "EX", "MEM", "WB"]
            
            for i, stage in enumerate(stages):
                current_cycle += 1
                status = "Forwarded" if (stage == "EX" and hazard_result.get("forward")) else "Normal"
                
                self.pipeline_schedule.append({
                    "Instruction": instr['raw'], "Stage": stage,
                    "Start": current_cycle - 1, "Finish": current_cycle, "Status": status
                })

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
                hit = "Hit" if self.memory.cache_hits > 0 else "Miss"
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
