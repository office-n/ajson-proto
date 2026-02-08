# ajson/core/aggregator.py
from typing import List, Dict, Any

class Aggregator:
    def __init__(self):
        pass

    def collect(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Combines results from multiple agents.
        """
        merged = {
            "status": "success",
            "items": [],
            "warnings": []
        }
        
        for res in results:
            if "error" in res:
                merged["warnings"].append(f"Agent error: {res['error']}")
                continue
                
            # Conflict Resolution: If outputs disagree? 
            # For Phase 9.1, we just append all valid sub-results.
            if "output" in res:
                merged["items"].append(res["output"])
            
        # Quality Gate (Simple)
        if not merged["items"] and not merged["warnings"]:
             merged["status"] = "empty"
             merged["warnings"].append("No valid output produced.")
             
        return merged
