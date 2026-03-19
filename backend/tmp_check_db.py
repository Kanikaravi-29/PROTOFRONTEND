from app.core.config import supabase_client
import json

res = supabase_client.table("projects").select("*").execute()
print(json.dumps(res.data, indent=2))

res_phases = supabase_client.table("project_phases").select("*").execute()
print(json.dumps(res_phases.data, indent=2))
