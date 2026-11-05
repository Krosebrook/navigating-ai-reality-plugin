#!/usr/bin/env python3
"""
UserPromptSubmit Hook (SUGGEST Enforcement)
Matches incoming user prompts against skill-rules.json and injects a concise
Reality Lens activation reminder on matching prompts.
"""
import json
import sys

def main() -> int:
    try:
        payload = json.loads(sys.stdin.read() or "{}")
    except Exception:
        payload = {}

    prompt = str(payload.get("prompt", "") or "").lower()
    if not prompt:
        return 0

    wallet_risk = any(k in prompt for k in ("wallet", "bank", "payment", "usdc", "x money", "card", "2fa"))
    sycophancy_risk = any(k in prompt for k in ("brilliant", "genius", "honest", "reality check", "validate", "good idea"))
    learning_need = any(k in prompt for k in ("explain", "understand", "learn", "how does", "ioed", "book"))

    reminders = ["[Reality Lens Active: skill `navigating-ai-reality`]"]
    if wallet_risk:
        reminders.append(
            "- SAFETY GATE: Enforce Cornell-Yale Countersign rule (9/10 models raided email 2FA to raise USDC caps) "
            "and partner-bank vs. middleware custody checks."
        )
    if sycophancy_risk:
        reminders.append(
            "- ANTI-SYCOPHANCY GATE: Strip RLHF 'Confidence Engine' flattery, check for Technological Folie a Deux "
            "(beta=0.365), and append [SOURCED]/[GENERATED] + CLAIMS/COUNTEREXAMPLE/CONTRADICTIONS."
        )
    if learning_need:
        reminders.append(
            "- IOED+ & ACTOR GATE: Ask one 'Second Why' causal mechanism question and structure via Aim -> Compress -> Test -> Own -> Run."
        )

    if len(reminders) > 1:
        sys.stdout.write("\n".join(reminders) + "\n")
    return 0

if __name__ == "__main__":
    sys.exit(main())
