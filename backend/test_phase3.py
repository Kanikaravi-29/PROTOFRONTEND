import asyncio
import os
import sys

# Add backend directory to path
sys.path.append('d:/Main Projects/IPV1/ProtoStruct2/backend')

from app.services.phase_service import start_phase_graph
from app.services.project_service import create_project_in_db
from app.core.config import supabase_client

if __name__ == "__main__":
    try:
        # Create a mock project and approve Phase 2 so Phase 3 can run
        project = create_project_in_db("00000000-0000-0000-0000-000000000000", "test problem")
        project_id = project["id"]
        
        supabase_client.table("project_phases").upsert({
            "project_id": project_id,
            "phase_name": "morphological_chart",
            "human_approved_data": {"test": "data"},
            "status": "completed"
        }, on_conflict="project_id, phase_name").execute()

        print("Running risk analysis...")
        res = start_phase_graph(project_id, "risk_analysis", "test problem")
        import json
        with open("test_phase3_output.json", "w") as f:
            json.dump(res, f, indent=2)
        print("Success! Output saved to test_phase3_output.json")
    except Exception as e:
        import traceback
        with open("error.txt", "w", encoding="utf-8") as f:
            traceback.print_exc(file=f)
        print("Failed. Check error.txt")
