"""
Tests for file upload functionality
"""
import pytest
from fastapi.testclient import TestClient
from ajson.app import app
from ajson import db
import io


client = TestClient(app)


def test_upload_ok():
    """Test successful file upload"""
    # Create a test file
    file_content = b"This is a test file content"
    file = io.BytesIO(file_content)
    
    # Upload
    response = client.post(
        "/upload",
        files={"file": ("test.txt", file, "text/plain")}
    )
    
    assert response.status_code == 200
    data = response.json()
    
    assert "upload_id" in data
    assert data["filename"] == "test.txt"
    assert data["size"] == len(file_content)
    
    # Verify in database
    upload = db.get_upload(data["upload_id"])
    assert upload is not None
    assert upload["original_name"] == "test.txt"


def test_upload_reject_ext():
    """Test rejection of disallowed file extension"""
    file_content = b"Malicious content"
    file = io.BytesIO(file_content)
    
    # Try to upload .exe file
    response = client.post(
        "/upload",
        files={"file": ("malware.exe", file, "application/x-msdownload")}
    )
    
    assert response.status_code == 400
    data = response.json()
    assert "not allowed" in data["detail"].lower()


def test_upload_reject_size():
    """Test rejection of file exceeding size limit"""
    # Create a file larger than 50MB
    large_content = b"X" * (51 * 1024 * 1024)  # 51MB
    file = io.BytesIO(large_content)
    
    response = client.post(
        "/upload",
        files={"file": ("large.txt", file, "text/plain")}
    )
    
    assert response.status_code == 413
    data = response.json()
    assert "exceeds maximum" in data["detail"].lower()


def test_upload_path_traversal_prevention():
    """Test that path traversal attempts are prevented"""
    file_content = b"Test content"
    file = io.BytesIO(file_content)
    
    # Try to upload with path traversal attempt
    response = client.post(
        "/upload",
        files={"file": ("../../etc/passwd.txt", file, "text/plain")}
    )
    
    assert response.status_code == 200
    data = response.json()
    
    # Filename should be sanitized to just the basename
    assert data["filename"] == "passwd.txt"
    
    # Verify stored_name doesn't contain path components
    upload = db.get_upload(data["upload_id"])
    assert "/" not in upload["stored_name"]
    assert "\\\\" not in upload["stored_name"]
