# Navigating AI Reality — Reality Lens v3.0.0 (39-Notebook Citizen Edition)

Production-grade **Claude Code Plugin**, **AgentSkill**, and **11-Tool Stateless MCP Server** (supporting both **Local `stdio`** and **Remote `Streamable HTTP`**) synthesized from 39 research notebooks to close the public AI capability-awareness gap while defending against cognitive, financial, career, and cyber threats.

---

## 1. Connect as a Remote Streamable HTTP MCP Server (Web & IDE Clients)

This repository includes `reality_lens_http_app.py`, a multi-stage non-root `Dockerfile`, and a declarative `render.yaml` Blueprint:

1. **Deploy on Render**: Open **Render Dashboard -> New -> Blueprint**, select `Krosebrook/navigating-ai-reality-plugin`, and enter a secret value for `REALITY_LENS_BEARER_TOKEN`.
2. **Deploy on Cloud Run (Alternative)**:
   ```bash
   gcloud run deploy reality-lens-mcp --source . --port 8000 --allow-unauthenticated --set-env-vars REALITY_LENS_BEARER_TOKEN=YOUR_SECRET
   ```
3. **Verify Health Endpoint**:
   ```bash
   curl -s https://reality-lens-mcp.onrender.com/health
   ```
4. **Register in Any Streamable HTTP MCP Client**:
   ```json
   {
     "mcpServers": {
       "reality_lens_remote": {
         "type": "http",
         "url": "https://reality-lens-mcp.onrender.com/mcp",
         "headers": {
           "Authorization": "Bearer YOUR_REALITY_LENS_BEARER_TOKEN"
         }
       }
     }
   }
   ```

---

## 2. Local Claude Code Plugin Installation (`stdio`)

```bash
git clone https://github.com/Krosebrook/navigating-ai-reality-plugin.git
cd navigating-ai-reality-plugin
./install.sh
```

---

## 3. All 8 Citizen Slash Commands & 11 Stateless MCP Tools (`v3.0.0`)

| Slash Command | MCP Tool | Purpose |
| :--- | :--- | :--- |
| `/reality-check` | `reality_lens_propel_goal` / `reality_lens_break_sycophancy` | Jagged Frontier (+40% vs -19pp), RLVR verification loop, and 3-agreement sycophancy guard |
| `/augment-me` | `reality_lens_ambition_and_gauntlet_builder` / `reality_lens_build_scaffold` | Felix Rieseberg's 4 Ambition axes, 3-line Generator-Critic-Verifier Gauntlet Loop, and Extended Mind Resume Card |
| `/safety-scan` | `reality_lens_audit_safety` | Blocks un-airgapped Email/Inbox + Payment/Wallet workflows (`Exit Code 2`) and 15,000x Swarm exposure |
| `/explain-deep` | `reality_lens_puncture_ioed` | 4-step IOED+ Puncture Protocol (Rozenblit & Keil 2002; Vitriol & Marsh 2018) |
| `/horizon-radar` | `reality_lens_horizon_radar` | 2026-2030 AGI timelines, FLI Safety Grades (best `C+`), METR ~7-month doubling, and MIT's 12 Paths |
| `/career-shield` | `reality_lens_career_and_layoff_shield` | Wharton AI Layoff Trap defense (Tsoukalas 2026) and 85% labor-to-compute compression playbook |
| `/scam-radar` | `reality_lens_scam_and_bank_run_radar` | SEC Form 8-K vs 10-K Grammar of the Scam detector and AI Bank Run liquidity air-gap |
| `/brain-fry-guard` | `reality_lens_brain_fry_and_family_guard` | BCG 14% Brain Fry cap (3.5h/day, <=3 agents), 81-pattern Workslop linter, and child Socratic guardrails |

---

## 4. Run the 10-Gate Deterministic Validator

```bash
python3 skills/navigating-ai-reality/scripts/validate_production_plugin.py
```

## License

MIT — Copyright (c) 2026 Kyle Rosebrook (`Krosebrook`)
