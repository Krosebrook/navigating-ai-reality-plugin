#!/usr/bin/env bash
set -euo pipefail
PLUGIN_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
echo "Installing Reality Lens (navigating-ai-reality-plugin v2.0.0)..."
python3 "$PLUGIN_DIR/skills/navigating-ai-reality/scripts/validate_production_plugin.py"

OS_TYPE="$(uname -s)"
if [[ "$OS_TYPE" == "Darwin" ]]; then
  CONFIG_DIR="$HOME/Library/Application Support/Claude"
elif [[ "$OS_TYPE" == "Linux" ]]; then
  CONFIG_DIR="$HOME/.config/Claude"
else
  CONFIG_DIR="$HOME/AppData/Roaming/Claude"
fi
mkdir -p "$CONFIG_DIR"
CONFIG_FILE="$CONFIG_DIR/claude_desktop_config.json"

python3 - "$CONFIG_FILE" "$PLUGIN_DIR/skills/navigating-ai-reality/scripts/reality_lens_mcp_server.py" << 'PYEOF'
import json, shutil, sys
from pathlib import Path
cfg = Path(sys.argv[1])
srv = str(Path(sys.argv[2]).resolve())
data = {"mcpServers": {}}
if cfg.exists():
    shutil.copy2(cfg, cfg.with_suffix(".json.bak"))
    try:
        data = json.loads(cfg.read_text())
    except Exception:
        data = {"mcpServers": {}}
data.setdefault("mcpServers", {})["reality_lens"] = {
    "command": "python3",
    "args": [srv],
    "env": {"REALITY_LENS_MODE": "non_tech_citizen", "COUNTERSIGN_STRICT": "true", "MAX_CALLS_PER_MINUTE": "30"}
}
cfg.write_text(json.dumps(data, indent=2) + "\n")
print("Registered 'reality_lens' MCP server in:", cfg)
PYEOF
echo "Done! Restart Claude Desktop or load in Claude Code / Cowork."
