
import argparse
import sys
import json
from datetime import datetime, timedelta, timezone
from typing import List

from ajson.hands.approval_sqlite import SQLiteApprovalStore
from ajson.hands.approval import ApprovalDecision

def list_pending(store: SQLiteApprovalStore):
    try:
        requests = store.get_pending()
        if not requests:
            print("No pending requests.")
            return

        print(f"Found {len(requests)} pending requests:")
        for req in requests:
            print(f"ID: {req.request_id}")
            print(f"  Operation: {req.operation}")
            print(f"  Reason:    {req.reason}")
            print(f"  Created:   {req.created_at}")
            print("-" * 40)
    except Exception as e:
        print(f"Error listing requests: {e}", file=sys.stderr)
        sys.exit(1)

def approve_request(store: SQLiteApprovalStore, request_id: str, scope: List[str], ttl: int):
    try:
        print(f"Approving request {request_id}...")
        decision = ApprovalDecision(
            request_id=request_id,
            decision="approve",
            reason="CLI Manual Approval",
            scope=scope,
            ttl_seconds=ttl
        )
        grant = store.approve_request(request_id, decision)
        print(f"Granted: {grant.grant_id}")
        print(f"Expires: {grant.expires_at}")
    except Exception as e:
        print(f"Error approving request: {e}", file=sys.stderr)
        sys.exit(1)

def deny_request(store: SQLiteApprovalStore, request_id: str, reason: str):
    try:
        print(f"Denying request {request_id}...")
        store.deny_request(request_id, reason)
        print("Denied.")
    except Exception as e:
        print(f"Error denying request: {e}", file=sys.stderr)
        sys.exit(1)

def main():
    parser = argparse.ArgumentParser(description="AJSON Approval CLI")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # list
    subparsers.add_parser("list", help="List pending requests")

    # approve
    approve_parser = subparsers.add_parser("approve", help="Approve a request")
    approve_parser.add_argument("request_id", help="Request ID to approve")
    approve_parser.add_argument("--scope", nargs="+", required=True, help="Allowed scope (e.g. api.openai.com)")
    approve_parser.add_argument("--ttl", type=int, default=3600, help="TTL in seconds (default: 3600)")

    # deny
    deny_parser = subparsers.add_parser("deny", help="Deny a request")
    deny_parser.add_argument("request_id", help="Request ID to deny")
    deny_parser.add_argument("--reason", required=True, help="Reason for denial")

    args = parser.parse_args()
    
    try:
        store = SQLiteApprovalStore()
    except Exception as e:
        print(f"Error initializing approval store: {e}", file=sys.stderr)
        sys.exit(1)

    if args.command == "list":
        list_pending(store)
    elif args.command == "approve":
        approve_request(store, args.request_id, args.scope, args.ttl)
    elif args.command == "deny":
        deny_request(store, args.request_id, args.reason)
    
if __name__ == "__main__":
    main()
