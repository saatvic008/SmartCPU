# agent_commit.py (Fixed Version)
import os
import subprocess
import sys

def bot_commit(file_path, content, commit_message, bot_type="core"):
    """
    Writes content to a file and commits it as a specific bot.
    bot_type: "core" for CoreDev Bot, "ui" for UI/Test Bot
    """
    # 1. Set Bot Identity
    if bot_type == "core":
        bot_name = "CoreDev Bot"
        bot_email = "coredev@smartcpu.local"
    else:
        bot_name = "UI/Test Bot"
        bot_email = "uitest@smartcpu.local"

    print(f"[{bot_name}] Starting autonomous commit process...")

    # 2. Ensure directory exists (FIXED: Only runs if there is a folder path)
    dir_name = os.path.dirname(file_path)
    if dir_name:
        os.makedirs(dir_name, exist_ok=True)

    # 3. Write the file
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"[{bot_name}] Successfully wrote to {file_path}")

    # 4. Execute Git Commands
    try:
        subprocess.run(["git", "config", "user.name", bot_name], check=True)
        subprocess.run(["git", "config", "user.email", bot_email], check=True)
        subprocess.run(["git", "add", file_path], check=True)
        subprocess.run(["git", "commit", "-m", commit_message], check=True)
        
        # Push to current branch
        print(f"[{bot_name}] Pushing to remote repository...")
        subprocess.run(["git", "push"], check=True)
        print(f"[{bot_name}] ✅ Commit and push successful!")
        
    except subprocess.CalledProcessError as e:
        print(f"[{bot_name}] ❌ Git operation failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    print("Agent script loaded. Awaiting task payload...")