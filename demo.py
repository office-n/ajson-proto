"""
Demo script to execute sample missions and verify SSOT
"""
import sys
import os
import json

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from ajson import db, orchestrator


def demo_normal_mission():
    """Demo: Normal mission that completes successfully"""
    print("\n" + "="*60)
    print("DEMO 1: Normal Mission (Should complete to DONE)")
    print("="*60)
    
    # Create mission
    mission_id = db.create_mission(
        title="Sample Test Mission",
        description="Execute pytest tests to verify the AJSON system"
    )
    print(f"\n✓ Created mission {mission_id}")
    
    # Execute through all states
    while True:
        mission = db.get_mission(mission_id)
        status = mission["status"]
        print(f"  Current status: {status}")
        
        if status == "DONE" or status == "PENDING_APPROVAL":
            break
        
        orchestrator.execute_mission(mission_id)
    
    # Show final state
    mission = db.get_mission(mission_id)
    print(f"\n✓ Final status: {mission['status']}")
    
    # Show SSOT data
    steps = db.get_steps_by_mission(mission_id)
    tool_runs = db.get_tool_runs_by_mission(mission_id)
    artifacts = db.get_artifacts_by_mission(mission_id)
    
    print(f"\n✓ SSOT Data:")
    print(f"  - Steps: {len(steps)}")
    print(f"  - Tool runs: {len(tool_runs)}")
    print(f"  - Artifacts: {len(artifacts)}")
    
    return mission_id


def demo_approval_mission():
    """Demo: Mission that requires approval"""
    print("\n" + "="*60)
    print("DEMO 2: Approval Required Mission (Should stop at PENDING_APPROVAL)")
    print("="*60)
    
    # Create mission
    mission_id = db.create_mission(
        title="Deploy to Production",
        description="Deploy application to production environment - requires approval"
    )
    print(f"\n✓ Created mission {mission_id}")
    
    # Execute until approval needed
    while True:
        mission = db.get_mission(mission_id)
        status = mission["status"]
        print(f"  Current status: {status}")
        
        if status == "DONE" or status == "PENDING_APPROVAL":
            break
        
        orchestrator.execute_mission(mission_id)
    
    # Show approval requests
    mission = db.get_mission(mission_id)
    print(f"\n✓ Final status: {mission['status']}")
    
    if mission["status"] == "PENDING_APPROVAL":
        approvals = db.get_pending_approvals(mission_id)
        print(f"\n✓ Pending Approvals: {len(approvals)}")
        for approval in approvals:
            print(f"  - Type: {approval['gate_type']}")
            print(f"  - Reason: {approval['reason']}")
    
    return mission_id


def show_ssot_summary():
    """Show SSOT database summary"""
    print("\n" + "="*60)
    print("SSOT DATABASE SUMMARY")
    print("="*60)
    
    missions = db.list_missions()
    print(f"\n✓ Total Missions: {len(missions)}")
    
    for mission in missions:
        print(f"\n  Mission {mission['id']}: {mission['title']}")
        print(f"    Status: {mission['status']}")
        
        steps = db.get_steps_by_mission(mission['id'])
        tool_runs = db.get_tool_runs_by_mission(mission['id'])
        approvals = db.get_pending_approvals(mission['id'])
        artifacts = db.get_artifacts_by_mission(mission['id'])
        
        print(f"    Steps: {len(steps)}, Tool Runs: {len(tool_runs)}, Approvals: {len(approvals)}, Artifacts: {len(artifacts)}")


if __name__ == "__main__":
    # Initialize database
    db.init_db()
    print("AJSON MVP Demo - Phase0 & Phase1 Complete")
    
    # Run demos
    demo_normal_mission()
    demo_approval_mission()
    show_ssot_summary()
    
    print("\n" + "="*60)
    print("DEMO COMPLETE ✓")
    print("="*60)
