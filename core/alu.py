"""
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
