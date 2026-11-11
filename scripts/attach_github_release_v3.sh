#!/usr/bin/env bash
set -euo pipefail

REPO="Krosebrook/navigating-ai-reality-plugin"
TAG="v3.0.0"

python3 skills/navigating-ai-reality/scripts/validate_production_plugin.py
zip -r navigating-ai-reality-plugin-v3.0.0.zip \
  .claude-plugin .claude commands skills companion-deliverables \
  reality_lens_http_app.py Dockerfile .dockerignore render.yaml \
  .mcp.json .env.example install.sh requirements.txt LICENSE README.md
unzip -t navigating-ai-reality-plugin-v3.0.0.zip

gh release upload "${TAG}" \
  navigating-ai-reality-plugin-v3.0.0.zip \
  companion-deliverables/claude_reality_lens_plugin.html \
  companion-deliverables/reality_lens_citizen_field_guide.md \
  companion-deliverables/reality_lens_companion_workbook.csv \
  companion-deliverables/reality_lens_prompt_and_template_pack.md \
  --repo "${REPO}" \
  --clobber
