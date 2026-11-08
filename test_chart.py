# test_chart.py
from visualization.pipeline_chart import generate_pipeline_gantt

mock_log = [
    "Cycle 1: IF - MOV R1, 10",
    "Cycle 2: ID - MOV R1, 10",
    "Cycle 3: EX - MOV R1, 10",
    "Cycle 4: MEM - MOV R1, 10",
    "Cycle 5: WB - MOV R1, 10",
    "Cycle 2: IF - ADD R2, R1, R3",
    "Cycle 3: ID - ADD R2, R1, R3",
    "Cycle 4: EX - ADD R2, R1, R3",
    "Cycle 5: MEM - ADD R2, R1, R3",
    "Cycle 6: WB - ADD R2, R1, R3"
]

fig = generate_pipeline_gantt(mock_log)
fig.write_html("test_pipeline.html")
print("Chart generated! Open test_pipeline.html in your browser.")