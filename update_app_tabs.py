# update_app_tabs.py
import subprocess

# Read current app.py
with open("app.py", "r", encoding="utf-8") as f:
    content = f.read()

# Add import for live execution
if "from visualization.live_execution import render_live_execution_tab" not in content:
    content = content.replace(
        "from visualization.pipeline_chart import generate_pipeline_gantt",
        "from visualization.pipeline_chart import generate_pipeline_gantt\nfrom visualization.live_execution import render_live_execution_tab"
    )

# Change tabs to include Live Execution as first tab
content = content.replace(
    'tab1, tab2, tab3, tab4, tab5 = st.tabs(["Overview", "Pipeline", "Memory", "Hazards", "Trace"])',
    'tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(["🎬 Live Execution", "Overview", "Pipeline", "Memory", "Hazards", "Trace"])'
)

# Add Live Execution tab content
live_tab_content = """
with tab1:
    render_live_execution_tab(state)
"""

# Insert after the tabs line
content = content.replace(
    'with tab1:\n    kpi1, kpi2, kpi3, kpi4, kpi5, kpi6 = st.columns(6)',
    live_tab_content + '\nwith tab2:\n    kpi1, kpi2, kpi3, kpi4, kpi5, kpi6 = st.columns(6)'
)

# Update remaining tab references
content = content.replace('with tab2:\n    st.markdown("### Pipeline Execution Timeline")', 'with tab3:\n    st.markdown("### Pipeline Execution Timeline")')
content = content.replace('with tab3:\n    st.markdown("### Cache Hierarchy Statistics")', 'with tab4:\n    st.markdown("### Cache Hierarchy Statistics")')
content = content.replace('with tab4:\n    st.markdown("### Hazard Analysis Center")', 'with tab5:\n    st.markdown("### Hazard Analysis Center")')
content = content.replace('with tab5:\n    st.markdown("### Instruction Execution Trace")', 'with tab6:\n    st.markdown("### Instruction Execution Trace")')

# Write back
with open("app.py", "w", encoding="utf-8") as f:
    f.write(content)

print("✅ app.py updated with Live Execution tab!")

# Commit
subprocess.run(["git", "add", "."])
subprocess.run(["git", "commit", "-m", "feat(ui): add Live Execution tab as first tab with cycle-by-cycle visualization"])
subprocess.run(["git", "push"])
print("✅ Changes pushed to GitHub!")