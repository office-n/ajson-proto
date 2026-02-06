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


class MessageCreate(BaseModel):
    """Create message request"""
    content: str
    attachment_ids: Optional[List[str]] = None


class MessageOut(BaseModel):
    """Message response"""
    id: int
    mission_id: int
    role: str
    content: str
    attachments_json: Optional[str]
    created_at: str



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
    from datetime import datetime
    
    # Initialize database
    db.init_db()
    
    # Auto-generate title if empty
    title = mission.title
    if not title or title.strip() == "":
        # Use first 20 chars of description + timestamp
        title = mission.description[:20] + f" {datetime.now().strftime('%Y-%m-%d %H:%M')}"
    
    # Create mission
    mission_id = db.create_mission(
        title=title,
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


@app.get("/missions/{mission_id}/messages")
def get_mission_messages(mission_id: int):
    """
    Get all messages for a mission
    
    Returns:
        {
            "mission_id": int,
            "messages": [...]
        }
    """
    db.init_db()
    
    # Verify mission exists
    mission = db.get_mission(mission_id)
    if not mission:
        raise HTTPException(status_code=404, detail=f"Mission {mission_id} not found")
    
    messages = db.get_messages(mission_id)
    
    return {
        "mission_id": mission_id,
        "messages": messages
    }


@app.post("/missions/{mission_id}/messages")
def create_mission_message(mission_id: int, message: MessageCreate, background_tasks: BackgroundTasks):
    """
    Send a message and trigger orchestrator
    
    Returns:
        { "message_id": int, "mission_id": int }
    """
    import json
    
    db.init_db()
    
    # Verify mission exists
    mission = db.get_mission(mission_id)
    if not mission:
        raise HTTPException(status_code=404, detail=f"Mission {mission_id} not found")
    
    # Insert user message
    attachments_json = json.dumps(message.attachment_ids or [])
    msg_id = db.create_message(
        mission_id=mission_id,
        role="user",
        content=message.content,
        attachments_json=attachments_json
    )
    
    # Trigger orchestrator in background
    # Note: Check for existing lock to prevent double execution
    # For MVP, run_to_terminal already has max iteration protection
    background_tasks.add_task(run_to_terminal, mission_id)
    
    return {"message_id": msg_id, "mission_id": mission_id}



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
    Mission Console UI - ChatGPT-style chat interface with legacy form UI
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
                margin-bottom: 20px;
                font-size: 14px;
            }
            
            /* Chat UI Styles */
            #chatRoot {
                margin-bottom: 30px;
            }
            
            #chatHistory {
                max-height: calc(100vh - 420px);
                min-height: 200px;
                overflow-y: auto;
                border: 2px solid #e0e0e0;
                border-radius: 8px;
                padding: 15px;
                padding-bottom: 180px; /* Reserve space for composer */
                margin-bottom: 15px;
                background: #f9f9f9;
            }
            
            .chat-message {
                padding: 10px;
                margin-bottom: 10px;
                border-radius: 8px;
                background: white;
                border-left: 4px solid #667eea;
            }
            
            .chat-message.user {
                border-left-color: #4caf50;
                background: #f1f8f4;
            }
            
            .chat-message.jarvis {
                border-left-color: #667eea;
            }
            
            .chat-message.cody {
                border-left-color: #ff9800;
            }
            
            .chat-message.ants {
                border-left-color: #e91e63;
            }
            
            .chat-role {
                font-weight: 600;
                margin-bottom: 5px;
                font-size: 12px;
                text-transform: uppercase;
                color: #666;
            }
            
            .chat-content {
                margin-bottom: 5px;
                line-height: 1.5;
            }
            
            .chat-time {
                font-size: 11px;
                color: #999;
            }
            
            #chatInputBar {
                position: sticky;
                bottom: 0;
                display: flex;
                gap: 10px;
                align-items: flex-end;
                background: white;
                padding: 15px;
                padding-bottom: max(15px, env(safe-area-inset-bottom));
                box-shadow: 0 -2px 10px rgba(0,0,0,0.1);
                border-radius: 8px;
                z-index: 100;
            }
            
            #chatMessageInput {
                flex: 1;
                padding: 12px;
                border: 2px solid #e0e0e0;
                border-radius: 8px;
                font-size: 14px;
                font-family: inherit;
                resize: vertical;
                min-height: clamp(100px, 20vh, 150px);
                max-height: min(300px, 40vh);
            }
            
            #chatMessageInput:focus {
                outline: none;
                border-color: #667eea;
            }
            
            #chatSendBtn {
                padding: 12px 24px;
                background: #667eea;
                color: white;
                border: none;
                border-radius: 8px;
                font-size: 14px;
                font-weight: 600;
                cursor: pointer;
                transition: background 0.3s;
            }
            
            #chatSendBtn:hover {
                background: #5568d3;
            }
            
            #chatSendBtn:disabled {
                background: #ccc;
                cursor: not-allowed;
            }
            
            #chatAttachBtn {
                padding: 12px;
                background: #f5f5f5;
                color: #333;
                border: 2px solid #e0e0e0;
                border-radius: 8px;
                font-size: 18px;
                cursor: pointer;
                transition: background 0.3s;
            }
            
            #chatAttachBtn:hover {
                background: #ececec;
            }
            
            #chatAttachments {
                display: flex;
                flex-wrap: wrap;
                gap: 8px;
                margin-bottom: 10px;
            }
            
            .attachment-chip {
                display: inline-flex;
                align-items: center;
                gap: 6px;
                padding: 6px 12px;
                background: #e3f2fd;
                border: 1px solid #90caf9;
                border-radius: 16px;
                font-size: 12px;
                color: #1976d2;
            }
            
            .attachment-chip .remove-btn {
                cursor: pointer;
                font-weight: bold;
                padding: 0 4px;
                color: #1976d2;
            }
            
            .attachment-chip .remove-btn:hover {
                color: #c62828;
            }
            
            #chatRoot.drag-over {
                background: #f0f4ff;
                border: 2px dashed #667eea;
            }
            
            #chatVoiceBtn {
                padding: 12px;
                background: #f5f5f5;
                color: #333;
                border: 2px solid #e0e0e0;
                border-radius: 8px;
                font-size: 18px;
                cursor: pointer;
                transition: all 0.3s;
            }
            
            #chatVoiceBtn:hover {
                background: #ececec;
            }
            
            #chatVoiceBtn.listening {
                outline: 3px solid #667eea;
                background: #e3f2fd;
                animation: pulse 1.5s infinite;
            }
            
            @keyframes pulse {
                0%, 100% { opacity: 1; }
                50% { opacity: 0.7; }
            }
            
            #chatError {
                padding: 10px;
                background: #ffebee;
                color: #c62828;
                border-radius: 8px;
                margin-bottom: 10px;
                display: none;
            }
            
            #chatError.show {
                display: block;
            }
            
            /* Trace button (P2) */
            .trace-btn {
                background: transparent;
                border: none;
                color: #999;
                font-size: 14px;
                cursor: pointer;
                padding: 2px 4px;
                margin-left: 6px;
                transition: color 0.2s;
            }
            
            .trace-btn:hover {
                color: #667eea;
            }
            
           /* Trace modal (P2) */
            .modal {
                display: none;
                position: fixed;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                background: rgba(0,0,0,0.5);
                z-index: 1000;
                justify-content: center;
                align-items: center;
            }
            
            .modal.show {
                display: flex;
            }
            
            .modal-content {
                background: white;
                border-radius: 12px;
                padding: 30px;
                max-width: 600px;
                max-height: 80vh;
                overflow-y: auto;
                position: relative;
            }
            
            .modal-header {
                display: flex;
                justify-content: space-between;
                align-items: center;
                margin-bottom: 20px;
            }
            
            .modal-close {
                background: #f5f5f5;
                border: none;
                border-radius: 50%;
                width: 32px;
                height: 32px;
                font-size: 20px;
                cursor: pointer;
                transition: background 0.2s;
            }
            
            .modal-close:hover {
                background: #ececec;
            }
            
            .trace-content {
                font-family: monospace;
                font-size: 12px;
                white-space: pre-wrap;
                word-wrap: break-word;
                background: #f9f9f9;
                padding: 15px;
                border-radius: 8px;
                border: 1px solid #e0e0e0;
            }
            
            /* Legacy UI Styles */
            details {
                margin-top: 20px;
            }
            
            summary {
                cursor: pointer;
                font-weight: 600;
                padding: 10px;
                background: #f5f5f5;
                border-radius: 8px;
            }
            
            summary:hover {
                background: #ececec;
            }
            
            label {
                display: block;
                margin-bottom: 8px;
                margin-top: 15px;
                font-weight: 600;
                color: #333;
            }
            
            input, textarea {
                width: 100%;
                padding: 12px;
                border: 2px solid #e0e0e0;
                border-radius: 8px;
                font-size: 14px;
                margin-bottom: 10px;
                transition: border-color 0.3s;
            }
            
            input:focus, textarea:focus {
                outline: none;
                border-color: #667eea;
            }
            
            button {
                background: #667eea;
                color: white;
                padding: 12px 24px;
                border: none;
                border-radius: 8px;
                font-size: 14px;
                font-weight: 600;
                cursor: pointer;
                transition: background 0.3s;
            }
            
            button:hover {
                background: #5568d3;
            }
            
            button:disabled {
                background: #ccc;
                cursor: not-allowed;
            }
            
            .status-card {
                background: white;
                border-radius: 12px;
                box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
                padding: 30px;
                margin-top: 20px;
                display: none;
            }
            
            .status-card.active {
                display: block;
            }
            
            .approval-section {
                background: #fff3cd;
                padding: 20px;
                border-radius: 8px;
                margin-top: 20px;
            }
            
            .approval-buttons {
                display: flex;
                gap: 10px;
                margin-top: 15px;
            }
            
            .btn-yes {
                background: #4caf50;
            }
            
            .btn-yes:hover {
                background: #45a049;
            }
            
            .btn-no {
                background: #f44336;
            }
            
            .btn-no:hover {
                background: #da190b;
            }
            
            .loading {
                display: inline-block;
                width: 14px;
                height: 14px;
                border: 3px solid #fff;
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
                <p class="subtitle">エージェント駆動型JSON実行システム - ChatGPT型UI</p>
                
                <!-- Chat UI -->
                <div id="chatRoot">
                    <div id="chatError"></div>
                    <div id="missionStatusDisplay" style="text-align: center; padding: 8px; font-size: 13px; color: #999;">未選択（最初の送信で自動作成されます）</div>
                    <div id="chatHistory">
                        <p style="color: #999; text-align: center;">ミッションを作成すると、ここにチャット履歴が表示されます</p>
                    </div>
                    <div id="chatAttachments"></div>
                    <div id="chatInputBar">
                        <button id="chatAttachBtn" type="button">📎</button>
                        <input id="chatFileInput" type="file" multiple accept=".pdf,.txt,.md,.json,.png,.jpg,.jpeg" style="display: none;" />
                        <button id="chatVoiceBtn" type="button" title="音声入力">🎤</button>
                        <textarea id="chatMessageInput" placeholder="メッセージを入力..."></textarea>
                        <button id="chatSendBtn">送信</button>
                    </div>
                </div>
                
                <!-- Trace Modal (P2) -->
                <div id="traceModal" class="modal">
                    <div class="modal-content">
                        <div class="modal-header">
                            <h3>🧾 Trace詳細</h3>
                            <button class="modal-close" onclick="hideTraceModal()">✕</button>
                        </div>
                        <div id="traceContent" class="trace-content"></div>
                    </div>
                </div>
                
                <!-- Legacy Form UI (collapsed) -->
                <details>
                    <summary>詳細設定（従来UI）</summary>
                    
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
                </details>
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
            
            // Initialize on page load
            document.addEventListener('DOMContentLoaded', () => {
                // Check URL for mission_id
                const params = new URLSearchParams(window.location.search);
                const missionIdFromUrl = params.get('mission_id');
                if (missionIdFromUrl) {
                    const parsedId = parseInt(missionIdFromUrl, 10);
                    // Validate mission_id from URL (補強②)
                    if (!isNaN(parsedId) && parsedId > 0) {
                        currentMissionId = parsedId;
                        updateMissionStatusDisplay();
                        startPolling();
                        loadMessages();
                    } else {
                        console.error('Invalid mission_id in URL:', missionIdFromUrl);
                        showError('URLのmission_idが無効です');
                    }
                } else {
                    updateMissionStatusDisplay();
                }
            });
            
            // Chat functions
            async function loadMessages() {
                if (!currentMissionId) {
                    return;
                }
                
                try {
                    const response = await fetch(`/missions/${currentMissionId}/messages`);
                    if (!response.ok) {
                        throw new Error(`HTTP ${response.status}`);
                    }
                    
                    const data = await response.json();
                    renderMessages(data.messages);
                    hideError();
                } catch (error) {
                    console.error('Failed to load messages:', error);
                    showError('メッセージの取得に失敗しました: ' + error.message);
                }
            }
            
            function renderMessages(messages) {
                const historyDiv = document.getElementById('chatHistory');
                
                if (!messages || messages.length === 0) {
                    historyDiv.innerHTML = '<p style="color: #999; text-align: center;">メッセージがありません</p>';
                    return;
                }
                
                historyDiv.innerHTML = messages.map(msg => {
                    const role = msg.role || 'system';
                    const content = msg.content || '';
                    const time = msg.created_at || '';
                                        // Render attachments if present
                    let attachmentsHtml = '';
                    if (msg.attachments_json) {
                        let attachments = [];
                        
                        // Parse JSON string if needed
                        if (typeof msg.attachments_json === 'string') {
                            try {
                                attachments = JSON.parse(msg.attachments_json);
                            } catch (e) {
                                console.error('Failed to parse attachments_json:', e);
                                attachments = [msg.attachments_json]; // Fallback
                            }
                        } else if (Array.isArray(msg.attachments_json)) {
                            attachments = msg.attachments_json;
                        }
                        
                        if (attachments.length > 0) {
                            attachmentsHtml = '<div style="margin-top: 8px;">' +
                                attachments.map(id => 
                                    `<div class="attachment-chip">📎 ${id}</div>`
                                ).join('') +
                            '</div>';
                        }
                    }
                    
                    // Add trace icon (P2)
                    const traceIcon = `<button class="trace-btn" onclick="showTrace(${msg.id})" title="Trace表示">🧾</button>`;
                    
                    return `
                        <div class="chat-message ${role}">
                            <div class="chat-role">${role} ${traceIcon}</div>
                            <div class="chat-content">${escapeHtml(content)}</div>
                            ${attachmentsHtml}
                            ${time ? `<div class="chat-time">${time}</div>` : ''}
                        </div>
                    `;
                }).join('');
                
                // Scroll to bottom
                historyDiv.scrollTop = historyDiv.scrollHeight;
            }
            
            function escapeHtml(text) {
                const div = document.createElement('div');
                div.textContent = text;
                return div.innerHTML;
            }
            
            // Attachment state and functions
            let pendingAttachments = []; // {upload_id, filename, size}
            
            function renderPendingAttachments() {
                const container = document.getElementById('chatAttachments');
                
                if (pendingAttachments.length === 0) {
                    container.innerHTML = '';
                    return;
                }
                
                container.innerHTML = pendingAttachments.map((att, index) => `
                    <div class="attachment-chip">
                        📎 ${att.filename || att.upload_id}
                        <span class="remove-btn" onclick="removeAttachment(${index})">✕</span>
                    </div>
                `).join('');
            }
            
            function removeAttachment(index) {
                pendingAttachments.splice(index, 1);
                renderPendingAttachments();
            }
            
            async function uploadAndAttach(files) {
                if (!files || files.length === 0) return;
                
                for (const file of files) {
                    try {
                        const formData = new FormData();
                        formData.append('file', file);
                        
                        const response = await fetch('/upload', {
                            method: 'POST',
                            body: formData
                        });
                        
                        if (!response.ok) {
                            const error = await response.json();
                            throw new Error(error.detail || 'Upload failed');
                        }
                        
                        const data = await response.json();
                        pendingAttachments.push({
                            upload_id: data.upload_id,
                            filename: data.filename,
                            size: data.size
                        });
                        
                        renderPendingAttachments();
                        hideError();
                        
                    } catch (error) {
                        console.error('Upload error:', error);
                        showError('アップロードエラー: ' + error.message);
                    }
                }
            }
            
            async function sendMessage() {
                const input = document.getElementById('chatMessageInput');
                const content = input.value.trim();
                
                if (!content) {
                    return;
                }
                
                const sendBtn = document.getElementById('chatSendBtn');
                sendBtn.disabled = true;
                sendBtn.textContent = '送信中...';
                
                try {
                    // Auto-create mission if not exists
                    if (!currentMissionId) {
                        const createResponse = await fetch('/missions', {
                            method: 'POST',
                            headers: { 'Content-Type': 'application/json' },
                            body: JSON.stringify({
                                title: '',  // Server auto-generates from first message
                                description: content,
                                attachments: pendingAttachments.map(a => a.upload_id)
                            })
                        });
                        
                        if (!createResponse.ok) {
                            throw new Error(`ミッション作成失敗: HTTP ${createResponse.status}`);
                        }
                        
                        const createData = await createResponse.json();
                        
                        // Validate mission_id (補強②)
                        if (!createData.mission_id || typeof createData.mission_id !== 'number') {
                            throw new Error('ミッション作成失敗: 無効なmission_idが返されました');
                        }
                        
                        currentMissionId = createData.mission_id;
                        
                        // Update URL
                        history.replaceState({}, '', `/console?mission_id=${currentMissionId}`);
                        
                        // Update mission status display
                        updateMissionStatusDisplay();
                        
                        // Start polling (with guard)
                        startPolling();
                    }
                    
                    // Send message
                    const response = await fetch(`/missions/${currentMissionId}/messages`, {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({
                            content: content,
                            attachment_ids: pendingAttachments.map(a => a.upload_id)
                        })
                    });
                    
                    if (!response.ok) {
                        throw new Error(`HTTP ${response.status}`);
                    }
                    
                    // Clear input and attachments
                    input.value = '';
                    input.style.height = ''; // Reset textarea height
                    pendingAttachments = [];
                    renderPendingAttachments();
                    
                    // Reload messages
                    await loadMessages();
                    hideError();
                    
                } catch (error) {
                    console.error('Failed to send message:', error);
                    showError('メッセージの送信に失敗しました: ' + error.message);
                } finally {
                    sendBtn.disabled = false;
                    sendBtn.textContent = '送信';
                }
            }
            
            function updateMissionStatusDisplay() {
                const statusDiv = document.getElementById('missionStatusDisplay');
                if (currentMissionId) {
                    statusDiv.innerHTML = `<span style="color: #666;">現在のミッション: #${currentMissionId}</span>`;
                } else {
                    statusDiv.innerHTML = `<span style="color: #999;">未選択（最初の送信で自動作成されます）<br><small style="font-size: 11px;">※初回メッセージはミッション内容としても使用されます</small></span>`;
                }
            }
            
            function showError(message) {
                const errorDiv = document.getElementById('chatError');
                errorDiv.textContent = message;
                errorDiv.classList.add('show');
            }
            
            function hideError() {
                const errorDiv = document.getElementById('chatError');
                errorDiv.classList.remove('show');
            }
            
            // Chat send button
            document.getElementById('chatSendBtn').addEventListener('click', sendMessage);
            
            // Enter to send (Shift+Enter for newline)
            document.getElementById('chatMessageInput').addEventListener('keydown', (e) => {
                if (e.key === 'Enter' && !e.shiftKey) {
                    e.preventDefault();
                    sendMessage();
                }
            });
            
            // Attach button
            document.getElementById('chatAttachBtn').addEventListener('click', () => {
                document.getElementById('chatFileInput').click();
            });
            
            document.getElementById('chatFileInput').addEventListener('change', (e) => {
                uploadAndAttach(e.target.files);
                e.target.value = ''; // Reset input
            });
            
            // Drag and drop
            const chatRoot = document.getElementById('chatRoot');
            
            chatRoot.addEventListener('dragover', (e) => {
                e.preventDefault();
                chatRoot.classList.add('drag-over');
            });
            
            chatRoot.addEventListener('dragleave', (e) => {
                e.preventDefault();
                chatRoot.classList.remove('drag-over');
            });
            
            chatRoot.addEventListener('drop', (e) => {
                e.preventDefault();
                chatRoot.classList.remove('drag-over');
                
                if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
                    uploadAndAttach(e.dataTransfer.files);
                }
            });
            
            // Chat voice input
            let chatRecognition = null;
            let isChatListening = false;
            
            function startChatVoiceInput() {
                const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
                
                if (!SpeechRecognition) {
                    showError('このブラウザは音声入力に未対応です（Chrome/Edgeで利用可能）');
                    return;
                }
                
                const voiceBtn = document.getElementById('chatVoiceBtn');
                const chatInput = document.getElementById('chatMessageInput');
                
                // Toggle: stop if already listening
                if (isChatListening && chatRecognition) {
                    chatRecognition.stop();
                    isChatListening = false;
                    voiceBtn.classList.remove('listening');
                    return;
                }
                
                // Initialize recognition if not exists
                if (!chatRecognition) {
                    chatRecognition = new SpeechRecognition();
                    chatRecognition.lang = 'ja-JP';
                    chatRecognition.continuous = false;
                    chatRecognition.interimResults = false;
                    
                    chatRecognition.onresult = (event) => {
                        const transcript = event.results[0][0].transcript;
                        // Append to existing input (or set if empty)
                        chatInput.value = (chatInput.value.trim() ? chatInput.value.trim() + ' ' : '') + transcript;
                        hideError();
                    };
                    
                    chatRecognition.onerror = (event) => {
                        console.error('Voice recognition error:', event.error);
                        let errorMsg = '音声入力エラー: ';
                        switch (event.error) {
                            case 'no-speech':
                                errorMsg += '音声が検出されませんでした';
                                break;
                            case 'audio-capture':
                                errorMsg += 'マイクにアクセスできません';
                                break;
                            case 'not-allowed':
                                errorMsg += 'マイクの使用が許可されていません';
                                break;
                            default:
                                errorMsg += event.error;
                        }
                        showError(errorMsg);
                    };
                    
                    chatRecognition.onend = () => {
                        isChatListening = false;
                        voiceBtn.classList.remove('listening');
                    };
                }
                
                // Start recognition
                try {
                    chatRecognition.start();
                    isChatListening = true;
                    voiceBtn.classList.add('listening');
                    hideError();
                } catch (e) {
                    console.error('Failed to start recognition:', e);
                    showError('音声入力の開始に失敗しました');
                }
            }
            
            // Chat voice button event listener
            document.getElementById('chatVoiceBtn').addEventListener('click', startChatVoiceInput);
            
            // Legacy upload function
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
                uploadStatus.innerHTML = '<span style="color: #999;">アップロード中...</span>';
                
                try {
                    const formData = new FormData();
                    formData.append('file', file);
                    
                    const response = await fetch('/upload', {
                        method: 'POST',
                        body: formData
                    });
                    
                    if (!response.ok) {
                        const error = await response.json();
                        throw new Error(error.detail || 'Upload failed');
                    }
                    
                    const data = await response.json();
                    
                    // Add upload_id to attachments field
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
                const attachments = attachmentsText.split('\\n').filter(line => line.trim() !== '');
                
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
                    
                    // Load messages for chat UI
                    loadMessages();
                    
                } catch (error) {
                    alert('ミッション作成エラー: ' + error.message);
                    submitBtn.disabled = false;
                    submitBtn.textContent = 'ミッション作成';
                }
            });
            
            function startPolling() {
                // Polling guard (補強①): prevent double intervals
                if (pollInterval) {
                    console.log('Polling already active, skipping restart');
                    return;
                }
                
                // Poll every 1 second
                pollInterval = setInterval(() => {
                    updateStatus();
                    loadMessages(); // Also update chat messages
                }, 1000);
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
            
            // Trace modal functions (P2)
            async function showTrace(messageId) {
                const modal = document.getElementById('traceModal');
                const traceContent = document.getElementById('traceContent');
                
                traceContent.textContent = 'Loading trace...';
                modal.classList.add('show');
                
                // For MVP: show placeholder (no actual trace API yet)
                // In future: fetch(`/missions/${currentMissionId}/messages/${messageId}/trace`)
                setTimeout(() => {
                    traceContent.textContent = `Trace for message #${messageId}\n\nStatus: トレース未実装\n\n理由: Phase 3 Lite では最小導線のみ実装。\n実際のトレース取得APIは今後実装予定。\n\n（DRY_RUN想定のため、LLM呼び出しトレースは存在しません）`;
                }, 100);
            }
            
            function hideTraceModal() {
                const modal = document.getElementById('traceModal');
                modal.classList.remove('show');
            }
            
            // Close modal on click outside
            document.addEventListener('click', (e) => {
                const modal = document.getElementById('traceModal');
                if (e.target === modal) {
                    hideTraceModal();
                }
            });
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
