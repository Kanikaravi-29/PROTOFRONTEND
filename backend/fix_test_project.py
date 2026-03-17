import sys
sys.path.append('d:/Main Projects/IPV1/ProtoStruct2/backend')
from app.core.config import supabase_client

project_id = "8ac98ba0-0e82-44c4-8a33-db544fb11f63"

# Let's see if project exists
prev = supabase_client.table("project_phases").select("*").eq("project_id", project_id).execute()
print("Phases for project:", prev.data)

# Force approve Phase 2
dummy_data = {"dummy": "approved"}
supabase_client.table("project_phases").upsert({
    "project_id": project_id,
    "phase_name": "morphological_chart",
    "human_approved_data": dummy_data,
    "status": "completed"
}, on_conflict="project_id, phase_name").execute()

print("Phase 2 forcefully approved for test project.")
