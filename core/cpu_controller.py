"""
CPU Controller Module
Orchestrates the execution of instructions across all CPU components.
Integrates Registers, ALU, Memory, Pipeline, and Hazard Detection.
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
        self.pipeline_log = []

    def reset(self):
        self.registers.reset()
        self.memory.reset()
        self.pipeline.reset()
        self.hazard_detector = HazardDetector() # Reset stats
        self.execution_log = []
        self.pipeline_log = []

    def execute_program(self, instructions: list):
        """Executes a list of parsed instructions and tracks pipeline stages."""
        self.reset()
        prev_instr = None
        
        for instr in instructions:
            # 1. Check for Hazards
            hazard_result = self.hazard_detector.check_raw_hazard(instr, prev_instr)
            is_control_hazard = self.hazard_detector.check_control_hazard(instr)
            
            # 2. Advance Pipeline (Simulate cycles)
            stalls = 0
            if hazard_result.get("stall", 0) > 0:
                stalls = hazard_result["stall"]
            elif is_control_hazard:
                stalls = 2 # 2-cycle penalty for branch
                
            for _ in range(stalls):
                self.pipeline.advance_cycle()
                self.pipeline_log.append(f"Stall Cycle {self.pipeline.current_cycle}")

            # 3. Fetch
            self.pipeline.advance_cycle()
            self.pipeline.fetch_instruction(instr['raw'])
            self.pipeline_log.append(f"Cycle {self.pipeline.current_cycle}: IF - {instr['raw']}")

            # 4. Functional Execution (Simplified: Execute all stages instantly for UI demo)
            for stage in ["ID", "EX", "MEM", "WB"]:
                self.pipeline.advance_cycle()
                self.pipeline_log.append(f"Cycle {self.pipeline.current_cycle}: {stage} - {instr['raw']}")

            # 5. Actual Logic Execution
            self._execute_instruction(instr)
            
            prev_instr = instr

    def _execute_instruction(self, instr: dict):
        op = instr['opcode']
        ops = instr['operands']
        
        try:
            if op == 'MOV':
                self.registers.write(ops[0], int(ops[1]))
                self.execution_log.append(f"MOV {ops[0]} <- {ops[1]}")
            elif op in ['ADD', 'SUB', 'AND', 'OR', 'XOR']:
                v1 = self.registers.read(ops[1])
                v2 = self.registers.read(ops[2])
                res = self.alu.execute(op, v1, v2)
                self.registers.write(ops[0], res)
                self.execution_log.append(f"{op} {ops[0]} <- {v1} {op} {v2} = {res}")
            elif op == 'STORE':
                val = self.registers.read(ops[0])
                self.memory.write(int(ops[1]), val)
                self.execution_log.append(f"STORE [{ops[1]}] <- {val}")
            elif op == 'LOAD':
                val = self.memory.read(int(ops[1]))
                self.registers.write(ops[0], val)
                self.execution_log.append(f"LOAD {ops[0]} <- [{ops[1]}] = {val}")
        except Exception as e:
            self.execution_log.append(f"Error in {instr['raw']}: {str(e)}")

    def get_state(self):
        return {
            "registers": self.registers.get_all(),
            "cache_stats": self.memory.get_stats(),
            "execution_log": self.execution_log,
            "pipeline_log": self.pipeline_log,
            "hazard_stats": self.hazard_detector.get_stats()
        }