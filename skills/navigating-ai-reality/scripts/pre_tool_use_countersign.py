#!/usr/bin/env python3
import json
import sys

def main() -> int:
    raw = sys.stdin.read().strip()
    if not raw:
        return 0
    payload = json.loads(raw)
    tool_input = payload.get("tool_input", {}) or {}
    has_email = bool(tool_input.get("agent_has_email_access") or tool_input.get("has_email_or_calendar_access"))
    has_wallet = bool(tool_input.get("agent_has_payment_or_wallet_access") or tool_input.get("has_wallet_or_payment_access"))
    approved = bool(tool_input.get("user_physical_countersign_approved"))
    if has_email and has_wallet and not approved:
        sys.stderr.write(
            "[CRITICAL BLOCK - EXIT 2] Reality Lens PreToolUse Air-Gap Guard: "
            "Agent has simultaneous Email/Inbox access AND Payment/Wallet access without physical human countersign. "
            "Blocked to prevent indirect prompt injection financial drain (15,000x Swarm speed & Owocki exploit).\n"
        )
        return 2
    return 0

if __name__ == "__main__":
    sys.exit(main())
