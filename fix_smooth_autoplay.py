# fix_smooth_autoplay.py
import subprocess

smooth_code = '''"""
Live Execution Visualization Module - Smooth Auto-Play Version
Uses st.empty() placeholders for in-place updates without full script reruns.
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
    
    return "\\n".join(narration_parts)

def render_live_execution_tab(state):
    """Main rendering function for the Live Execution tab with smooth auto-play."""
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
    
    st.markdown("### 🎬 Live Execution Visualization")
    st.caption("Step through each clock cycle to see exactly what the CPU is doing.")
    
    # Speed control
    speed_col1, speed_col2 = st.columns([1, 3])
    with speed_col1:
        speed = st.selectbox("⚡ Playback Speed", ["0.5x (Slow)", "1x (Normal)", "2x (Fast)", "4x (Very Fast)"], index=1)
    
    speed_map = {"0.5x (Slow)": 1.5, "1x (Normal)": 0.8, "2x (Fast)": 0.4, "4x (Very Fast)": 0.2}
    delay = speed_map[speed]
    
    # Control buttons
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
        play_label = "▶ Auto-Play" if not st.session_state.get("is_playing", False) else "⏸ Pause"
        play_type = "primary" if not st.session_state.get("is_playing", False) else "secondary"
        if st.button(play_label, type=play_type, use_container_width=True):
            st.session_state.is_playing = not st.session_state.get("is_playing", False)
            st.rerun()
    
    # Initialize cycle if needed
    if 'live_cycle' not in st.session_state:
        st.session_state.live_cycle = 1
    
    # Create empty placeholders for smooth updates
    progress_placeholder = st.empty()
    cpu_placeholder = st.empty()
    narration_placeholder = st.empty()
    pipeline_placeholder = st.empty()
    components_placeholder = st.empty()
    hazard_placeholder = st.empty()
    
    # Auto-play loop
    if st.session_state.get("is_playing", False):
        for cycle in range(st.session_state.live_cycle, total_cycles + 1):
            st.session_state.live_cycle = cycle
            
            # Update progress
            progress_placeholder.progress(cycle / total_cycles, text=f"📍 Cycle {cycle} of {total_cycles}")
            
            # Get current state
            active_stages = get_cycle_state(schedule, cycle)
            
            # Update CPU diagram
            active_stage = active_stages[0]["Stage"] if active_stages else None
            
            with cpu_placeholder.container():
                st.markdown(f"### 🖥️ CPU Microarchitecture - Cycle {cycle}")
                
                col_cpu, col_memory = st.columns([2, 1])
                
                with col_cpu:
                    st.markdown("#### **CPU Core**")
                    
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
                    
                    decode_color = "🟡" if active_stage == "ID" else "⚪"
                    st.markdown(f"**{decode_color} Decode Unit**")
                    st.info("Identifies opcode and operands from instruction")
                    
                    st.markdown("---")
                    
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
                        if registers:
                            reg_preview = {k: registers[k] for k in list(registers.keys())[:4]}
                            st.json(reg_preview)
                
                with col_memory:
                    st.markdown("#### **Memory Hierarchy**")
                    
                    mem_color = "🔴" if active_stage == "MEM" else "⚪"
                    st.markdown(f"**{mem_color} Cache (LRU)**")
                    
                    total_accesses = cache_stats.get("hits", 0) + cache_stats.get("misses", 0)
                    hit_ratio = (cache_stats.get("hits", 0) / total_accesses * 100) if total_accesses > 0 else 0
                    
                    col_h, col_m, col_r = st.columns(3)
                    col_h.metric("Hits", cache_stats.get("hits", 0))
                    col_m.metric("Misses", cache_stats.get("misses", 0))
                    col_r.metric("Ratio", f"{hit_ratio:.0f}%")
                    
                    st.markdown("---")
                    
                    st.markdown("**⚪ Main Memory (RAM)**")
                    st.caption("Address → Value mapping")
                
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
            
            # Update narration
            narration = generate_narration(cycle, schedule, execution_log, hazard_stats)
            narration_placeholder.markdown("### 📖 Detailed Execution Narration")
            narration_placeholder.markdown(narration)
            
            # Update pipeline
            instructions = list(dict.fromkeys([e["Instruction"] for e in schedule]))
            pipeline_placeholder.markdown("### 📊 Pipeline Activity")
            
            with pipeline_placeholder.container():
                for instr in instructions[:5]:
                    instr_entries = [e for e in schedule if e["Instruction"] == instr]
                    current_entry = next((e for e in instr_entries if e["Start"] < cycle <= e["Finish"]), None)
                    
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
                        completed = any(e["Finish"] <= cycle for e in instr_entries)
                        if completed:
                            st.caption(f"✅ **{instr}** → Completed")
                        else:
                            st.caption(f"⏳ **{instr}** → Pending")
            
            # Update components
            col1, col2 = components_placeholder.columns(2)
            
            with col1:
                st.markdown("#### 📋 Register File State")
                if registers:
                    reg_df = pd.DataFrame([
                        {"Register": k, "Value (Hex)": f"0x{v:08X}", "Value (Dec)": v}
                        for k, v in registers.items()
                    ])
                    st.dataframe(reg_df, use_container_width=True, hide_index=True, height=150)
            
            with col2:
                st.markdown("#### 💾 Cache State")
                if cache_lines:
                    cache_df = pd.DataFrame(cache_lines)
                    st.dataframe(cache_df, use_container_width=True, hide_index=True, height=150)
                else:
                    st.info("Cache not initialized")
            
            # Update hazards
            has_hazard = False
            for hazard in hazard_stats.get("hazards", []):
                if f"Cycle {cycle}" in hazard.get("msg", "") or cycle <= len(hazard_stats.get("hazards", [])) * 2:
                    has_hazard = True
                    break
            
            if has_hazard:
                hazard_placeholder.error(f"""
                ### 🚨 HAZARD DETECTED AT CYCLE {cycle}
                
                **What happened:** The pipeline encountered a hazard requiring special handling.
                
                **Resolution:**
                {chr(10).join([f"- {h['msg']}" for h in hazard_stats.get('hazards', [])[:3]])}
                
                **Impact:** This hazard caused pipeline stalls or required data forwarding.
                """)
            else:
                hazard_placeholder.empty()
            
            # Check if pause was requested
            if not st.session_state.get("is_playing", False):
                break
            
            time.sleep(delay)
        
        # Auto-play finished
        st.session_state.is_playing = False
        progress_placeholder.success("✅ Simulation complete!")
    
    else:
        # Manual mode - show current cycle
        current_cycle = st.session_state.live_cycle
        
        progress_placeholder.progress(current_cycle / total_cycles, text=f"📍 Cycle {current_cycle} of {total_cycles}")
        
        active_stages = get_cycle_state(schedule, current_cycle)
        active_stage = active_stages[0]["Stage"] if active_stages else None
        
        with cpu_placeholder.container():
            st.markdown(f"### 🖥️ CPU Microarchitecture - Cycle {current_cycle}")
            
            col_cpu, col_memory = st.columns([2, 1])
            
            with col_cpu:
                st.markdown("#### **CPU Core**")
                
                pc_col, arrow1, ir_col = st.columns([1, 0.2, 1])
                
                with pc_col:
                    pc_color = "🔵" if active_stage == "IF" else "⚪"
                    st.markdown(f"**{pc_color} PC (Program Counter)**")
                    st.code(f"0x{current_cycle:04X}", language=None)
                
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
                
                decode_color = "🟡" if active_stage == "ID" else "⚪"
                st.markdown(f"**{decode_color} Decode Unit**")
                st.info("Identifies opcode and operands from instruction")
                
                st.markdown("---")
                
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
                    if registers:
                        reg_preview = {k: registers[k] for k in list(registers.keys())[:4]}
                        st.json(reg_preview)
            
            with col_memory:
                st.markdown("#### **Memory Hierarchy**")
                
                mem_color = "🔴" if active_stage == "MEM" else "⚪"
                st.markdown(f"**{mem_color} Cache (LRU)**")
                
                total_accesses = cache_stats.get("hits", 0) + cache_stats.get("misses", 0)
                hit_ratio = (cache_stats.get("hits", 0) / total_accesses * 100) if total_accesses > 0 else 0
                
                col_h, col_m, col_r = st.columns(3)
                col_h.metric("Hits", cache_stats.get("hits", 0))
                col_m.metric("Misses", cache_stats.get("misses", 0))
                col_r.metric("Ratio", f"{hit_ratio:.0f}%")
                
                st.markdown("---")
                
                st.markdown("**⚪ Main Memory (RAM)**")
                st.caption("Address → Value mapping")
            
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
        
        narration = generate_narration(current_cycle, schedule, execution_log, hazard_stats)
        narration_placeholder.markdown("### 📖 Detailed Execution Narration")
        narration_placeholder.markdown(narration)
        
        instructions = list(dict.fromkeys([e["Instruction"] for e in schedule]))
        pipeline_placeholder.markdown("### 📊 Pipeline Activity")
        
        with pipeline_placeholder.container():
            for instr in instructions[:5]:
                instr_entries = [e for e in schedule if e["Instruction"] == instr]
                current_entry = next((e for e in instr_entries if e["Start"] < current_cycle <= e["Finish"]), None)
                
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
        
        col1, col2 = components_placeholder.columns(2)
        
        with col1:
            st.markdown("#### 📋 Register File State")
            if registers:
                reg_df = pd.DataFrame([
                    {"Register": k, "Value (Hex)": f"0x{v:08X}", "Value (Dec)": v}
                    for k, v in registers.items()
                ])
                st.dataframe(reg_df, use_container_width=True, hide_index=True, height=150)
        
        with col2:
            st.markdown("#### 💾 Cache State")
            if cache_lines:
                cache_df = pd.DataFrame(cache_lines)
                st.dataframe(cache_df, use_container_width=True, hide_index=True, height=150)
            else:
                st.info("Cache not initialized")
        
        has_hazard = False
        for hazard in hazard_stats.get("hazards", []):
            if f"Cycle {current_cycle}" in hazard.get("msg", "") or current_cycle <= len(hazard_stats.get("hazards", [])) * 2:
                has_hazard = True
                break
        
        if has_hazard:
            hazard_placeholder.error(f"""
            ### 🚨 HAZARD DETECTED AT CYCLE {current_cycle}
            
            **What happened:** The pipeline encountered a hazard requiring special handling.
            
            **Resolution:**
            {chr(10).join([f"- {h['msg']}" for h in hazard_stats.get('hazards', [])[:3]])}
            
            **Impact:** This hazard caused pipeline stalls or required data forwarding.
            """)
        else:
            hazard_placeholder.empty()
'''

# Write the file
with open("visualization/live_execution.py", "w", encoding="utf-8") as f:
    f.write(smooth_code)

print("✅ Replaced live_execution.py with smooth auto-play version!")

# Commit
subprocess.run(["git", "add", "visualization/live_execution.py"])
subprocess.run(["git", "commit", "-m", "feat(viz): implement smooth auto-play with st.empty() placeholders and speed control"])
subprocess.run(["git", "push"])
print("✅ Fix committed and pushed!")