#!/usr/bin/env python3
"""
Standalone CLI Runner for Reality Lens (`navigating-ai-reality`)
Usage:
    python3 cli_reality_check.py propel --goal "Audit my medical bill"
    python3 cli_reality_check.py ioed --topic "How LLMs work" --explanation "Token loop..."
    python3 cli_reality_check.py sycophancy --text "Brilliant genius idea!" --streak 3
    python3 cli_reality_check.py safety --scenario "Email + USDC wallet" --email --wallet
"""
import argparse
import asyncio
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import reality_lens_mcp_server as srv


async def _dispatch(args: argparse.Namespace) -> dict:
    if args.cmd == "propel":
        return await srv.reality_lens_propel_goal(args.goal, args.domain)
    if args.cmd == "scaffold":
        return await srv.reality_lens_build_scaffold(args.goal, args.interruption)
    if args.cmd == "ioed":
        return await srv.reality_lens_puncture_ioed(args.topic, args.explanation, args.confidence)
    if args.cmd == "sycophancy":
        return await srv.reality_lens_break_sycophancy(args.text, args.streak, args.high_stakes)
    if args.cmd == "safety":
        return await srv.reality_lens_audit_safety(
            args.scenario, args.email, args.wallet, args.fintech, args.countersign
        )
    if args.cmd == "horizon":
        return await srv.reality_lens_horizon_radar(args.topic)
    return {"tools": await srv.reality_lens_search_tools(args.query)}


def main() -> int:
    parser = argparse.ArgumentParser(description="Reality Lens CLI for Non-Technical Citizens")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_prop = sub.add_parser("propel")
    p_prop.add_argument("--goal", required=True)
    p_prop.add_argument("--domain", default="verifiable")

    p_scaf = sub.add_parser("scaffold")
    p_scaf.add_argument("--goal", required=True)
    p_scaf.add_argument("--interruption", default="high")

    p_ioed = sub.add_parser("ioed")
    p_ioed.add_argument("--topic", required=True)
    p_ioed.add_argument("--explanation", default="I read the summary.")
    p_ioed.add_argument("--confidence", type=int, default=8)

    p_syc = sub.add_parser("sycophancy")
    p_syc.add_argument("--text", required=True)
    p_syc.add_argument("--streak", type=int, default=1)
    p_syc.add_argument("--high-stakes", action="store_true")

    p_safe = sub.add_parser("safety")
    p_safe.add_argument("--scenario", required=True)
    p_safe.add_argument("--email", action="store_true")
    p_safe.add_argument("--wallet", action="store_true")
    p_safe.add_argument("--fintech", action="store_true")
    p_safe.add_argument("--countersign", action="store_true")

    p_hor = sub.add_parser("horizon")
    p_hor.add_argument("--topic", default="all")

    p_search = sub.add_parser("search")
    p_search.add_argument("--query", default="all")

    args = parser.parse_args()
    res = asyncio.run(_dispatch(args))
    print(json.dumps(res, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
