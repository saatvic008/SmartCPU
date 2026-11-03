# run_bot1_task1.py
from agent_commit import bot_commit

# --- PAYLOAD 1: Registers ---
registers_code = '''"""
CPU Register Management Module
Simulates 8 general-purpose registers (R0-R7), PC, and IR.
"""

class RegisterFile:
    def __init__(self):
        self.reset()

    def reset(self):
        # Initialize 8 general-purpose registers to 0
        self.registers = {f"R{i}": 0 for i in range(8)}
        self.pc = 0  # Program Counter
        self.ir = "" # Instruction Register

    def read(self, reg_name: str) -> int:
        reg_name = reg_name.upper()
        if reg_name in self.registers:
            return self.registers[reg_name]
        raise ValueError(f"Invalid register: {reg_name}")

    def write(self, reg_name: str, value: int):
        reg_name = reg_name.upper()
        if reg_name in self.registers:
            self.registers[reg_name] = int(value) & 0xFFFFFFFF  # Simulate 32-bit register
        else:
            raise ValueError(f"Invalid register: {reg_name}")

    def get_all(self) -> dict:
        return self.registers.copy()

    def set_pc(self, address: int):
        self.pc = address

    def get_pc(self) -> int:
        return self.pc
'''

# --- PAYLOAD 2: ALU ---
alu_code = '''"""
Arithmetic Logic Unit (ALU) Module
Performs basic arithmetic and logical operations.
"""

class ALU:
    @staticmethod
    def execute(operation: str, operand1: int, operand2: int) -> int:
        op = operation.upper()
        
        if op == "ADD":
            return operand1 + operand2
        elif op == "SUB":
            return operand1 - operand2
        elif op == "AND":
            return operand1 & operand2
        elif op == "OR":
            return operand1 | operand2
        elif op == "XOR":
            return operand1 ^ operand2
        else:
            raise ValueError(f"Unsupported ALU operation: {operation}")
'''

# Execute Bot 1 Commits
print("Triggering CoreDev Bot...")
bot_commit(
    file_path="core/registers.py",
    content=registers_code,
    commit_message="feat(core): implement RegisterFile class with R0-R7, PC, and IR",
    bot_type="core"
)

bot_commit(
    file_path="core/alu.py",
    content=alu_code,
    commit_message="feat(core): implement ALU class with ADD, SUB, AND, OR, XOR operations",
    bot_type="core"
)

print("Bot 1 Task 1 Complete. Check GitHub!")