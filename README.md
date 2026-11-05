# Navigating AI Reality (`navigating-ai-reality-plugin` v2.0.0)

**Veteran Staff-Level Production Claude Plugin, Deterministic Hook Suite & MCP 2025.11 Stateless Server for Non-Technical End Users.**

Built on the [`agentskills.io`](https://agentskills.io) open specification and Anthropic Knowledge Work Plugin standard.

## Package Architecture

```text
navigating-ai-reality-plugin/
├── .claude-plugin/
│   └── plugin.json                                     # Anthropic Cowork / Claude Code Plugin Manifest
├── .mcp.json                                           # Zero-config MCP Server registration
├── .claude/
│   ├── settings.json                                   # Least-privilege allow/deny rules & Hook wiring
│   ├── skills/skill-rules.json                         # Deterministic SUGGEST & PreToolUse BLOCK rules
│   └── hooks/
│       ├── user_prompt_submit.py                       # Intent matcher & safety/propulsion reminder
│       ├── pre_tool_use_countersign.py                 # Exit Code 2 BLOCK on Email+Wallet 2FA self-escalation
│       └── stop_adversarial_audit.py                   # Post-response epistemic check
├── commands/                                           # 5 Plain-English Slash Commands
│   ├── augment-me.md                                   # /augment-me (Centaur/Cyborg + 7-Pillar Resume Card)
│   ├── explain-deep.md                                 # /explain-deep (IOED+ Second-Why + ACTOR Protocol)
│   ├── reality-check.md                                # /reality-check (Anti-Sycophancy + Folie a Deux Breaker)
│   ├── safety-scan.md                                  # /safety-scan (Cornell-Yale Wallet Gate + Custody Audit)
│   └── horizon-radar.md                                # /horizon-radar (RSI, Cyber Swarms & FLI Safety Grades)
├── skills/
│   └── navigating-ai-reality/                          # Spec-compliant Gerund AgentSkill (Zero README.md inside)
│       ├── SKILL.md                                    # L0 Frontmatter + L1 Body (<= 500 lines)
│       ├── references/                                 # L2 1-Hop Domain References
│       │   ├── capability-funnel-and-jagged-frontier.md
│       │   ├── extended-mind-and-ioed-actor.md
│       │   ├── sycophancy-constitution-and-folie.md
│       │   └── swarms-wallets-rsi-and-doomsday.md
│       ├── assets/                                     # User Config & Zero-Placeholder Templates
│       │   ├── config.md
│       │   └── resume-card-template.md
│       └── scripts/                                    # Production MCP Server, CLI & 10-Gate Validator
│           ├── reality_lens_mcp_server.py
│           ├── cli_reality_check.py
│           └── validate_production_plugin.py
├── install.sh                                          # 1-Click macOS / Linux / WSL Installer
├── requirements.txt
└── .env.example
```

## Quick Start (3 Ways to Use)

1. **1-Click Desktop / CLI Install:**
   ```bash
   ./install.sh
   ```
2. **Claude Cowork / Claude Code Plugin Install:**
   ```bash
   claude plugin add ./navigating-ai-reality-plugin
   ```
3. **Standalone Skills Manager Upload:**
   Upload `skills/navigating-ai-reality/` (or the entire zip) directly into Claude's Skills Manager UI.
