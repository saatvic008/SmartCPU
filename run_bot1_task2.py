# run_bot1_task2.py
from agent_commit import bot_commit

# --- PAYLOAD: Instruction Parser ---
parser_code = '''"""
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
'''

# Execute Bot 1 Commit
print("Triggering CoreDev Bot for Instruction Parser...")
bot_commit(
    file_path="core/instruction_parser.py",
    content=parser_code,
    commit_message="feat(core): implement InstructionParser for assembly text conversion",
    bot_type="core"
)

print("Bot 1 Task 2 Complete. Check GitHub!")