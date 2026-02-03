"""
FastAPI application for AJSON MVP
"""
from fastapi import FastAPI, HTTPException, BackgroundTasks, UploadFile, File
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from pathlib import Path
import os
import uuid

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


@app.get("/healthz")
def healthz():
    """
    Health check endpoint for monitoring
    
    Returns:
        {"status": "ok"}
    """
    return {"status": "ok"}


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


# Upload configuration
UPLOAD_DIR = Path("./uploads")
ALLOWED_EXTENSIONS = {'.pdf', '.txt', '.md', '.json', '.png', '.jpg', '.jpeg'}
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB


@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    """
    Upload a file with security constraints
    
    Returns:
        { "upload_id": str, "filename": str }
    """
    # Validate extension
    filename = file.filename or "unknown"
    file_ext = Path(filename).suffix.lower()
    
    if file_ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400, 
            detail=f"File extension {file_ext} not allowed. Allowed: {', '.join(ALLOWED_EXTENSIONS)}"
        )
    
    # Read file content
    content = await file.read()
    file_size = len(content)
    
    # Validate size
    if file_size > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=413, 
            detail=f"File size {file_size} bytes exceeds maximum {MAX_FILE_SIZE} bytes (50MB)"
        )
    
    # Generate UUID and sanitized filename (path traversal prevention)
    upload_id = str(uuid.uuid4())
    # Only use basename to prevent path traversal
    safe_filename = Path(filename).name
    stored_name = f"{upload_id}{file_ext}"
    
    # Ensure upload directory exists
    UPLOAD_DIR.mkdir(exist_ok=True)
    
    # Save file
    file_path = UPLOAD_DIR / stored_name
    with open(file_path, "wb") as f:
        f.write(content)
    
    # Store in database
    db.init_db()
    db.create_upload(
        upload_id=upload_id,
        original_name=safe_filename,
        stored_name=stored_name,
        size=file_size,
        mime_type=file.content_type
    )
    
    return {
        "upload_id": upload_id,
        "filename": safe_filename,
        "size": file_size
    }


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
                <p class="subtitle">エージェント駆動型JSON実行システム - MVP</p>
                
                <form id="missionForm">
                    <label for="title">ミッション名</label>
                    <input type="text" id="title" name="title" placeholder="例: テスト実行" required>
                    
                    <label for="description">ミッション内容 <button type="button" id="voiceBtn" onclick="startVoiceInput()" style="margin-left: 10px; padding: 4px 8px; font-size: 12px;">🎤 音声入力</button></label>
                    <textarea id="description" name="description" placeholder="実行したい内容を記述してください..." required></textarea>
                    
                    <label for="fileUpload">ファイル添付（任意）</label>
                    <input type="file" id="fileUpload" name="file" accept=".pdf,.txt,.md,.json,.png,.jpg,.jpeg" style="margin-bottom: 10px;">
                    <button type="button" onclick="uploadFile()" id="uploadBtn" style="margin-bottom: 20px; background: #4caf50;">📎 ファイルアップロード</button>
                    <div id="uploadStatus" style="margin-bottom: 20px; font-size: 14px; color: #666;"></div>
                    
                    <label for="attachments">添付（パス/URL/upload_id）</label>
                    <textarea id="attachments" name="attachments" placeholder="パス、URL、またはupload_idを改行区切りで入力（任意）" style="min-height: 80px;"></textarea>
                    
                    <button type="submit" id="submitBtn">ミッション作成</button>
                </form>
            </div>
            
            <div class="status-card" id="statusCard">
                <h2>ミッション状況</h2>
                <p><strong>ミッションID:</strong> <span id="missionId">-</span></p>
                <p><strong>タイトル:</strong> <span id="missionTitle">-</span></p>
                <p><strong>ステータス:</strong> <span id="missionStatus">-</span></p>
                
                <div id="approvalSection" style="display: none;" class="approval-section">
                    <h3>⚠️ 承認が必要です</h3>
                    <p><strong>タイプ:</strong> <span id="approvalType">-</span></p>
                    <p><strong>理由:</strong> <span id="approvalReason">-</span></p>
                    <div class="approval-buttons">
                        <button class="btn-yes" onclick="approve('yes')">✓ 承認</button>
                        <button class="btn-no" onclick="approve('no')">✗ 却下</button>
                    </div>
                </div>
                
                <div style="margin-top: 20px;">
                    <h3>ステップ</h3>
                    <div id="stepsList"></div>
                </div>
            </div>
        </div>
        
        <script>
            let currentMissionId = null;
            let pollInterval = null;
            
            // Upload file function
            async function uploadFile() {
                const fileInput = document.getElementById('fileUpload');
                const file = fileInput.files[0];
                
                if (!file) {
                    alert('ファイルを選択してください');
                    return;
                }
                
                const uploadBtn = document.getElementById('uploadBtn');
                const uploadStatus = document.getElementById('uploadStatus');
                
                uploadBtn.disabled = true;
                uploadBtn.textContent = 'アップロード中...';
                uploadStatus.textContent = '';
                
                try {
                    const formData = new FormData();
                    formData.append('file', file);
                    
                    const response = await fetch('/upload', {
                        method: 'POST',
                        body: formData
                    });
                    
                    if (!response.ok) {
                        const error = await response.json();
                        throw new Error(error.detail || 'アップロード失敗');
                    }
                    
                    const data = await response.json();
                    
                    // Add upload_id to attachments textarea
                    const attachmentsField = document.getElementById('attachments');
                    const currentValue = attachmentsField.value.trim();
                    attachmentsField.value = currentValue 
                        ? currentValue + '\\n' + data.upload_id 
                        : data.upload_id;
                    
                    uploadStatus.innerHTML = `<span style="color: green;">✓ ${data.filename} をアップロードしました (ID: ${data.upload_id})</span>`;
                    fileInput.value = '';
                    
                } catch (error) {
                    alert('アップロードエラー: ' + error.message);
                    uploadStatus.innerHTML = `<span style="color: red;">✗ ${error.message}</span>`;
                } finally {
                    uploadBtn.disabled = false;
                    uploadBtn.textContent = '📎 ファイルアップロード';
                }
            }
            
            // Voice input function
            function startVoiceInput() {
                if (!('webkitSpeechRecognition' in window)) {
                    alert('音声入力は非対応です（Chrome/Edgeで利用可能）');
                    return;
                }
                
                const recognition = new webkitSpeechRecognition();
                recognition.lang = 'ja-JP';
                recognition.continuous = false;
                recognition.interimResults = false;
                
                const voiceBtn = document.getElementById('voiceBtn');
                voiceBtn.disabled = true;
                voiceBtn.textContent = '🎤 聞き取り中...';
                
                recognition.onresult = (event) => {
                    const transcript = event.results[0][0].transcript;
                    const descField = document.getElementById('description');
                    descField.value += (descField.value ? ' ' : '') + transcript;
                    voiceBtn.disabled = false;
                    voiceBtn.textContent = '🎤 音声入力';
                };
                
                recognition.onerror = (event) => {
                    alert('音声認識エラー: ' + event.error);
                    voiceBtn.disabled = false;
                    voiceBtn.textContent = '🎤 音声入力';
                };
                
                recognition.onend = () => {
                    voiceBtn.disabled = false;
                    voiceBtn.textContent = '🎤 音声入力';
                };
                
                recognition.start();
            }
            
            // Mission form submission
            document.getElementById('missionForm').addEventListener('submit', async (e) => {
                e.preventDefault();
                
                const title = document.getElementById('title').value;
                const description = document.getElementById('description').value;
                const attachmentsText = document.getElementById('attachments').value;
                const attachments = attachmentsText.split('\n').filter(line => line.trim() !== '');
                
                // Disable submit button
                const submitBtn = document.getElementById('submitBtn');
                submitBtn.disabled = true;
                submitBtn.innerHTML = '作成中... <span class="loading"></span>';
                
                try {
                    const response = await fetch('/missions', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ title, description, attachments })
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
                    alert('ミッション作成エラー: ' + error.message);
                    submitBtn.disabled = false;
                    submitBtn.textContent = 'ミッション作成';
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
                    
                    // Japanese status mapping
                    const statusLabels = {
                        'CREATED': '作成済(CREATED)',
                        'PLANNED': '計画済(PLANNED)',
                        'PRE_AUDIT': '事前監査中(PRE_AUDIT)',
                        'EXECUTE': '実行中(EXECUTE)',
                        'POST_AUDIT': '事後監査中(POST_AUDIT)',
                        'FINALIZE': '最終処理中(FINALIZE)',
                        'DONE': '完了(DONE)',
                        'PENDING_APPROVAL': '承認待ち(PENDING_APPROVAL)',
                        'ERROR': 'エラー(ERROR)'
                    };
                    
                    const displayStatus = statusLabels[mission.status] || mission.status;
                    
                    // Update status badge
                    document.getElementById('missionStatus').innerHTML = 
                        `<span class="status-badge ${status}">${displayStatus}</span>`;
                    
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
                        submitBtn.textContent = 'ミッション作成';
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
                    alert('承認処理エラー: ' + error.message);
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
