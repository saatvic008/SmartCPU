"""
Live Execution Visualization Module - Native Streamlit Version
Uses Streamlit components instead of raw HTML for reliable rendering.
"""
import streamlit as st
import pandas as pd
import time

def get_cycle_state(schedule, cycle):
    """Get all instructions active at a specific cycle."""
    active = []
    for entry in schedule:
        if entry["Start"] < cycle <= entry["Finish"]:
            active.append(entry)
    return active

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
            "EX": f"🟢 **Execute (EX):** The instruction `{instr}` is in the Execute stage. The ALU is performing the required operation.",
            "MEM": f"🔴 **Memory Access (MEM):** The instruction `{instr}` is accessing memory. If this is a LOAD/STORE operation, data is being read from or written to the cache/memory.",
            "WB": f"🟣 **Write Back (WB):** The instruction `{instr}` is writing its result back to the register file. The computed value is being stored in the destination register.",
            "STALL": f"⚫ **Pipeline Stall:** The pipeline is stalled. The CPU is waiting for a dependency to resolve or a hazard to clear. No useful work is done this cycle."
        }
        
        desc = stage_descriptions.get(stage, f"**{stage} Stage:** Processing `{instr}`.")
        
        if stage == "EX" and status == "Forwarded":
            desc += " ⚡ **Data Forwarding Active:** The required operand is being forwarded directly from a previous instruction's result, avoiding a stall."
        
        narration_parts.append(desc)
        narration_parts.append("")
    
    return "\n".join(narration_parts)

def render_cpu_diagram_native(cycle, active_stages, register_values, cache_hits, cache_misses):
    """Render CPU diagram using Streamlit native components."""
    
    active_stage = active_stages[0]["Stage"] if active_stages else None
    
    st.markdown(f"### 🖥️ CPU Microarchitecture - Cycle {cycle}")
    
    # Create the main layout
    col_cpu, col_memory = st.columns([2, 1])
    
    with col_cpu:
        st.markdown("#### **CPU Core**")
        
        # PC and IR row
        pc_col, arrow1, ir_col = st.columns([1, 0.2, 1])
        
        with pc_col:
            pc_color = "🔵" if active_stage == "IF" else "⚪"
            st.markdown(f"**{pc_color} PC (Program Counter)**")
            st.code(f"0x{cycle:04X}", language=None)
        
        with arrow1:
            st.markdown("<div style='text-align:center; font-size:2rem; margin-top:20px;'>→</div>", unsafe_allow_html=True)
        
        with ir_col:
            ir_color = "🟠" if active_stage == "ID" else "⚪"
            st.markdown(f"**{ir_color} IR (Instruction Register)**")
            if active_stages:
                st.code(active_stages[0]["Instruction"][:20], language=None)
            else:
                st.code("IDLE", language=None)
        
        st.markdown("---")
        
        # Decode Unit
        decode_color = "🟡" if active_stage == "ID" else "⚪"
        st.markdown(f"**{decode_color} Decode Unit**")
        st.info("Identifies opcode and operands from instruction")
        
        st.markdown("---")
        
        # ALU and Registers
        alu_col, arrow2, reg_col = st.columns([1, 0.2, 1])
        
        with alu_col:
            alu_color = "🟢" if active_stage == "EX" else "⚪"
            st.markdown(f"**{alu_color} ALU (Arithmetic Logic Unit)**")
            if active_stage == "EX" and active_stages:
                instr = active_stages[0]["Instruction"]
                if "ADD" in instr:
                    st.success("Performing: ADDITION")
                elif "SUB" in instr:
                    st.success("Performing: SUBTRACTION")
                else:
                    st.success("Computing...")
            else:
                st.caption("Idle")
        
        with arrow2:
            st.markdown("<div style='text-align:center; font-size:2rem; margin-top:20px;'>↔</div>", unsafe_allow_html=True)
        
        with reg_col:
            wb_color = "🟣" if active_stage == "WB" else "⚪"
            st.markdown(f"**{wb_color} Register File**")
            st.caption("R0-R7, PC, IR")
            # Show a few key registers
            if register_values:
                reg_preview = {k: register_values[k] for k in list(register_values.keys())[:4]}
                st.json(reg_preview)
    
    with col_memory:
        st.markdown("#### **Memory Hierarchy**")
        
        # Cache
        mem_color = "🔴" if active_stage == "MEM" else "⚪"
        st.markdown(f"**{mem_color} Cache (LRU)**")
        
        total = cache_hits + cache_misses
        hit_ratio = (cache_hits / total * 100) if total > 0 else 0
        
        col_h, col_m, col_r = st.columns(3)
        col_h.metric("Hits", cache_hits)
        col_m.metric("Misses", cache_misses)
        col_r.metric("Ratio", f"{hit_ratio:.0f}%")
        
        st.markdown("---")
        
        # Main Memory
        st.markdown("**⚪ Main Memory (RAM)**")
        st.caption("Address → Value mapping")
    
    # Bus indicators
    st.markdown("---")
    st.markdown("#### **Bus Activity**")
    
    bus_col1, bus_col2, bus_col3 = st.columns(3)
    
    with bus_col1:
        if active_stage == "IF":
            st.error("🔴 **Address Bus:** ACTIVE - Fetching instruction")
        else:
            st.caption("🔴 Address Bus: Idle")
    
    with bus_col2:
        if active_stage in ["EX", "WB", "MEM"]:
            activity = "Writing result" if active_stage == "WB" else "Reading operands" if active_stage == "EX" else "Memory access"
            st.info(f"🔵 **Data Bus:** ACTIVE - {activity}")
        else:
            st.caption("🔵 Data Bus: Idle")
    
    with bus_col3:
        if active_stage == "ID":
            st.warning("🟡 **Control Bus:** ACTIVE - Decoding instruction")
        else:
            st.caption("🟡 Control Bus: Idle")

def render_pipeline_row_native(schedule, current_cycle):
    """Render pipeline state using Streamlit components."""
    if not schedule:
        st.info("No pipeline data available.")
        return
    
    instructions = list(dict.fromkeys([e["Instruction"] for e in schedule]))
    
    st.markdown("#### 📊 Pipeline Activity")
    
    for instr in instructions[:5]:
        instr_entries = [e for e in schedule if e["Instruction"] == instr]
        current_entry = next((e for e in instr_entries if e["Start"] < current_cycle <= e["Finish"]), None)
        
        col_instr, col_stage = st.columns([2, 1])
        
        with col_instr:
            if current_entry:
                stage = current_entry["Stage"]
                status = current_entry.get("Status", "")
                
                stage_emoji = {"IF": "🔵", "ID": "🟠", "EX": "🟢", "MEM": "🔴", "WB": "🟣", "STALL": "⚫"}.get(stage, "⚪")
                
                if status == "Forwarded":
                    st.success(f"{stage_emoji} **{instr}** → {stage} (Forwarded)")
                elif stage == "STALL":
                    st.error(f"{stage_emoji} **{instr}** → {stage}")
                else:
                    st.info(f"{stage_emoji} **{instr}** → {stage}")
            else:
                completed = any(e["Finish"] <= current_cycle for e in instr_entries)
                if completed:
                    st.caption(f"✅ **{instr}** → Completed")
                else:
                    st.caption(f"⏳ **{instr}** → Pending")

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
    
    if 'live_cycle' not in st.session_state:
        st.session_state.live_cycle = 1
    if 'is_playing' not in st.session_state:
        st.session_state.is_playing = False
    
    st.markdown("### 🎬 Live Execution Visualization")
    st.caption("Step through each clock cycle to see exactly what the CPU is doing.")
    
    # Control Panel
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if st.button("⏮ First", use_container_width=True):
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
        play_label = "▶ Auto-Play" if not st.session_state.is_playing else "⏸ Pause"
        play_type = "primary" if not st.session_state.is_playing else "secondary"
        if st.button(play_label, type=play_type, use_container_width=True):
            st.session_state.is_playing = not st.session_state.is_playing
    
    # Cycle Slider
    current_cycle = st.slider(
        "📍 Cycle Position",
        min_value=1,
        max_value=total_cycles,
        value=st.session_state.live_cycle,
        step=1
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
    
    # Main Visualization
    active_stages = get_cycle_state(schedule, current_cycle)
    
    # CPU Diagram (Native Streamlit)
    render_cpu_diagram_native(
        current_cycle,
        active_stages,
        registers,
        cache_stats.get("hits", 0),
        cache_stats.get("misses", 0)
    )
    
    st.markdown("---")
    
    # Detailed Narration
    st.markdown("### 📖 Detailed Execution Narration")
    narration = generate_narration(current_cycle, schedule, execution_log, hazard_stats)
    st.markdown(narration)
    
    st.markdown("---")
    
    # Pipeline Activity
    render_pipeline_row_native(schedule, current_cycle)
    
    st.markdown("---")
    
    # Component Details
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 📋 Register File State")
        if registers:
            reg_df = pd.DataFrame([
                {"Register": k, "Value (Hex)": f"0x{v:08X}", "Value (Dec)": v}
                for k, v in registers.items()
            ])
            st.dataframe(reg_df, use_container_width=True, hide_index=True, height=200)
    
    with col2:
        st.markdown("#### 💾 Cache State")
        if cache_lines:
            cache_df = pd.DataFrame(cache_lines)
            st.dataframe(cache_df, use_container_width=True, hide_index=True, height=200)
        else:
            st.info("Cache not initialized")
    
    # Hazard Flash
    has_hazard = False
    for hazard in hazard_stats.get("hazards", []):
        if f"Cycle {current_cycle}" in hazard.get("msg", "") or current_cycle <= len(hazard_stats.get("hazards", [])) * 2:
            has_hazard = True
            break
    
    if has_hazard:
        st.markdown("---")
        st.error(f"""
        ### 🚨 HAZARD DETECTED AT CYCLE {current_cycle}
        
        **What happened:** The pipeline encountered a hazard requiring special handling.
        
        **Resolution:**
        {chr(10).join([f"- {h['msg']}" for h in hazard_stats.get('hazards', [])[:3]])}
        
        **Impact:** This hazard caused pipeline stalls or required data forwarding.
        """)
    
    # Forwarding Log
    if hazard_stats.get("forwarding_log"):
        st.markdown("#### ⚡ Active Data Forwarding")
        for log in hazard_stats["forwarding_log"][:3]:
            st.success(f"✅ {log}")
