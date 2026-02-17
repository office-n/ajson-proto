
import argparse
import sys
import json
import os
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


def cockpit_start():
    try:
        from ajson.cli.cockpit import Cockpit
        ui = Cockpit()
        ui.run()
    except Exception as e:
        print(f"Error starting cockpit: {e}", file=sys.stderr)
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

    # allowlist
    allowlist_parser = subparsers.add_parser("allowlist", help="Manage allowlist")
    allowlist_subs = allowlist_parser.add_subparsers(dest="allowlist_command", required=True)
    
    # allowlist add
    allowlist_add = allowlist_subs.add_parser("add", help="Add a rule to allowlist")
    allowlist_add.add_argument("host", help="Host pattern (e.g. *.example.com)")
    allowlist_add.add_argument("port", type=int, help="Port number (0 for any)")
    allowlist_add.add_argument("--reason", required=True, help="Reason for allowing")

    # cockpit
    subparsers.add_parser("cockpit", help="Start M1 Cockpit MVP")

    args = parser.parse_args()
    
    if args.command == "cockpit":
        cockpit_start()
        return

    try:
        db_path = os.environ.get("APPROVAL_STORE_DB", "data/approvals.db")
        store = SQLiteApprovalStore(db_path=db_path)
    except Exception as e:
        print(f"Error initializing approval store: {e}", file=sys.stderr)
        sys.exit(1)

    if args.command == "list":
        list_pending(store)
    elif args.command == "approve":
        approve_request(store, args.request_id, args.scope, args.ttl)
    elif args.command == "deny":
        deny_request(store, args.request_id, args.reason)
    elif args.command == "allowlist":
        if args.allowlist_command == "add":
            from ajson.hands.allowlist import Allowlist
            allowlist_mgr = Allowlist(db_path=store.db_path)
            allowlist_mgr.add_rule(args.host, args.port, args.reason)
            print(f"Added allowlist rule: {args.host}:{args.port}")
    
if __name__ == "__main__":
    main()
