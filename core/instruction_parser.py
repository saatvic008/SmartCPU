"""
Instruction Parser Module
Converts raw assembly text into structured dictionaries for the CPU.
"""

class InstructionParser:
    @staticmethod
    def parse(instruction: str) -> dict:
        # Remove comments (anything after #) and clean up whitespace
        instruction = instruction.split('#')[0].strip()
        if not instruction:
            return None

        # Split by comma and space to isolate opcode and operands
        parts = [p.strip() for p in instruction.replace(',', ' ').split()]
        
        opcode = parts[0].upper()
        operands = parts[1:]

        return {
            'opcode': opcode,
            'operands': operands,
            'raw': instruction
        }

    @staticmethod
    def parse_program(program_text: str) -> list:
        """Parses a multiline string of assembly code into a list of instructions."""
        instructions = []
        for line in program_text.splitlines():
            parsed = InstructionParser.parse(line)
            if parsed:
                instructions.append(parsed)
        return instructions
