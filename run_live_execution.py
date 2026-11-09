# run_live_execution.py
from agent_commit import bot_commit

# --- LIVE EXECUTION MODULE ---
live_execution_code = '''"""
Live Execution Visualization Module
Provides cycle-by-cycle simulation with detailed narration and CPU diagram.
"""
import streamlit as st
import time

def get_cycle_state(schedule, cycle):
    """Get all instructions active at a specific cycle."""
    active = []
    for entry in schedule:
        if entry["Start"] < cycle <= entry["Finish"]:
            active.append(entry)
    return active

def get_completed_instructions(schedule, cycle):
    """Get instructions that have completed by this cycle."""
    completed = []
    for entry in schedule:
        if entry["Finish"] <= cycle:
            completed.append(entry)
    return completed

def generate_narration(cycle, schedule, execution_log, hazard_stats):
    """Generate detailed plain-English narration for the current cycle."""
    active = get_cycle_state(schedule, cycle)
    
    if not active:
        return "⏸️ **Idle Cycle:** The pipeline is empty. No instructions are being processed at this cycle."
    
    narration_parts = []
    narration_parts.append(f"**📍 Cycle {cycle} Overview:**")
    narration_parts.append("")
    
    for entry in active:
        instr = entry["Instruction"]
        stage = entry["Stage"]
        status = entry.get("Status", "Normal")
        
        stage_descriptions = {
            "IF": f"🔵 **Instruction Fetch (IF):** The instruction `{instr}` is being fetched from memory. The Program Counter (PC) points to this instruction's address, and it's being loaded into the Instruction Register (IR).",
            "ID": f"🟠 **Instruction Decode (ID):** The instruction `{instr}` is being decoded. The control unit is identifying the opcode and operands. Register file is being read to fetch operand values.",
            "EX": f"🟢 **Execute (EX):** The instruction `{instr}` is in the Execute stage. The ALU is performing the required operation. ",
            "MEM": f"🔴 **Memory Access (MEM):** The instruction `{instr}` is accessing memory. If this is a LOAD/STORE operation, data is being read from or written to the cache/memory.",
            "WB": f"🟣 **Write Back (WB):** The instruction `{instr}` is writing its result back to the register file. The computed value is being stored in the destination register.",
            "STALL": f"⚫ **Pipeline Stall:** The pipeline is stalled. The CPU is waiting for a dependency to resolve or a hazard to clear. No useful work is done this cycle."
        }
        
        desc = stage_descriptions.get(stage, f"**{stage} Stage:** Processing `{instr}`.")
        
        # Add specific details for EX stage
        if stage == "EX" and "ADD" in instr:
            desc += "The ALU is performing addition. Once complete, the result will be forwarded or written back."
        elif stage == "EX" and "SUB" in instr:
            desc += "The ALU is performing subtraction."
        elif stage == "EX" and status == "Forwarded":
            desc += "⚡ **Data Forwarding Active:** The required operand is being forwarded directly from a previous instruction's result, avoiding a stall."
        
        narration_parts.append(desc)
        narration_parts.append("")
    
    # Add hazard information if present
    if hazard_stats.get("hazards"):
        narration_parts.append("**⚠️ Hazard Activity:**")
        for hazard in hazard_stats["hazards"]:
            if f"Cycle {cycle}" in hazard.get("msg", "") or cycle <= len(hazard_stats["hazards"]) * 2:
                narration_parts.append(f"- {hazard['msg']}")
    
    return "\\n".join(narration_parts)

def generate_cpu_diagram_html(cycle, active_stages, register_values, cache_hits, cache_misses):
    """Generate HTML/CSS for the CPU component diagram."""
    
    # Determine which components are active
    stage_colors = {
        "IF": "#1f77b4",
        "ID": "#ff7f0e", 
        "EX": "#2ca02c",
        "MEM": "#d62728",
        "WB": "#9467bd",
        "STALL": "#7f7f7f"
    }
    
    active_stage = active_stages[0]["Stage"] if active_stages else None
    active_color = stage_colors.get(active_stage, "#555")
    
    # Calculate hit ratio
    total = cache_hits + cache_misses
    hit_ratio = (cache_hits / total * 100) if total > 0 else 0
    
    html = f"""
    <div style="background: #161b22; border: 2px solid #30363d; border-radius: 12px; padding: 20px; font-family: 'Segoe UI', sans-serif;">
        <h3 style="color: #58a6ff; margin-top: 0; text-align: center;">🖥️ CPU Microarchitecture - Cycle {cycle}</h3>
        
        <div style="display: flex; justify-content: space-between; align-items: stretch; gap: 15px;">
            
            <!-- CPU Section -->
            <div style="flex: 2; background: #0d1117; border: 2px solid {active_color}; border-radius: 8px; padding: 15px; position: relative;">
                <h4 style="color: #c9d1d9; margin-top: 0; text-align: center;">CPU Core</h4>
                
                <!-- PC and IR -->
                <div style="display: flex; justify-content: space-around; margin-bottom: 20px;">
                    <div style="background: {active_color if active_stage == 'IF' else '#21262d'}; border: 2px solid #58a6ff; border-radius: 6px; padding: 10px; text-align: center; min-width: 80px; transition: all 0.3s;">
                        <div style="font-size: 0.7rem; color: #8b949e;">PC</div>
                        <div style="font-family: monospace; font-size: 1.1rem; color: #3fb950;">0x{cycle:04X}</div>
                    </div>
                    <div style="display: flex; align-items: center; color: #8b949e; font-size: 1.5rem;">→</div>
                    <div style="background: {active_color if active_stage == 'ID' else '#21262d'}; border: 2px solid #58a6ff; border-radius: 6px; padding: 10px; text-align: center; min-width: 80px; transition: all 0.3s;">
                        <div style="font-size: 0.7rem; color: #8b949e;">IR</div>
                        <div style="font-family: monospace; font-size: 0.9rem; color: #3fb950;">FETCH</div>
                    </div>
                </div>
                
                <!-- Decode Unit -->
                <div style="background: {active_color if active_stage == 'ID' else '#21262d'}; border: 2px dashed #d29922; border-radius: 6px; padding: 10px; text-align: center; margin-bottom: 20px; transition: all 0.3s;">
                    <div style="font-size: 0.7rem; color: #8b949e;">Decode Unit</div>
                    <div style="font-family: monospace; font-size: 0.9rem; color: #d29922;">OPCODE + OPERANDS</div>
                </div>
                
                <!-- ALU and Registers -->
                <div style="display: flex; justify-content: space-between; align-items: center; gap: 10px;">
                    <div style="background: {active_color if active_stage == 'EX' else '#21262d'}; border: 2px solid #3fb950; border-radius: 6px; padding: 15px; text-align: center; flex: 1; transition: all 0.3s;">
                        <div style="font-size: 0.7rem; color: #8b949e;">ALU</div>
                        <div style="font-family: monospace; font-size: 1rem; color: #3fb950;">COMPUTE</div>
                    </div>
                    
                    <div style="color: #8b949e; font-size: 1.5rem;">↔</div>
                    
                    <div style="background: {active_color if active_stage == 'WB' else '#21262d'}; border: 2px solid #9467bd; border-radius: 6px; padding: 10px; text-align: center; flex: 1; transition: all 0.3s;">
                        <div style="font-size: 0.7rem; color: #8b949e;">Register File</div>
                        <div style="font-family: monospace; font-size: 0.8rem; color: #9467bd;">R0-R7</div>
                        <div style="font-size: 0.7rem; color: #8b949e; margin-top: 5px;">PC, IR</div>
                    </div>
                </div>
            </div>
            
            <!-- Memory Section -->
            <div style="flex: 1; display: flex; flex-direction: column; gap: 15px;">
                <div style="background: {active_color if active_stage == 'MEM' else '#21262d'}; border: 2px solid #d62728; border-radius: 8px; padding: 15px; text-align: center; flex: 1; transition: all 0.3s;">
                    <h4 style="color: #c9d1d9; margin: 0 0 10px 0;">Cache</h4>
                    <div style="font-size: 0.8rem; color: #8b949e;">LRU Policy</div>
                    <div style="margin-top: 10px; font-family: monospace;">
                        <div style="color: #3fb950;">Hits: {cache_hits}</div>
                        <div style="color: #f85149;">Misses: {cache_misses}</div>
                        <div style="color: #58a6ff;">Ratio: {hit_ratio:.1f}%</div>
                    </div>
                </div>
                
                <div style="background: #21262d; border: 2px solid #8b949e; border-radius: 8px; padding: 15px; text-align: center; flex: 1;">
                    <h4 style="color: #c9d1d9; margin: 0 0 10px 0;">Main Memory</h4>
                    <div style="font-size: 0.8rem; color: #8b949e;">RAM</div>
                    <div style="margin-top: 10px; font-family: monospace; font-size: 0.9rem; color: #8b949e;">
                        Address → Value
                    </div>
                </div>
            </div>
        </div>
        
        <!-- Bus Indicators -->
        <div style="margin-top: 15px; padding: 10px; background: #0d1117; border-radius: 6px; font-family: monospace; font-size: 0.85rem;">
            <div style="color: #d62728;">🔴 Address Bus: {"Active - Fetching instruction" if active_stage == 'IF' else "Idle"}</div>
            <div style="color: #1f77b4;">🔵 Data Bus: {"Active - " + ("Writing result" if active_stage == 'WB' else "Reading operands" if active_stage == 'EX' else "Memory access" if active_stage == 'MEM' else "Idle")}</div>
            <div style="color: #d29922;">🟡 Control Bus: {"Active - Decoding instruction" if active_stage == 'ID' else "Idle"}</div>
        </div>
    </div>
    """
    return html

def render_pipeline_row(schedule, current_cycle):
    """Render a visual pipeline row showing current state."""
    if not schedule:
        return "No pipeline data available."
    
    # Get unique instructions
    instructions = list(dict.fromkeys([e["Instruction"] for e in schedule]))
    
    stage_colors = {
        "IF": "🔵", "ID": "🟠", "EX": "🟢", 
        "MEM": "🔴", "WB": "🟣", "STALL": "⚫"
    }
    
    html_parts = ["<div style='background: #161b22; padding: 15px; border-radius: 8px; font-family: monospace;'>"]
    html_parts.append("<div style='color: #8b949e; margin-bottom: 10px;'>Pipeline State at Current Cycle:</div>")
    
    for instr in instructions[:5]:  # Show first 5 instructions
        instr_entries = [e for e in schedule if e["Instruction"] == instr]
        current_entry = next((e for e in instr_entries if e["Start"] < current_cycle <= e["Finish"]), None)
        
        if current_entry:
            stage = current_entry["Stage"]
            color = stage_colors.get(stage, "⚪")
            status = current_entry.get("Status", "")
            highlight = "background: #30363d; padding: 5px; border-radius: 4px;" if status == "Forwarded" else ""
            html_parts.append(f"<div style='margin: 5px 0; {highlight}'>{color} **{instr}** → {stage} {('(Forwarded)' if status == 'Forwarded' else '')}</div>")
        else:
            completed = any(e["Finish"] <= current_cycle for e in instr_entries)
            if completed:
                html_parts.append(f"<div style='margin: 5px 0; opacity: 0.5;'>✅ **{instr}** → Completed</div>")
            else:
                html_parts.append(f"<div style='margin: 5px 0; opacity: 0.3;'>⏳ **{instr}** → Pending</div>")
    
    html_parts.append("</div>")
    return "".join(html_parts)

def render_live_execution_tab(state):
    """Main rendering function for the Live Execution tab."""
    schedule = state.get("pipeline_schedule", [])
    execution_log = state.get("execution_log", [])
    hazard_stats = state.get("hazard_stats", {})
    registers = state.get("registers", {})
    cache_stats = state.get("cache_stats", {})
    cache_lines = state.get("cache_lines", [])
    
    if not schedule:
        st.info("🎬 Run a simulation to see the live execution visualization.")
        return
    
    total_cycles = state.get("total_cycles", 0)
    
    # Initialize session state for cycle control
    if 'live_cycle' not in st.session_state:
        st.session_state.live_cycle = 1
    if 'is_playing' not in st.session_state:
        st.session_state.is_playing = False
    
    st.markdown("### 🎬 Live Execution Visualization")
    st.caption("Step through each clock cycle to see exactly what the CPU is doing.")
    
    # Control Panel
    col1, col2, col3, col4 = st.columns([1, 1, 1, 2])
    
    with col1:
        if st.button("⏮ First Cycle", use_container_width=True):
            st.session_state.live_cycle = 1
            st.rerun()
    
    with col2:
        if st.button("◀ Previous", use_container_width=True):
            if st.session_state.live_cycle > 1:
                st.session_state.live_cycle -= 1
                st.rerun()
    
    with col3:
        if st.button("Next ▶", use_container_width=True):
            if st.session_state.live_cycle < total_cycles:
                st.session_state.live_cycle += 1
                st.rerun()
    
    with col4:
        play = st.button("▶ Auto-Play" if not st.session_state.is_playing else "⏸ Pause", 
                        type="primary" if not st.session_state.is_playing else "secondary",
                        use_container_width=True)
        if play:
            st.session_state.is_playing = not st.session_state.is_playing
    
    # Cycle Slider
    current_cycle = st.slider(
        "📍 Cycle Position",
        min_value=1,
        max_value=total_cycles,
        value=st.session_state.live_cycle,
        step=1,
        help="Drag to move through cycles"
    )
    st.session_state.live_cycle = current_cycle
    
    # Auto-play logic
    if st.session_state.is_playing:
        if current_cycle < total_cycles:
            time.sleep(0.8)
            st.session_state.live_cycle = current_cycle + 1
            st.rerun()
        else:
            st.session_state.is_playing = False
            st.success("✅ Simulation complete!")
    
    # Main Visualization Area
    active_stages = get_cycle_state(schedule, current_cycle)
    
    # CPU Diagram
    st.markdown("### 🖥️ CPU Component State")
    cpu_html = generate_cpu_diagram_html(
        current_cycle, 
        active_stages, 
        registers,
        cache_stats.get("hits", 0),
        cache_stats.get("misses", 0)
    )
    st.markdown(cpu_html, unsafe_allow_html=True)
    
    # Detailed Narration
    st.markdown("### 📖 Detailed Execution Narration")
    narration = generate_narration(current_cycle, schedule, execution_log, hazard_stats)
    st.markdown(narration)
    
    # Pipeline Row Visualization
    st.markdown("### 📊 Pipeline Activity")
    pipeline_html = render_pipeline_row(schedule, current_cycle)
    st.markdown(pipeline_html, unsafe_allow_html=True)
    
    # Component Details
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 📋 Register File State")
        reg_df = __import__('pandas').DataFrame([
            {"Register": k, "Value (Hex)": f"0x{v:08X}", "Value (Dec)": v} 
            for k, v in registers.items()
        ])
        st.dataframe(reg_df, use_container_width=True, hide_index=True, height=200)
    
    with col2:
        st.markdown("#### 💾 Cache State")
        if cache_lines:
            cache_df = __import__('pandas').DataFrame(cache_lines)
            st.dataframe(cache_df, use_container_width=True, hide_index=True, height=200)
        else:
            st.info("Cache not initialized")
    
    # Hazard Flash Effect
    has_hazard_at_cycle = False
    for hazard in hazard_stats.get("hazards", []):
        if f"Cycle {current_cycle}" in hazard.get("msg", "") or current_cycle <= len(hazard_stats.get("hazards", [])) * 2:
            has_hazard_at_cycle = True
            break
    
    if has_hazard_at_cycle:
        st.error(f"""
        ### 🚨 HAZARD DETECTED AT CYCLE {current_cycle}
        
        **What happened:** The pipeline encountered a hazard that required special handling.
        
        **Resolution:** 
        {chr(10).join([f"- {h['msg']}" for h in hazard_stats.get('hazards', [])[:3]])}
        
        **Impact:** This hazard caused pipeline stalls or required data forwarding to resolve.
        """)
    
    # Forwarding Log
    if hazard_stats.get("forwarding_log"):
        st.markdown("#### ⚡ Active Data Forwarding")
        for log in hazard_stats["forwarding_log"][:3]:
            st.success(f"✅ {log}")
'''

print("🎬 Creating Live Execution Module...")
bot_commit(
    file_path="visualization/live_execution.py",
    content=live_execution_code,
    commit_message="feat(viz): add live execution visualization with cycle-by-cycle narration and CPU diagram",
    bot_type="core"
)
print("✅ Live Execution Module Created!")