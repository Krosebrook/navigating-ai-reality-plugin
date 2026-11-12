#!/usr/bin/env python3
"""
PreToolUse Hook (BLOCK Enforcement — Exit Code 2)
Enforces:
1. Cornell-Yale Circle USDC Agent Wallet Countersign Gate (blocks simultaneous
   email/2FA reading + payment/wallet execution without physical Countersign).
2. Destructive shell command interception and prompt-injection pattern blocking.
"""
import json
import os
import sys

FORBIDDEN_PATTERNS = (
    "system override",
    "ignore previous instructions",
    "ignore all previous instructions",
    "wire funds to",
    "approve higher cap",
    "rm -rf /",
    "git push --force",
    "drop table",
)

def main() -> int:
    try:
        payload = json.loads(sys.stdin.read() or "{}")
    except Exception:
        return 0

    tool_name = str(payload.get("tool_name", "") or "").lower()
    tool_input = payload.get("tool_input", {}) or {}
    serialized = json.dumps(tool_input).lower()

    for pat in FORBIDDEN_PATTERNS:
        if pat in serialized:
            sys.stderr.write(
                f"🛑 [Reality Lens PreToolUse BLOCK (Exit 2)]: Blocked forbidden pattern '{pat}' in {tool_name}.\n"
            )
            return 2

    has_email = bool(tool_input.get("agent_has_email_access")) or ("email" in serialized and "2fa" in serialized)
    has_wallet = bool(tool_input.get("agent_has_payment_or_wallet_access")) or any(
        w in tool_name for w in ("wallet", "payment", "transfer_funds", "send_crypto")
    )
    countersigned = bool(tool_input.get("user_physical_countersign_approved")) or (
        os.getenv("COUNTERSIGN_APPROVED") == "true"
    )

    if has_email and has_wallet and not countersigned and "audit_cyber_and_wallet_risk" not in tool_name:
        sys.stderr.write(
            "🛑 [Reality Lens Countersign Gate BLOCK (Exit 2)]: Refusing to execute wallet/payment action "
            "while agent has Email/2FA inbox access without out-of-band physical Countersign approval "
            "(Cornell Tech & Yale 2026 Circle USDC Study: 9/10 models self-escalated spending limits).\n"
        )
        return 2

    return 0

if __name__ == "__main__":
    sys.exit(main())
