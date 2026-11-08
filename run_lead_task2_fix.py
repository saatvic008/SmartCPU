# run_lead_task2_fix.py
from agent_commit import bot_commit

# --- PAYLOAD: Fixed Pipeline Visualization Module ---
pipeline_chart_code = '''"""
Pipeline Visualization Module
Generates interactive Gantt charts for the 5-stage pipeline using Plotly.
Fixed: Uses horizontal bar chart to properly display integer clock cycles.
"""
import plotly.graph_objects as go
import re

def generate_pipeline_gantt(pipeline_log: list) -> go.Figure:
    """
    Parses the pipeline execution log and generates a Gantt chart.
    Expected log format: "Cycle X: STAGE - Instruction"
    """
    data = []
    
    # Regex to parse the log string
    pattern = r"Cycle (\d+): (IF|ID|EX|MEM|WB|Stall Cycle \d+) - (.+)"
    
    for entry in pipeline_log:
        match = re.search(pattern, entry)
        if match:
            cycle = int(match.group(1))
            stage = match.group(2)
            instruction = match.group(3).strip()
            
            # Handle Stall Cycles specifically
            if "Stall" in stage:
                stage = "STALL"
                
            data.append({
                "instruction": instruction,
                "start": cycle - 1,
                "finish": cycle,
                "stage": stage
            })

    if not data:
        fig = go.Figure()
        fig.update_layout(title="No Pipeline Data Available", template="plotly_dark")
        return fig

    # Color mapping for stages
    color_map = {
        "IF": "#1f77b4",    # Blue
        "ID": "#ff7f0e",    # Orange
        "EX": "#2ca02c",    # Green
        "MEM": "#d62728",   # Red
        "WB": "#9467bd",    # Purple
        "STALL": "#7f7f7f"  # Gray
    }

    # Create horizontal bar chart (Gantt-style)
    fig = go.Figure()

    # Get unique instructions in order
    instructions = list(dict.fromkeys([d["instruction"] for d in data]))
    
    for instr in instructions:
        instr_data = [d for d in data if d["instruction"] == instr]
        for d in instr_data:
            fig.add_trace(go.Bar(
                name=d["stage"],
                y=[instr],
                x=[d["finish"] - d["start"]],  # Duration
                base=[d["start"]],              # Start position
                orientation='h',
                marker_color=color_map.get(d["stage"], "#ffffff"),
                hovertemplate=f"<b>{instr}</b><br>Stage: {d['stage']}<br>Cycle: {d['start']+1} to {d['finish']}<extra></extra>"
            ))

    # Layout configuration
    fig.update_layout(
        title="Instruction Pipeline Execution (Gantt Chart)",
        xaxis_title="Clock Cycles",
        yaxis_title="Instruction",
        template="plotly_dark",
        height=max(300, len(instructions) * 50),
        barmode='overlay',
        showlegend=True,
        legend_title="Pipeline Stage",
        xaxis=dict(
            tickmode='linear',
            tick0=1,
            dtick=1,
            range=[0, max(d["finish"] for d in data) + 1]
        )
    )

    return fig
'''

# Execute Bot Commit
print("Triggering CoreDev Bot to fix Pipeline Visualization...")
bot_commit(
    file_path="visualization/pipeline_chart.py",
    content=pipeline_chart_code,
    commit_message="fix(viz): switch to horizontal bar chart to fix integer clock cycle display",
    bot_type="core"
)

print("Team Lead Task 2 Fix Complete!")