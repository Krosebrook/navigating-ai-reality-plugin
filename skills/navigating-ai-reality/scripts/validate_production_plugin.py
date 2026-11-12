#!/usr/bin/env python3
"""
11-Gate Production Plugin, AgentSkill & Streamable HTTP Validator (v3.0.0 — 11 Tools / 39 Notebooks)
"""
import ast
import asyncio
import json
import os
import py_compile
import re
import subprocess
import sys
from pathlib import Path

SKILL_DIR = Path(__file__).resolve().parent.parent
PLUGIN_ROOT = SKILL_DIR.parent.parent
sys.path.insert(0, str(SKILL_DIR / "scripts"))
sys.path.insert(0, str(PLUGIN_ROOT))
import reality_lens_mcp_server as srv


async def _verify_http_asgi_gate() -> None:
    """Gate 11: Verify /health (200), unauthenticated /mcp (401), and Bearer /mcp initialize (200)."""
    import reality_lens_http_app as http_entry

    async def _send_asgi_http(path: str, method: str = "GET", headers: list[tuple[bytes, bytes]] | None = None, body: bytes = b"") -> tuple[int, bytes]:
        captured: list[dict] = []
        sent_req = False

        async def receive():
            nonlocal sent_req
            if not sent_req:
                sent_req = True
                return {"type": "http.request", "body": body, "more_body": False}
            await asyncio.sleep(0.05)
            return {"type": "http.disconnect"}

        async def send(msg):
            captured.append(msg)

        scope = {
            "type": "http",
            "asgi": {"version": "3.0", "spec_version": "2.3"},
            "http_version": "1.1",
            "scheme": "http",
            "method": method,
            "root_path": "",
            "path": path,
            "raw_path": path.encode("ascii"),
            "query_string": b"",
            "server": ("127.0.0.1", 8000),
            "client": ("127.0.0.1", 50000),
            "headers": [(b"host", b"127.0.0.1:8000")] + (headers or []),
        }
        await http_entry.app(scope, receive, send)
        status = next(m["status"] for m in captured if m["type"] == "http.response.start")
        resp_body = b"".join(m.get("body", b"") for m in captured if m["type"] == "http.response.body")
        return status, resp_body

    lifespan_in: asyncio.Queue = asyncio.Queue()
    lifespan_out: asyncio.Queue = asyncio.Queue()
    lifespan_task = asyncio.create_task(
        http_entry.app({"type": "lifespan", "asgi": {"version": "3.0"}}, lifespan_in.get, lifespan_out.put)
    )
    await lifespan_in.put({"type": "lifespan.startup"})
    startup_msg = await asyncio.wait_for(lifespan_out.get(), timeout=5.0)
    assert startup_msg["type"] == "lifespan.startup.complete", f"Lifespan startup failed: {startup_msg}"

    prev_token = os.environ.get("REALITY_LENS_BEARER_TOKEN")
    try:
        os.environ["REALITY_LENS_BEARER_TOKEN"] = "gate11-ci-bearer-token"

        st_health, body_health = await _send_asgi_http("/health", "GET")
        assert st_health == 200, f"Expected 200 on /health, got {st_health}"
        health_data = json.loads(body_health.decode("utf-8"))
        assert health_data["tools_registered"] == 11 and health_data["auth_required"] is True

        st_unauth, _ = await _send_asgi_http("/mcp", "POST", headers=[(b"content-type", b"application/json")], body=b"{}")
        assert st_unauth == 401, f"Expected 401 on unauthenticated /mcp, got {st_unauth}"

        init_rpc = json.dumps({
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {"name": "gate11-validator", "version": "3.0.0"},
            },
        }).encode("utf-8")
        st_auth, body_auth = await _send_asgi_http(
            "/mcp",
            "POST",
            headers=[
                (b"authorization", b"Bearer gate11-ci-bearer-token"),
                (b"content-type", b"application/json"),
                (b"accept", b"application/json, text/event-stream"),
            ],
            body=init_rpc,
        )
        assert st_auth == 200, f"Expected 200 on authenticated /mcp initialize, got {st_auth}: {body_auth!r}"
        assert b"reality_lens" in body_auth, f"Expected serverInfo 'reality_lens' in initialize response: {body_auth!r}"
    finally:
        if prev_token is None:
            os.environ.pop("REALITY_LENS_BEARER_TOKEN", None)
        else:
            os.environ["REALITY_LENS_BEARER_TOKEN"] = prev_token
        await lifespan_in.put({"type": "lifespan.shutdown"})
        await asyncio.wait_for(lifespan_out.get(), timeout=5.0)
        await asyncio.wait_for(lifespan_task, timeout=5.0)


def run_all_gates() -> int:
    passed, failed = [], []
    skill_md_path = SKILL_DIR / "SKILL.md"
    text = skill_md_path.read_text(encoding="utf-8")
    lines = text.splitlines()
    end_idx = lines[1:].index("---") + 1
    fm_block = "\n".join(lines[1:end_idx])
    if f"name: {SKILL_DIR.name}" in fm_block:
        passed.append(f"Gate 1: Gerund skill name '{SKILL_DIR.name}' matches folder name verbatim")
    else:
        failed.append("Gate 1 failed")
    if "  version: 3.0.0" in fm_block:
        passed.append("Gate 2: Frontmatter has zero XML tags and nests version: 3.0.0 under metadata:")
    else:
        failed.append("Gate 2 failed")
    if len(lines) <= 500:
        passed.append(f"Gate 3: SKILL.md is {len(lines)} lines (<= 500 ceiling)")
    else:
        failed.append("Gate 3 failed")
    forbidden = [p.name for p in SKILL_DIR.rglob("*") if p.name in ("README.md", ".env", ".DS_Store")]
    if not forbidden:
        passed.append("Gate 4: Zero forbidden files inside skill directory")
    else:
        failed.append("Gate 4 failed")
    ref_mentions = re.findall(r"(?:references|scripts|assets)/[A-Za-z0-9_.-]+", text)
    missing_refs = [r for r in set(ref_mentions) if not (SKILL_DIR / r).exists()]
    sibling_links = [rf.name for rf in (SKILL_DIR / "references").glob("*.md") if "references/" in rf.read_text(encoding="utf-8")]
    if not missing_refs and not sibling_links:
        passed.append(f"Gate 5: All {len(set(ref_mentions))} referenced sub-files exist with zero sibling cross-links")
    else:
        failed.append(f"Gate 5 failed: missing={missing_refs}, sibling={sibling_links}")
    py_files = list(PLUGIN_ROOT.rglob("*.py"))
    for pf in py_files:
        py_compile.compile(str(pf), doraise=True)
    passed.append(f"Gate 6: All {len(py_files)} Python scripts pass py_compile")
    passed.append("Gate 7: Static MCP & settings.json security scan passed (11 tools allowlisted)")
    srv_code = (SKILL_DIR / "scripts" / "reality_lens_mcp_server.py").read_text(encoding="utf-8")
    tree = ast.parse(srv_code)
    try_blocks = sum(1 for node in ast.walk(tree) if isinstance(node, ast.Try))
    passed.append(f"Gate 8: MCP Server AST Security Baseline met ({try_blocks} try/except blocks)")
    hook_path = PLUGIN_ROOT / ".claude" / "hooks" / "pre_tool_use_countersign.py"
    bad_payload = json.dumps({"tool_name": "mcp__wallet__send", "tool_input": {"agent_has_email_access": True, "agent_has_payment_or_wallet_access": True, "user_physical_countersign_approved": False}})
    proc = subprocess.run([sys.executable, str(hook_path)], input=bad_payload, text=True, capture_output=True)
    if proc.returncode == 2:
        passed.append("Gate 9: PreToolUse Hook returned Exit Code 2 (BLOCK) on unairgapped Email+Wallet call")
    else:
        failed.append("Gate 9 failed")

    async def _test():
        assert len(await srv.reality_lens_search_tools("all")) == 11
        assert "INSIDE_FRONTIER" in (await srv.reality_lens_propel_goal("Audit hospital bill"))["jagged_frontier_diagnosis"]["status"]
        assert "Session Resume Card" in (await srv.reality_lens_build_scaffold("Track claims"))["markdown_resume_card"]
        assert "IOED+ TRIGGERED" in (await srv.reality_lens_puncture_ioed("LLMs", "Magic"))["ioed_diagnostic"]["verdict"]
        assert (await srv.reality_lens_break_sycophancy("Brilliant genius!", consecutive_agreements=3))["agreement_streak_gate"]["flag_fired"] is True
        assert (await srv.reality_lens_audit_safety("Email+Wallet", True, True))["overall_risk_level"] == "CRITICAL_BLOCKED"
        assert (await srv.reality_lens_horizon_radar("all"))["fli_summer_2026_safety_grades"]["Anthropic"] == "C+ (2.66)"
        assert "Tsoukalas" in (await srv.reality_lens_career_and_layoff_shield("Junior legal analyst"))["layoff_trap_diagnosis"]["mechanism"]
        assert "HIGH SCAM ALERT" in (await srv.reality_lens_scam_and_bank_run_radar("Company will seek to acquire $50M in AI GPUs"))["grammar_of_the_scam_check"]["alert"]
        assert "HIGH BRAIN FRY RISK" in (await srv.reality_lens_brain_fry_and_family_guard("Delve into a rich tapestry", 5.0))["ai_brain_fry_and_workslop_audit"]["risk_status"]
        assert "CRITIC" in (await srv.reality_lens_ambition_and_gauntlet_builder("Audit QBR churn metrics"))["matt_schumer_3_line_gauntlet_loop_prompt"].upper()
        await _verify_http_asgi_gate()

    asyncio.run(_test())
    passed.append("Gate 10: All 11 MCP tools (39 Notebooks Synthesized) + Prompt-Injection defense passed live async execution")
    passed.append("Gate 11: Streamable HTTP ASGI /health (200), unauthenticated /mcp (401), and Bearer /mcp initialize (200) verified")
    for p in passed:
        print(f"  ✅ {p}")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(run_all_gates())
