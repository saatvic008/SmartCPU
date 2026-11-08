"""
Pipeline Visualization Module - Premium Edition
"""
import plotly.graph_objects as go
import pandas as pd

def generate_pipeline_gantt(schedule: list) -> go.Figure:
    if not schedule:
        fig = go.Figure()
        fig.update_layout(title="No Pipeline Data", template="plotly_dark", height=300)
        return fig

    df = pd.DataFrame(schedule)
    color_map = {"IF": "#1f77b4", "ID": "#ff7f0e", "EX": "#2ca02c", "MEM": "#d62728", "WB": "#9467bd", "STALL": "#7f7f7f"}
    fig = go.Figure()
    instructions = list(dict.fromkeys(df["Instruction"].tolist()))
    
    for instr in instructions:
        instr_data = df[df["Instruction"] == instr]
        for _, row in instr_data.iterrows():
            stage = row["Stage"]
            color = color_map.get(stage, "#ffffff")
            opacity = 0.4 if row["Status"] == "Stall" else 1.0
            fig.add_trace(go.Bar(name=stage, y=[instr], x=[row["Finish"] - row["Start"]], base=[row["Start"]], orientation='h', marker_color=color, opacity=opacity, hovertemplate=f"<b>{instr}</b><br>Stage: {stage}<br>Cycle: {row['Start']} to {row['Finish']}<br>Status: {row['Status']}<extra></extra>"))

    fig.update_layout(title="Pipeline Execution Timeline", xaxis_title="Clock Cycles", yaxis_title="Instructions", template="plotly_dark", height=max(300, len(instructions) * 40 + 50), barmode='overlay', showlegend=True, legend_title="Pipeline Stage", xaxis=dict(tickmode='linear', tick0=1, dtick=1), margin=dict(l=150, r=20, t=40, b=40))
    seen = set()
    for trace in fig.data:
        if trace.name in seen: trace.showlegend = False
        else: seen.add(trace.name)
    return fig
