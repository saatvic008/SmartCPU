"""
Pipeline Visualization Module
Generates interactive Gantt charts for the 5-stage pipeline using Plotly.
"""
import plotly.express as px
import pandas as pd
import re

def generate_pipeline_gantt(pipeline_log: list) -> "plotly.graph_objects.Figure":
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
                "Task": instruction,
                "Start": cycle - 1, # 0-indexed for Plotly
                "Finish": cycle,
                "Stage": stage
            })

    if not data:
        # Return an empty figure if no data
        return px.timeline(title="No Pipeline Data Available")

    df = pd.DataFrame(data)
    
    # Color mapping for stages
    color_map = {
        "IF": "#1f77b4",    # Blue
        "ID": "#ff7f0e",    # Orange
        "EX": "#2ca02c",    # Green
        "MEM": "#d62728",   # Red
        "WB": "#9467bd",    # Purple
        "STALL": "#7f7f7f"  # Gray
    }

    fig = px.timeline(
        df, 
        x_start="Start", 
        x_end="Finish", 
        y="Task", 
        color="Stage",
        color_discrete_map=color_map,
        title="Instruction Pipeline Execution (Gantt Chart)",
        labels={"Task": "Instruction", "Stage": "Pipeline Stage"}
    )
    
    fig.update_yaxes(autorange="reversed") # Show first instruction at the top
    fig.update_layout(
        xaxis_title="Clock Cycles",
        template="plotly_dark",
        height=400
    )
    
    return fig
