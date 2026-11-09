# fix_live_execution.py
import subprocess

# Read the current live_execution.py
with open("visualization/live_execution.py", "r", encoding="utf-8") as f:
    content = f.read()

# Add the components import at the top
if "import streamlit.components.v1 as components" not in content:
    content = content.replace(
        "import streamlit as st",
        "import streamlit as st\nimport streamlit.components.v1 as components"
    )

# Replace st.markdown(cpu_html, unsafe_allow_html=True) with components.html()
content = content.replace(
    "st.markdown(cpu_html, unsafe_allow_html=True)",
    "components.html(cpu_html, height=500, scrolling=False)"
)

# Also fix the pipeline HTML rendering
content = content.replace(
    "st.markdown(pipeline_html, unsafe_allow_html=True)",
    "st.markdown(pipeline_html, unsafe_allow_html=True)"  # Keep this one as is
)

# Write back
with open("visualization/live_execution.py", "w", encoding="utf-8") as f:
    f.write(content)

print("✅ Fixed live_execution.py to use components.html()")

# Commit the fix
subprocess.run(["git", "add", "visualization/live_execution.py"])
subprocess.run(["git", "commit", "-m", "fix(viz): use components.html() for proper HTML rendering in live execution"])
subprocess.run(["git", "push"])
print("✅ Fix committed and pushed!")