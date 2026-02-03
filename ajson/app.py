"""
FastAPI application for AJSON MVP
"""
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import os

from ajson import db, orchestrator
from ajson.models import MissionStatus, MissionCreate

app = FastAPI(title="AJSON Mission API", version="1.0.0")

# CORS for development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Request models
class ApprovalDecision(BaseModel):
    """Approval decision request"""
    decision: str  # "yes" or "no"


# Helper functions
def run_to_terminal(mission_id: int):
    """
    Execute mission until terminal state (DONE, PENDING_APPROVAL, or ERROR)
    """
    max_iterations = 20  # Safety limit
    iterations = 0
    
    while iterations < max_iterations:
        mission = db.get_mission(mission_id)
        if not mission:
            break
        
        status = mission["status"]
        
        # Terminal states
        if status in [MissionStatus.DONE, MissionStatus.PENDING_APPROVAL, MissionStatus.ERROR]:
            break
        
        try:
            orchestrator.execute_mission(mission_id)
        except Exception as e:
            # Mark as error on failure
            db.update_mission_status(mission_id, MissionStatus.ERROR)
            break
        
        iterations += 1


# API Endpoints
@app.post("/missions")
def create_mission(mission: MissionCreate, background_tasks: BackgroundTasks):
    """
    Create a new mission and execute it in the background
    
    Returns:
        { "mission_id": int }
    """
    # Initialize database
    db.init_db()
    
    # Create mission
    mission_id = db.create_mission(
        title=mission.title,
        description=mission.description
    )
    
    # Run in background to avoid blocking UI
    background_tasks.add_task(run_to_terminal, mission_id)
    
    return {"mission_id": mission_id}


@app.get("/missions/{mission_id}")
def get_mission(mission_id: int):
    """
    Get mission status and details
    
    Returns:
        {
            "mission": {...},
            "steps": [...],
            "approvals": [...],
            "artifacts": [...]
        }
    """
    mission = db.get_mission(mission_id)
    if not mission:
        raise HTTPException(status_code=404, detail=f"Mission {mission_id} not found")
    
    steps = db.get_steps_by_mission(mission_id)
    approvals = db.get_pending_approvals(mission_id)
    artifacts = db.get_artifacts_by_mission(mission_id)
    
    return {
        "mission": mission,
        "steps": steps,
        "approvals": approvals,
        "artifacts": artifacts
    }


@app.post("/missions/{mission_id}/approve")
def approve_mission(mission_id: int, decision: ApprovalDecision, background_tasks: BackgroundTasks):
    """
    Approve or reject a pending mission
    
    Args:
        decision: "yes" or "no"
    
    Returns:
        { "status": str, "message": str }
    """
    mission = db.get_mission(mission_id)
    if not mission:
        raise HTTPException(status_code=404, detail=f"Mission {mission_id} not found")
    
    if mission["status"] != MissionStatus.PENDING_APPROVAL:
        raise HTTPException(
            status_code=400, 
            detail=f"Mission {mission_id} is not pending approval (current status: {mission['status']})"
        )
    
    if decision.decision.lower() == "yes":
        # Approve and resume
        orchestrator.approve_mission(mission_id)
        
        # Continue execution in background
        background_tasks.add_task(run_to_terminal, mission_id)
        
        return {
            "status": "approved",
            "message": f"Mission {mission_id} approved and resumed"
        }
    elif decision.decision.lower() == "no":
        # Reject: update to ABORTED state (or keep PENDING_APPROVAL with rejected approvals)
        # For MVP, we'll just mark approvals as rejected and keep mission in PENDING_APPROVAL
        approvals = db.get_pending_approvals(mission_id)
        for approval in approvals:
            # Mark as rejected (we'll update DB function if needed)
            pass  # MVP: just keep in PENDING_APPROVAL state
        
        return {
            "status": "rejected",
            "message": f"Mission {mission_id} approval rejected, mission stopped"
        }
    else:
        raise HTTPException(status_code=400, detail="Decision must be 'yes' or 'no'")


@app.get("/console", response_class=HTMLResponse)
def console():
    """
    Mission Console UI - Single page for mission creation and monitoring
    """
    html_content = """
    <!DOCTYPE html>
    <html lang="ja">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>AJSON Mission Console</title>
        <style>
            * {
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }
            
            body {
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
                padding: 20px;
            }
            
            .container {
                max-width: 900px;
                margin: 0 auto;
            }
            
            .card {
                background: white;
                border-radius: 12px;
                box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
                padding: 30px;
                margin-bottom: 20px;
            }
            
            h1 {
                color: #667eea;
                margin-bottom: 10px;
                font-size: 32px;
            }
            
            .subtitle {
                color: #666;
                margin-bottom: 30px;
                font-size: 14px;
            }
            
            label {
                display: block;
                margin-bottom: 8px;
                font-weight: 600;
                color: #333;
            }
            
            input, textarea {
                width: 100%;
                padding: 12px;
                border: 2px solid #e0e0e0;
                border-radius: 8px;
                font-size: 14px;
                margin-bottom: 20px;
                transition: border-color 0.3s;
            }
            
            input:focus, textarea:focus {
                outline: none;
                border-color: #667eea;
            }
            
            textarea {
                resize: vertical;
                min-height: 120px;
                font-family: inherit;
            }
            
            button {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                border: none;
                padding: 14px 28px;
                border-radius: 8px;
                font-size: 16px;
                font-weight: 600;
                cursor: pointer;
                transition: transform 0.2s, box-shadow 0.2s;
            }
            
            button:hover {
                transform: translateY(-2px);
                box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
            }
            
            button:active {
                transform: translateY(0);
            }
            
            button:disabled {
                background: #ccc;
                cursor: not-allowed;
                transform: none;
            }
            
            .status-card {
                display: none;
                background: #f8f9fa;
                border-radius: 8px;
                padding: 20px;
                margin-top: 20px;
            }
            
            .status-card.active {
                display: block;
            }
            
            .status-badge {
                display: inline-block;
                padding: 6px 12px;
                border-radius: 6px;
                font-size: 12px;
                font-weight: 600;
                text-transform: uppercase;
                margin-right: 10px;
            }
            
            .status-badge.created { background: #e3f2fd; color: #1976d2; }
            .status-badge.planned { background: #f3e5f5; color: #7b1fa2; }
            .status-badge.pre_audit { background: #fff3e0; color: #e65100; }
            .status-badge.execute { background: #e8f5e9; color: #2e7d32; }
            .status-badge.post_audit { background: #fce4ec; color: #c2185b; }
            .status-badge.finalize { background: #e0f2f1; color: #00695c; }
            .status-badge.done { background: #c8e6c9; color: #2e7d32; }
            .status-badge.pending_approval { background: #fff9c4; color: #f57f17; }
            .status-badge.error { background: #ffcdd2; color: #c62828; }
            
            .approval-section {
                margin-top: 20px;
                padding: 16px;
                background: #fff9c4;
                border-left: 4px solid #f57f17;
                border-radius: 4px;
            }
            
            .approval-buttons {
                margin-top: 12px;
            }
            
            .btn-yes {
                background: #4caf50;
                margin-right: 10px;
            }
            
            .btn-no {
                background: #f44336;
            }
            
            .step-item {
                padding: 12px;
                background: white;
                border-radius: 6px;
                margin-bottom: 8px;
                border-left: 3px solid #667eea;
            }
            
            .loading {
                display: inline-block;
                width: 16px;
                height: 16px;
                border: 3px solid #f3f3f3;
                border-top: 3px solid #667eea;
                border-radius: 50%;
                animation: spin 1s linear infinite;
                margin-left: 10px;
            }
            
            @keyframes spin {
                0% { transform: rotate(0deg); }
                100% { transform: rotate(360deg); }
            }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="card">
                <h1>🚀 AJSON Mission Console</h1>
                <p class="subtitle">Agent-driven JSON Orchestration System - MVP</p>
                
                <form id="missionForm">
                    <label for="title">Mission Title</label>
                    <input type="text" id="title" name="title" placeholder="e.g., Run Tests" required>
                    
                    <label for="description">Mission Description</label>
                    <textarea id="description" name="description" placeholder="Describe what you want to accomplish..." required></textarea>
                    
                    <button type="submit" id="submitBtn">Create Mission</button>
                </form>
            </div>
            
            <div class="status-card" id="statusCard">
                <h2>Mission Status</h2>
                <p><strong>Mission ID:</strong> <span id="missionId">-</span></p>
                <p><strong>Title:</strong> <span id="missionTitle">-</span></p>
                <p><strong>Status:</strong> <span id="missionStatus">-</span></p>
                
                <div id="approvalSection" style="display: none;" class="approval-section">
                    <h3>⚠️ Approval Required</h3>
                    <p><strong>Type:</strong> <span id="approvalType">-</span></p>
                    <p><strong>Reason:</strong> <span id="approvalReason">-</span></p>
                    <div class="approval-buttons">
                        <button class="btn-yes" onclick="approve('yes')">✓ Approve</button>
                        <button class="btn-no" onclick="approve('no')">✗ Reject</button>
                    </div>
                </div>
                
                <div style="margin-top: 20px;">
                    <h3>Steps</h3>
                    <div id="stepsList"></div>
                </div>
            </div>
        </div>
        
        <script>
            let currentMissionId = null;
            let pollInterval = null;
            
            document.getElementById('missionForm').addEventListener('submit', async (e) => {
                e.preventDefault();
                
                const title = document.getElementById('title').value;
                const description = document.getElementById('description').value;
                
                // Disable submit button
                const submitBtn = document.getElementById('submitBtn');
                submitBtn.disabled = true;
                submitBtn.innerHTML = 'Creating... <span class="loading"></span>';
                
                try {
                    const response = await fetch('/missions', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ title, description, attachments: [] })
                    });
                    
                    const data = await response.json();
                    currentMissionId = data.mission_id;
                    
                    // Show status card
                    document.getElementById('statusCard').classList.add('active');
                    document.getElementById('missionId').textContent = currentMissionId;
                    document.getElementById('missionTitle').textContent = title;
                    
                    // Start polling
                    startPolling();
                    
                } catch (error) {
                    alert('Error creating mission: ' + error.message);
                    submitBtn.disabled = false;
                    submitBtn.textContent = 'Create Mission';
                }
            });
            
            function startPolling() {
                if (pollInterval) clearInterval(pollInterval);
                
                // Poll every 1 second
                pollInterval = setInterval(updateStatus, 1000);
                updateStatus(); // Initial update
            }
            
            async function updateStatus() {
                if (!currentMissionId) return;
                
                try {
                    const response = await fetch(`/missions/${currentMissionId}`);
                    const data = await response.json();
                    
                    const mission = data.mission;
                    const status = mission.status.toLowerCase().replace(/_/g, '_');
                    
                    // Update status badge
                    document.getElementById('missionStatus').innerHTML = 
                        `<span class="status-badge ${status}">${mission.status}</span>`;
                    
                    // Update steps
                    const stepsList = document.getElementById('stepsList');
                    stepsList.innerHTML = data.steps.map(step => `
                        <div class="step-item">
                            <strong>${step.role}</strong>: ${step.status}
                        </div>
                    `).join('');
                    
                    // Check for approvals
                    const approvalSection = document.getElementById('approvalSection');
                    if (data.approvals && data.approvals.length > 0) {
                        const approval = data.approvals[0];
                        document.getElementById('approvalType').textContent = approval.gate_type;
                        document.getElementById('approvalReason').textContent = approval.reason;
                        approvalSection.style.display = 'block';
                    } else {
                        approvalSection.style.display = 'none';
                    }
                    
                    // Stop polling if done
                    if (mission.status === 'DONE' || mission.status === 'ERROR') {
                        clearInterval(pollInterval);
                        
                        // Re-enable submit button
                        const submitBtn = document.getElementById('submitBtn');
                        submitBtn.disabled = false;
                        submitBtn.textContent = 'Create Mission';
                    }
                    
                } catch (error) {
                    console.error('Error updating status:', error);
                }
            }
            
            async function approve(decision) {
                if (!currentMissionId) return;
                
                try {
                    const response = await fetch(`/missions/${currentMissionId}/approve`, {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ decision })
                    });
                    
                    const data = await response.json();
                    
                    if (decision === 'yes') {
                        // Resume polling
                        startPolling();
                    } else {
                        // Stop polling if rejected
                        clearInterval(pollInterval);
                    }
                    
                } catch (error) {
                    alert('Error processing approval: ' + error.message);
                }
            }
        </script>
    </body>
    </html>
    """
    return html_content


@app.get("/")
def root():
    """Redirect to console"""
    return {"message": "AJSON Mission API", "console": "/console"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
