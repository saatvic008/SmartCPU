"""
CPU Controller Module - Premium Edition
Executes instructions and builds an overlapped five-stage pipeline timeline.

Note: The register/ALU/memory model remains sequential for compatibility with
this project. The pipeline schedule models stage overlap and basic penalties.
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
        """Execute the program and create an overlapped IF-ID-EX-MEM-WB schedule."""
        self.reset()
        previous_instr = None
        next_fetch_cycle = 1  # 1-based clock cycle for the first instruction
        stages = ["IF", "ID", "EX", "MEM", "WB"]

        for instr in instructions:
            hazard = self.hazard_detector.check_raw_hazard(instr, previous_instr)
            is_control = self.hazard_detector.check_control_hazard(instr)
            load_stall = int(hazard.get("stall", 0))
            control_penalty = 2 if is_control else 0

            # The current instruction advances through the pipeline. A load-use
            # bubble is inserted between ID and EX; following fetches are delayed.
            cycle = next_fetch_cycle
            for stage in stages:
                if stage == "EX" and load_stall:
                    self.pipeline_schedule.append({
                        "Instruction": instr["raw"], "Stage": "STALL",
                        "Start": cycle - 1, "Finish": cycle,
                        "Status": "Stall"
                    })
                    cycle += load_stall

                status = "Forwarded" if (stage == "EX" and hazard.get("forward")) else "Normal"
                self.pipeline_schedule.append({
                    "Instruction": instr["raw"], "Stage": stage,
                    "Start": cycle - 1, "Finish": cycle, "Status": status
                })
                cycle += 1

            # Execute the existing functional CPU model and log completion at WB.
            wb_cycle = cycle - 1
            self._execute_instruction(instr, wb_cycle)

            # Normally one new instruction is fetched per cycle. A load-use stall
            # holds fetch for one cycle; a control hazard applies a two-cycle penalty
            # to subsequent fetches in this simplified model.
            next_fetch_cycle += 1 + load_stall + control_penalty
            previous_instr = instr

    def _execute_instruction(self, instr: dict, cycle: int):
        op = instr['opcode']
        ops = instr['operands']
        log_entry = {"Cycle": cycle, "PC": cycle - 1, "Instruction": instr['raw'], "Op": op, "Result": "-"}

        try:
            if op == 'MOV':
                val = int(ops[1])
                self.registers.write(ops[0], val)
                log_entry["Result"] = f"{ops[0]} <- {val}"
            elif op in ['ADD', 'SUB', 'AND', 'OR', 'XOR']:
                v1 = self.registers.read(ops[1])
                v2 = self.registers.read(ops[2])
                res = self.alu.execute(op, v1, v2)
                self.registers.write(ops[0], res)
                log_entry["Result"] = f"{ops[0]} <- {res}"
            elif op == 'STORE':
                val = self.registers.read(ops[0])
                self.memory.write(int(ops[1]), val)
                log_entry["Result"] = f"MEM[{ops[1]}] <- {val}"
                self.memory_trace.append({"Cycle": cycle, "Instr": instr['raw'], "Addr": ops[1], "Value": val, "Type": "STORE", "Cache": "Write-Through"})
            elif op == 'LOAD':
                val = self.memory.read(int(ops[1]))
                self.registers.write(ops[0], val)
                log_entry["Result"] = f"{ops[0]} <- {val}"
                hit = "Hit" if self.memory.cache_hits > 0 else "Miss"
                self.memory_trace.append({"Cycle": cycle, "Instr": instr['raw'], "Addr": ops[1], "Value": val, "Type": "LOAD", "Cache": hit})
        except Exception as exc:
            log_entry["Result"] = f"Error: {str(exc)}"

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
