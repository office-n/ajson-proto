import os
import shutil
from ajson.core.worktree import WorktreeManager
from ajson.hands.runner import ToolRunner

def test_m2_mvp():
    print("--- Starting M2 MVP Verification ---")
    
    # Init
    wm = WorktreeManager("worktrees_test")
    runner = ToolRunner(dry_run=False) # Enable execution
    task_id = "test-task-123"
    work_path = wm.create(task_id)
    print(f"[1] Created Worktree: {work_path}")
    
    # 1. Write file
    print("[2] Testing write_worktree...")
    res = runner.execute_tool("write_worktree", {
        "worktree_root": work_path,
        "path": "test.txt",
        "content": "Hello M2"
    })
    print(f"    Result: {res['status']}, {res.get('output', res.get('error'))}")
    assert res['status'] == "success"
    
    # 2. List files
    print("[3] Testing ls_worktree...")
    res = runner.execute_tool("ls_worktree", {
        "worktree_root": work_path,
        "path": "."
    })
    print(f"    Result: {res['status']}, {res.get('output', res.get('error'))}")
    assert "test.txt" in res['output']
    
    # 3. Read file
    print("[4] Testing read_worktree...")
    res = runner.execute_tool("read_worktree", {
        "worktree_root": work_path,
        "path": "test.txt"
    })
    print(f"    Result: {res['status']}, {res.get('output', res.get('error'))}")
    assert "Hello M2" in res['output']
    
    # 4. Security Violation (Targeting outside)
    print("[5] Testing Security Guard (Accessing /tmp/evil.txt)...")
    res = runner.execute_tool("write_worktree", {
        "worktree_root": work_path,
        "path": "../../evil.txt",
        "content": "Hacked"
    })
    print(f"    Result: {res['status']}, {res.get('error')}")
    assert res['status'] == "error"
    assert "Security Violation" in res['error']

    # 5. Remove (Trash)
    print("[6] Testing remove_worktree (Trash move)...")
    res = runner.execute_tool("remove_worktree", {
        "worktree_root": work_path,
        "path": "test.txt",
        "permanent": False
    })
    print(f"    Result: {res['status']}, {res.get('output')}")
    assert res['status'] == "success"
    assert os.path.exists(os.path.join(work_path, ".trash", "test.txt"))

    print("--- M2 MVP Verification SUCCESS ---")
    
    # Cleanup
    shutil.rmtree("worktrees_test")

if __name__ == "__main__":
    try:
        test_m2_mvp()
    except Exception as e:
        print(f"FAILED: {e}")
        import traceback
        traceback.print_exc()
        exit(1)
