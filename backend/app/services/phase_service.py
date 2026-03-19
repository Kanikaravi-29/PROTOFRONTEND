from app.ai.graph import app_graph
from app.core.config import supabase_client
from typing import Dict

def enforce_phase_order(project_id: str, phase_name: str):
    if phase_name == "morphological_chart":
        prev = supabase_client.table("project_phases").select("*").eq("project_id", project_id).eq("phase_name", "functional_decomposition").execute()
        if not prev.data or (not prev.data[0].get("human_approved_data") and not prev.data[0].get("ai_generated_data")):
            raise ValueError("Phase 1 must be completed (AI generated) before proceeding to Phase 2.")
    elif phase_name == "risk_analysis":
        prev = supabase_client.table("project_phases").select("*").eq("project_id", project_id).eq("phase_name", "morphological_chart").execute()
        if not prev.data or (not prev.data[0].get("human_approved_data") and not prev.data[0].get("ai_generated_data")):
            raise ValueError("Phase 2 must be completed (AI generated) before proceeding to Phase 3.")

def start_phase_graph(project_id: str, phase_name: str, problem_statement: str):
    enforce_phase_order(project_id, phase_name)
    config = {"configurable": {"thread_id": project_id}}
    
    current_state = app_graph.get_state(config)
    initial_input = {
        "project_id": project_id,
        "problem_statement": problem_statement,
        "current_phase": phase_name,
        "revision_count": 0,
        "validation_feedback": ""
    }

    # If memory is empty, try to restore context from database
    if not current_state.values:
        # Restore Phase 1 if we're in Phase 2 or 3
        if phase_name in ["morphological_chart", "risk_analysis"]:
            res = supabase_client.table("project_phases").select("*").eq("project_id", project_id).eq("phase_name", "functional_decomposition").execute()
            if res.data:
                p1_data = res.data[0].get("human_approved_data") or res.data[0].get("ai_generated_data")
                if p1_data:
                    initial_input["functional_tree"] = p1_data

        # Restore Phase 2 if we're in Phase 3
        if phase_name == "risk_analysis":
            res = supabase_client.table("project_phases").select("*").eq("project_id", project_id).eq("phase_name", "morphological_chart").execute()
            if res.data:
                p2_data = res.data[0].get("human_approved_data") or res.data[0].get("ai_generated_data")
                if p2_data:
                    initial_input["morphological_alternatives"] = p2_data
    
    # Run the graph until the interrupt breakpoint
    for _ in app_graph.stream(initial_input, config, stream_mode="values"):
        pass

    final_state = app_graph.get_state(config).values
    
    # Parse final state
    ai_data = {}
    if phase_name == "functional_decomposition":
        ai_data = final_state.get("functional_tree", {})
    elif phase_name == "morphological_chart":
        ai_data = final_state.get("morphological_alternatives", {})
    elif phase_name == "risk_analysis":
        ai_data = final_state.get("risk_checklist", {})
        
    status = "human_review"
    if final_state.get("validation_feedback"):
        if final_state.get("revision_count", 0) >= 3:
            status = "validation_failed"
        else:
            status = "pending"
    elif phase_name == "risk_analysis":
        status = "completed"

    # Upsert phase record
    supabase_client.table("project_phases").upsert({
        "project_id": project_id,
        "phase_name": phase_name,
        "ai_generated_data": ai_data,
        "status": status
    }, on_conflict="project_id, phase_name").execute()

    return {"state": final_state, "status": status}

def update_phase_human_data(project_id: str, phase_name: str, human_data: Dict):
    config = {"configurable": {"thread_id": project_id}}
    
    # Update LangGraph state manually
    state_updates = {}
    if phase_name == "functional_decomposition":
        state_updates = {"functional_tree": human_data}
    elif phase_name == "morphological_chart":
        state_updates = {"morphological_alternatives": human_data}
    elif phase_name == "risk_analysis":
        state_updates = {"risk_checklist": human_data}
        
    app_graph.update_state(config, state_updates)
    
    # Update Database
    supabase_client.table("project_phases").update({
        "human_approved_data": human_data,
        "status": "completed"
    }).eq("project_id", project_id).eq("phase_name", phase_name).execute()

    return {"message": "Phase updated successfully and LangGraph state synchronized."}
