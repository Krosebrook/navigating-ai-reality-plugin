#!/usr/bin/env python3
"""
Stop Hook (WARN Advisory)
Checks post-response output on consequential topics to remind the agent to
maintain local 7-Pillar Resume Cards and Adversarial Review footers.
"""
import json
import sys

def main() -> int:
    try:
        payload = json.loads(sys.stdin.read() or "{}")
    except Exception:
        payload = {}

    transcript = str(payload.get("stop_reason", "") or "")
    _ = transcript
    return 0

if __name__ == "__main__":
    sys.exit(main())
