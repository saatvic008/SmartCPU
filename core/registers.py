"""
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
