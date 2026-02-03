"""
Demo script to execute sample missions via API
"""
import httpx
import time


API_BASE_URL = "http://localhost:8000"


def demo_normal_mission():
    """Demo: Normal mission that completes successfully"""
    print("\n" + "="*60)
    print("DEMO 1: Normal Mission (Should complete to DONE)")
    print("="*60)
    
    # Create mission via API
    print("\n➤ Creating mission via POST /missions...")
    response = httpx.post(f"{API_BASE_URL}/missions", json={
        "title": "Sample Test Mission",
        "description": "Execute pytest tests to verify the AJSON system",
        "attachments": []
    })
    
    if response.status_code != 200:
        print(f"✗ Failed to create mission: {response.status_code}")
        return None
    
    mission_id = response.json()["mission_id"]
    print(f"✓ Created mission {mission_id}")
    
    # Poll until terminal state
    print("\n➤ Polling mission status...")
    while True:
        response = httpx.get(f"{API_BASE_URL}/missions/{mission_id}")
        data = response.json()
        status = data["mission"]["status"]
        
        print(f"  Current status: {status}")
        
        if status in ["DONE", "PENDING_APPROVAL", "ERROR"]:
            break
        
        time.sleep(1)
    
    # Show final state
    print(f"\n✓ Final status: {status}")
    
    # Show SSOT data
    print(f"\n✓ SSOT Data:")
    print(f"  - Steps: {len(data['steps'])}")
    print(f"  - Approvals: {len(data['approvals'])}")
    print(f"  - Artifacts: {len(data['artifacts'])}")
    
    return mission_id


def demo_approval_mission():
    """Demo: Mission that requires approval"""
    print("\n" + "="*60)
    print("DEMO 2: Approval Required Mission (Should stop at PENDING_APPROVAL)")
    print("="*60)
    
    # Create mission with dangerous keyword
    print("\n➤ Creating mission with 'deploy' keyword...")
    response = httpx.post(f"{API_BASE_URL}/missions", json={
        "title": "Deploy to Production",
        "description": "Deploy application to production environment - requires approval",
        "attachments": []
    })
    
    if response.status_code != 200:
        print(f"✗ Failed to create mission: {response.status_code}")
        return None
    
    mission_id = response.json()["mission_id"]
    print(f"✓ Created mission {mission_id}")
    
    # Poll until it stops at PENDING_APPROVAL
    print("\n➤ Polling mission status...")
    while True:
        response = httpx.get(f"{API_BASE_URL}/missions/{mission_id}")
        data = response.json()
        status = data["mission"]["status"]
        
        print(f"  Current status: {status}")
        
        if status in ["DONE", "PENDING_APPROVAL", "ERROR"]:
            break
        
        time.sleep(1)
    
    # Show approval requests
    print(f"\n✓ Final status: {status}")
    
    if status == "PENDING_APPROVAL":
        approvals = data["approvals"]
        print(f"\n✓ Pending Approvals: {len(approvals)}")
        for approval in approvals:
            print(f"  - Type: {approval['gate_type']}")
            print(f"  - Reason: {approval['reason']}")
    
    return mission_id


def show_ssot_summary():
    """Show SSOT database summary by querying all missions"""
    print("\n" + "="*60)
    print("SSOT DATABASE SUMMARY")
    print("="*60)
    
    # Note: In a real implementation, we'd add a GET /missions endpoint
    # For now, we'll just print what we know from the demos
    print("\n✓ All missions created via API and tracked in SQLite SSOT")
    print("  - Each mission has full audit trail (steps, tool_runs, approvals, artifacts)")
    print("  - API provides real-time status via GET /missions/{id}")


if __name__ == "__main__":
    print("AJSON MVP Demo - Phase2 & Phase3 Complete (API Mode)")
    print("=" * 60)
    print("⚠️  NOTE: This demo requires uvicorn server to be running!")
    print("    Please start the server in another terminal:")
    print("    $ cd ajson-proto")
    print("    $ source venv/bin/activate")
    print("    $ uvicorn ajson.app:app --reload --port 8000")
    print("=" * 60)
    
    # Ask user to confirm server is running
    input("\nPress Enter once the server is running...")
    
    # Check if server is running
    try:
        response = httpx.get(f"{API_BASE_URL}/")
        print("✓ Server is running!\n")
    except httpx.ConnectError:
        print("✗ Server is not running. Please start it first.")
        print("  Run: uvicorn ajson.app:app --reload --port 8000")
        exit(1)
    
    # Run demos
    demo_normal_mission()
    demo_approval_mission()
    show_ssot_summary()
    
    print("\n" + "="*60)
    print("DEMO COMPLETE ✓")
    print("="*60)
    print("\nNext steps:")
    print("  - Open http://localhost:8000/console in your browser")
    print("  - Try creating missions with different descriptions")
    print("  - Test approval flow with dangerous keywords (deploy, delete, etc.)")
