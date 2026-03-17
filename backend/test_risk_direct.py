import sys
sys.path.append('d:/Main Projects/IPV1/ProtoStruct2/backend')

from app.ai.graph import app_graph

if __name__ == "__main__":
    initial_input = {
        "project_id": "test_proj_123",
        "problem_statement": "Design a portable solar-powered water purifier",
        "current_phase": "risk_analysis",
        "revision_count": 0,
        "validation_feedback": "",
        "morphological_alternatives": {
            "Power Source": "Solar Panel",
            "Filtration": "Reverse Osmosis",
            "Pump": "DC Water Pump"
        }
    }
    
    config = {"configurable": {"thread_id": "test_thread_123"}}
    
    try:
        import json
        print("Starting direct stream...")
        results = []
        for chunk in app_graph.stream(initial_input, config, stream_mode="values"):
            results.append(chunk)
        
        with open("direct_output.json", "w", encoding="utf-8") as f:
            json.dump(results, f, indent=2)
        print("Saved to direct_output.json!")
    except Exception as e:
        import traceback
        traceback.print_exc()
