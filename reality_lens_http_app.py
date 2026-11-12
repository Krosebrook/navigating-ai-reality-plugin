#!/usr/bin/env python3
"""
Reality Lens v3.0.0 — Remote Streamable HTTP ASGI Entrypoint
============================================================
Exposes all 11 Reality Lens MCP tools over MCP Streamable HTTP at `/mcp`
with a `<2s` `/health` probe, forwarded-TLS header support, DNS-rebinding/Host
compatibility for cloud hosts (Render, Cloud Run, Railway, Fly.io), and optional
constant-time Bearer token authentication (`REALITY_LENS_BEARER_TOKEN`).
"""
from __future__ import annotations

import hmac
import json
import os
import sys
from pathlib import Path
from typing import Any, Callable

# Ensure reality_lens_mcp_server is importable from repo root or scripts/
REPO_ROOT = Path(__file__).resolve().parent
SCRIPTS_DIR = REPO_ROOT / "skills" / "navigating-ai-reality" / "scripts"
if SCRIPTS_DIR.exists() and str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

import reality_lens_mcp_server as srv  # noqa: E402


def _build_inner_mcp_asgi_app() -> Any:
    """Build the underlying Streamable HTTP ASGI app across FastMCP v2/v3 & MCP SDK."""
    sdk = getattr(srv.mcp, "_sdk", None)
    if sdk is not None:
        # Disable localhost-only Host header lock so Render/Cloud Run hostnames don't 421
        settings = getattr(sdk, "settings", None)
        if settings is not None:
            if hasattr(settings, "stateless_http"):
                settings.stateless_http = True
            if hasattr(settings, "host"):
                settings.host = "0.0.0.0"
            transport_sec = getattr(settings, "transport_security", None)
            if transport_sec is not None and hasattr(transport_sec, "enable_dns_rebinding_protection"):
                transport_sec.enable_dns_rebinding_protection = False

        # FastMCP 2.3+ / 3.x canonical ASGI factory
        if hasattr(sdk, "http_app"):
            try:
                return sdk.http_app(path="/mcp", stateless_http=True, transport="streamable-http")
            except TypeError:
                return sdk.http_app(path="/mcp")

        # Official `mcp.server.fastmcp` Python SDK ASGI factory
        if hasattr(sdk, "streamable_http_app"):
            return sdk.streamable_http_app()

    # Deterministic JSON-RPC 2.0 Streamable HTTP fallback if neither SDK HTTP helper is installed
    async def _minimal_jsonrpc_mcp_app(scope: dict[str, Any], receive: Callable, send: Callable) -> None:
        if scope["type"] == "lifespan":
            while True:
                msg = await receive()
                if msg["type"] == "lifespan.startup":
                    await send({"type": "lifespan.startup.complete"})
                elif msg["type"] == "lifespan.shutdown":
                    await send({"type": "lifespan.shutdown.complete"})
                    return
        if scope["type"] != "http":
            return
        body = b""
        while True:
            msg = await receive()
            body += msg.get("body", b"")
            if not msg.get("more_body", False):
                break
        try:
            req = json.loads(body.decode("utf-8") or "{}")
            req_id = req.get("id")
            method = req.get("method", "")
            params = req.get("params") or {}
            if method == "initialize":
                result = {
                    "protocolVersion": "2025-11-25",
                    "capabilities": {"tools": {}, "resources": {}},
                    "serverInfo": {"name": "reality_lens", "version": "3.0.0"},
                }
            elif method == "tools/list":
                result = {
                    "tools": [
                        {
                            "name": name,
                            "description": f"{meta['plain_name']} — {meta['summary']}",
                            "inputSchema": {"type": "object", "additionalProperties": True},
                        }
                        for name, meta in srv.TOOL_CATALOG.items()
                    ]
                }
            elif method == "tools/call":
                t_name = params.get("name", "")
                t_args = params.get("arguments") or {}
                out = await srv.mcp.call_tool(t_name, **t_args)
                result = {"content": [{"type": "text", "text": json.dumps(out, indent=2)}], "isError": False}
            else:
                result = {"status": "ok", "method": method}
            payload = json.dumps({"jsonrpc": "2.0", "id": req_id, "result": result}).encode("utf-8")
            status = 200
        except Exception as exc:
            payload = json.dumps(
                {"jsonrpc": "2.0", "id": None, "error": {"code": -32000, "message": str(exc)}}
            ).encode("utf-8")
            status = 400

        await send(
            {
                "type": "http.response.start",
                "status": status,
                "headers": [(b"content-type", b"application/json")],
            }
        )
        await send({"type": "http.response.body", "body": payload})

    return _minimal_jsonrpc_mcp_app


_inner_app = _build_inner_mcp_asgi_app()


async def _send_json(send: Callable, status: int, data: dict[str, Any], extra_headers: list[tuple[bytes, bytes]] | None = None) -> None:
    raw = json.dumps(data).encode("utf-8")
    headers = [
        (b"content-type", b"application/json"),
        (b"access-control-allow-origin", os.environ.get("REALITY_LENS_CORS_ORIGIN", "*").encode("utf-8")),
        (b"access-control-allow-headers", b"authorization, content-type, mcp-session-id, mcp-protocol-version"),
        (b"access-control-allow-methods", b"GET, POST, DELETE, OPTIONS"),
    ]
    if extra_headers:
        headers.extend(extra_headers)
    await send({"type": "http.response.start", "status": status, "headers": headers})
    await send({"type": "http.response.body", "body": raw})


async def app(scope: dict[str, Any], receive: Callable, send: Callable) -> None:
    """Production ASGI middleware wrapping `/health`, CORS preflight, Bearer auth, and `/mcp`."""
    if scope["type"] == "lifespan":
        if hasattr(_inner_app, "__call__"):
            try:
                await _inner_app(scope, receive, send)
                return
            except Exception:
                pass
        while True:
            message = await receive()
            if message["type"] == "lifespan.startup":
                await send({"type": "lifespan.startup.complete"})
            elif message["type"] == "lifespan.shutdown":
                await send({"type": "lifespan.shutdown.complete"})
                return

    if scope["type"] != "http":
        await _inner_app(scope, receive, send)
        return

    path: str = scope.get("path", "/")
    method: str = scope.get("method", "GET").upper()

    if method == "OPTIONS":
        await _send_json(send, 204, {})
        return

    if path in ("/", "/health", "/api/health"):
        await _send_json(
            send,
            200,
            {
                "status": "ok",
                "service": "reality_lens",
                "version": "3.0.0",
                "transport": "streamable-http",
                "mcp_endpoint": "/mcp",
                "tools_registered": len(srv.TOOL_CATALOG),
                "notebooks_synthesized": 39,
                "auth_required": bool(os.environ.get("REALITY_LENS_BEARER_TOKEN")),
            },
        )
        return

    expected_token = os.environ.get("REALITY_LENS_BEARER_TOKEN", "").strip()
    if expected_token:
        headers_dict = {k.decode("latin1").lower(): v.decode("latin1") for k, v in scope.get("headers", [])}
        auth_header = headers_dict.get("authorization", "")
        provided = auth_header[7:].strip() if auth_header.lower().startswith("bearer ") else ""
        if not provided or not hmac.compare_digest(provided.encode("utf-8"), expected_token.encode("utf-8")):
            await _send_json(
                send,
                401,
                {"error": "Unauthorized", "hint": "Pass Authorization: Bearer <REALITY_LENS_BEARER_TOKEN>"},
                extra_headers=[(b"www-authenticate", b'Bearer realm="reality_lens_mcp"')],
            )
            return

    if path == "/mcp":
        routes = getattr(getattr(_inner_app, "router", None), "routes", [])
        if any(type(r).__name__ == "Mount" and getattr(r, "path", "") == "/mcp" for r in routes):
            scope = {**scope, "path": "/mcp/", "raw_path": b"/mcp/"}

    await _inner_app(scope, receive, send)


if __name__ == "__main__":
    import uvicorn

    port = int(os.environ.get("PORT", "8000"))
    uvicorn.run(
        "reality_lens_http_app:app",
        host="0.0.0.0",
        port=port,
        proxy_headers=True,
        forwarded_allow_ips="*",
    )
