# fix_hazard_text.py
import os

file_path = "pipeline/hazard_detection.py"
with open(file_path, 'r') as f:
    content = f.read()

# Replace the generic "Load-Use" text with logic that checks if it's actually a LOAD
old_code = '''else:
                # Load-Use Hazard: Must stall
                result["stall"] = 1
                self.stalls += 1
                msg = f"Load-Use Hazard: {current_instr['raw']} must wait for {previous_instr['raw']}"
                self.detected_hazards.append(msg)'''

new_code = '''else:
                # Check if it's a real Load-Use or just a RAW hazard
                hazard_type = "Load-Use Hazard" if previous_instr.get('opcode') == 'LOAD' else "RAW Data Hazard"
                result["stall"] = 1
                self.stalls += 1
                msg = f"{hazard_type}: {current_instr['raw']} must wait for {previous_instr['raw']}"
                self.detected_hazards.append(msg)'''

content = content.replace(old_code, new_code)

with open(file_path, 'w') as f:
    f.write(content)

import subprocess
subprocess.run(["git", "add", file_path])
subprocess.run(["git", "commit", "-m", "fix(hazards): correct hazard terminology for MOV vs LOAD"])
subprocess.run(["git", "push"])
print("Hazard text fixed and pushed!")