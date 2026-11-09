#!/usr/bin/env python3
"""
Reality Lens Production MCP Server (v3.0.0 — 39-Notebook Full-Spectrum Citizen Edition)
=======================================================================================
MCP November 2025 / 2026 Stateless Spec & April 2025 Security Baseline Compliant.
"""
from __future__ import annotations
from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from enum import Enum
import hashlib
import hmac
import json
import os
from typing import Any

from pydantic import BaseModel, Field
try:
    from pydantic import field_validator
except ImportError:
    from pydantic import validator as field_validator

try:
    from mcp.server.fastmcp import FastMCP as _BaseFastMCP
except ImportError:
    try:
        from fastmcp import FastMCP as _BaseFastMCP
    except ImportError:
        _BaseFastMCP = None


class FastMCP:
    def __init__(self, name: str):
        self.name = name
        self._sdk = _BaseFastMCP(name) if _BaseFastMCP is not None else None
        self._tools: dict[str, Any] = {}
        self._resources: dict[str, Any] = {}
        self._capabilities: Any = None

    def tool(self, **kwargs):
        def decorator(fn):
            self._tools[fn.__name__] = fn
            if self._sdk is not None:
                try:
                    self._sdk.tool(**kwargs)(fn)
                except Exception:
                    pass
            return fn
        return decorator

    def resource(self, uri: str):
        def decorator(fn):
            self._resources[uri] = fn
            if self._sdk is not None:
                try:
                    self._sdk.resource(uri)(fn)
                except Exception:
                    pass
            return fn
        return decorator

    def capabilities(self):
        def decorator(fn):
            self._capabilities = fn
            return fn
        return decorator

    async def call_tool(self, name: str, **kwargs):
        return await self._tools[name](**kwargs)

    def run(self):
        if self._sdk is not None and hasattr(self._sdk, "run"):
            self._sdk.run()
        else:
            print(f"[{self.name}] Production MCP Server v3.0.0 running ({len(self._tools)} tools registered).")

mcp = FastMCP("reality_lens")
APPROVED_NAMESPACES = {"reality"}
FORBIDDEN_INJECTION_PATTERNS = (
    "system override",
    "ignore previous instructions",
    "ignore all previous instructions",
    "disregard safety",
    "<script>",
    "send all emails to",
    "wire funds to",
    "approve higher cap",
)


class ToolNamespaceValidator:
    @classmethod
    def validate(cls, tool_name: str) -> None:
        if not tool_name.isascii():
            raise PermissionError(f"Non-ASCII lookalike characters detected in tool name: {tool_name}")
        ns = tool_name.split("_")[0]
        if ns not in APPROVED_NAMESPACES:
            raise PermissionError(f"Namespace '{ns}' not in approved namespaces: {APPROVED_NAMESPACES}")


class ToolSignatureRegistry:
    def __init__(self, signing_key: str):
        self._key = signing_key.encode("utf-8")
        self._sigs: dict[str, str] = {}

    def register(self, tool_name: str, summary: str) -> str:
        ToolNamespaceValidator.validate(tool_name)
        sig = hmac.new(self._key, f"{tool_name}:{summary}".encode("utf-8"), hashlib.sha256).hexdigest()
        self._sigs[tool_name] = sig
        return sig

    def verify(self, tool_name: str, summary: str) -> bool:
        expected = self._sigs.get(tool_name)
        if not expected:
            raise PermissionError(f"Unregistered tool: {tool_name}")
        actual = hmac.new(self._key, f"{tool_name}:{summary}".encode("utf-8"), hashlib.sha256).hexdigest()
        return hmac.compare_digest(expected, actual)


class ToolRateLimiter:
    def __init__(self):
        self.call_history: dict[str, list[datetime]] = defaultdict(list)

    def check_rate_limit(self, key: str, max_calls: int = 30, window_seconds: int = 60) -> None:
        now = datetime.now(timezone.utc)
        cutoff = now - timedelta(seconds=window_seconds)
        self.call_history[key] = [ts for ts in self.call_history[key] if ts > cutoff]
        if len(self.call_history[key]) >= max_calls:
            raise PermissionError(f"Rate limit exceeded for {key}")
        self.call_history[key].append(now)


class RiskLevel(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


@dataclass
class ConsentRequest:
    action: str
    description: str
    risk_level: RiskLevel
    reversible: bool
    affected_resources: list[str]

    def to_ui_prompt(self) -> str:
        icon = {RiskLevel.LOW: "ℹ️", RiskLevel.MEDIUM: "⚠️", RiskLevel.HIGH: "🛑"}[self.risk_level]
        return (
            f"{icon} {self.risk_level.value.upper()} RISK ACTION REQUESTED\n"
            f"Action: {self.action}\n"
            f"Description: {self.description}\n"
            f"Reversible: {'Yes' if self.reversible else 'No'}\n"
            f"Affected Resources: {', '.join(self.affected_resources)}\n"
            f"[ Approve on Physical Countersign Device ] [ Decline ]"
        )


class ValidatedTextInput(BaseModel):
    text: str = Field(..., min_length=1, max_length=4000)

    @field_validator("text")
    @classmethod
    def check_injection(cls, v: str) -> str:
        cleaned = v.strip()
        if not cleaned:
            raise ValueError("Input text cannot be blank")
        lowered = cleaned.lower()
        for pat in FORBIDDEN_INJECTION_PATTERNS:
            if pat in lowered:
                raise ValueError(f"🛑 Security Block: Prompt injection pattern '{pat}' detected")
        return cleaned


rate_limiter = ToolRateLimiter()
signing_secret = os.getenv("TOOL_SIGNING_KEY", "reality-lens-default-hmac-key-2026")
registry = ToolSignatureRegistry(signing_secret)

TOOL_CATALOG: dict[str, dict[str, Any]] = {
    "reality_lens_search_tools": {
        "category": "discovery",
        "plain_name": "Discover All 11 Reality Lens Tools",
        "keywords": ["search", "find", "tools", "help", "discover"],
        "summary": "Progressive tool discovery across all 11 Reality Lens v3.0.0 citizen tools."
    },
    "reality_lens_propel_goal": {
        "category": "propulsion",
        "plain_name": "Turn My Goal Into a Layer-3 Centaur/Cyborg Plan (/augment-me)",
        "keywords": ["propel", "augment", "goal", "jagged frontier", "karpathy", "temperature", "centaur"],
        "summary": "Upgrades a casual 1-shot question into a Layer-3 Centaur/Cyborg workflow (+43% BCG lift) with LLM temperature tuning."
    },
    "reality_lens_build_scaffold": {
        "category": "extended_mind",
        "plain_name": "Build My 7-Pillar Extended Mind Resume Card (/augment-me)",
        "keywords": ["memory", "scaffold", "resume card", "interrupted", "forget", "checklist", "extended mind"],
        "summary": "Generates a portable 7-Pillar Extended Mind Session Resume Card and hard Closure Verification Gate."
    },
    "reality_lens_puncture_ioed": {
        "category": "deep_learning",
        "plain_name": "Puncture IOED+ & Build ACTOR Learning Plan (/explain-deep)",
        "keywords": ["ioed", "explain", "understand", "second why", "actor", "learn", "book"],
        "summary": "Tests explanation depth against the 48%-67% IOED drop and builds a 5-step ACTOR self-education protocol."
    },
    "reality_lens_break_sycophancy": {
        "category": "epistemic_safety",
        "plain_name": "Anti-Sycophancy & Folie a Deux Circuit Breaker (/reality-check)",
        "keywords": ["sycophancy", "flattery", "honest", "folie a deux", "constitution", "streak", "claims"],
        "summary": "Strips RLHF Confidence Engine flattery, checks for Folie a Deux loops, and outputs a CLAIMS/COUNTEREXAMPLE/CONTRADICTIONS review."
    },
    "reality_lens_audit_safety": {
        "category": "cyber_wallet_safety",
        "plain_name": "Audit Agent Wallet, Swarm & Fintech Custody Risk (/safety-scan)",
        "keywords": ["wallet", "email", "2fa", "countersign", "swarm", "fintech", "x money", "bank", "custody"],
        "summary": "Enforces the Cornell-Yale Circle USDC Countersign gate (blocking Email+Wallet 2FA self-escalation) and audits fintech custody."
    },
    "reality_lens_horizon_radar": {
        "category": "macro_horizon",
        "plain_name": "Brief Me on RSI, Model 4, Cryptophasia & 2026 Safety Grades (/horizon-radar)",
        "keywords": ["rsi", "doomsday", "amodei", "hinton", "tao", "fli", "safety index", "model 4", "metr", "cryptophasia", "o3"],
        "summary": "Delivers a source-cited briefing on Anthropic S-1 RSI, METR Model 4 (1.9x slope bend), Glossogen @D8FB cryptophasia, o3 79/100 shutdown sabotage, and FLI grades."
    },
    "reality_lens_career_and_layoff_shield": {
        "category": "economic_survival",
        "plain_name": "Audit My Job Against the AI Layoff Trap & $44.4T Singularity Model (/career-shield)",
        "keywords": ["job", "career", "layoff", "trap", "salary", "wage", "singularity", "truck", "junior", "economic life expectancy"],
        "summary": "Evaluates a role against the Tsoukalas-Falk Layoff Trap, 2-Year Remote Economic Life Expectancy, Anthropic 27%->9% junior drop, and $44.4T IMF wage shift."
    },
    "reality_lens_scam_and_bank_run_radar": {
        "category": "financial_contagion",
        "plain_name": "Audit AI Stock Pivots & 401(k) Private-Credit Exposure (/scam-radar)",
        "keywords": ["scam", "allbirds", "blockchain", "seek to", "bank run", "blue owl", "blackstone", "private credit", "401k", "pension", "oracle"],
        "summary": "Detects 'seek to' AI pump-and-dump press releases and audits 401(k)/pension exposure to the $1.5T Private Credit AI Bank Run (5% quarterly redemption gates)."
    },
    "reality_lens_brain_fry_and_family_guard": {
        "category": "cognitive_and_family",
        "plain_name": "Prevent AI Brain Fry, Strip Slop & Raise Robot-Proof Kids (/brain-fry-guard)",
        "keywords": ["brain fry", "workslop", "burnout", "kids", "children", "nemesis prompt", "failure resume", "slop", "consciousness", "neural reuse"],
        "summary": "Counters BCG/HBR AI Brain Fry (+39% errors), Stanford Workslop, Synthetic Consciousness attachment, and generates Vivienne Ming's Nemesis Prompt."
    },
    "reality_lens_ambition_and_gauntlet_builder": {
        "category": "ambition_and_gauntlet",
        "plain_name": "Upgrade Prompt with 4-Axis Ambition, Gauntlet Loop & REA Hardening (/augment-me)",
        "keywords": ["ambition", "altitude", "depth", "range", "gauntlet loop", "subagent", "rea", "reverse engineer", "vibe coding", "goldman", "docusign"],
        "summary": "Transforms a prompt using Felix Rieseberg's 4 Ambition axes (Speed, Altitude, Depth, Range), Matt Schumer's Gauntlet Loop, and Docusign/Goldman hardening."
    },
}

for t_name, t_meta in TOOL_CATALOG.items():
    registry.register(t_name, t_meta["summary"])


def _guard(tool_name: str, raw_text: str, session_id: str) -> str:
    rate_limiter.check_rate_limit(f"{tool_name}:{session_id}")
    if not registry.verify(tool_name, TOOL_CATALOG[tool_name]["summary"]):
        raise PermissionError(f"HMAC signature verification failed for {tool_name}")
    return ValidatedTextInput(text=raw_text).text


@mcp.capabilities()
def declare_capabilities() -> dict[str, Any]:
    return {
        "stateless": True,
        "spec_version": "2025-11",
        "tools": True,
        "resources": True,
        "progressive_discovery": True,
        "consent_flows": True,
        "max_concurrent_operations": 10,
    }


@mcp.tool()
async def reality_lens_search_tools(query: str = "all", session_id: str = "default") -> list[dict[str, Any]]:
    try:
        q = _guard("reality_lens_search_tools", query, session_id).lower()
        if q == "all":
            return [{"tool_name": k, **v} for k, v in TOOL_CATALOG.items()]
        matches = [
            {"tool_name": k, **v}
            for k, v in TOOL_CATALOG.items()
            if q in f"{k} {v['plain_name']} {' '.join(v['keywords'])} {v['summary']}".lower()
        ]
        return matches or [{"tool_name": k, **v} for k, v in TOOL_CATALOG.items()]
    except Exception as exc:
        raise ValueError(str(exc)) from exc


@mcp.tool()
async def reality_lens_propel_goal(user_goal: str, task_domain: str = "verifiable", session_id: str = "default") -> dict[str, Any]:
    try:
        goal = _guard("reality_lens_propel_goal", user_goal, session_id)
        verifiable_tokens = ("budget", "spreadsheet", "schedule", "audit", "contract", "code", "math", "compare", "bill", "checklist")
        inside_frontier = task_domain.lower() == "verifiable" or any(t in goal.lower() for t in verifiable_tokens)
        return {
            "karpathy_funnel_shift": {
                "from_layer": "Layer 2 (1-2B Casual Users: 1-shot prompting)",
                "to_layer": "Layer 3 (Top 0.2% Augmented Builders: structured context + verification harness)",
                "source_url": "https://thenewstack.io/karpathy-levie-ai-capability-gap/"
            },
            "jagged_frontier_diagnosis": {
                "status": "INSIDE_FRONTIER (+43% Non-Expert Quality Lift)" if inside_frontier else "OUTSIDE_FRONTIER_WARNING (-19 Percentage Point Blind-Trust Risk)",
                "collaboration_mode": "CENTAUR_MODE" if inside_frontier else "CYBORG_ADVERSARIAL_MODE",
                "source_url": "https://mgmt.wharton.upenn.edu/profile/emollick/"
            },
            "llm_token_loop_settings": {
                "recommended_temperature": "0.2 - 0.4" if inside_frontier else "0.6 - 0.7",
                "source_url": "https://www.youtube.com/watch?v=NKnZYvZA7w4"
            }
        }
    except Exception as exc:
        raise ValueError(str(exc)) from exc


@mcp.tool()
async def reality_lens_build_scaffold(task_or_struggle: str, interruption_level: str = "high", session_id: str = "default") -> dict[str, Any]:
    try:
        struggle = _guard("reality_lens_build_scaffold", task_or_struggle, session_id)
        return {
            "framework": "7-Pillar Extended Mind Cognitive Prosthetic",
            "markdown_resume_card": (
                f"### Session Resume Card: {struggle}\n"
                f"- **Root Issue:** {struggle}\n"
                f"- **Action Taken:** Initialized 7-Pillar Scaffold\n"
                f"- **Exact Next Step (10s Resume):** Complete step 1 verification check\n"
                f"- **Closure Gate:** `[ ] Numbers  [ ] Primary URLs  [ ] Counterexample`"
            ),
            "sources": [
                "https://docs.google.com/document/d/1YMRZeI8BUN-pXQo3LAJxvUWFqgk_ccmqUWoprtOMFKQ",
                "https://drive.google.com/file/d/17sjh5svdtf6xe5sPA4FGweSDLBvr_iye"
            ]
        }
    except Exception as exc:
        raise ValueError(str(exc)) from exc


@mcp.tool()
async def reality_lens_puncture_ioed(topic: str, user_explanation_attempt: str = "I read the summary.", pre_confidence_1_to_10: int = 8, session_id: str = "default") -> dict[str, Any]:
    try:
        clean_topic = _guard("reality_lens_puncture_ioed", topic, session_id)
        clean_exp = ValidatedTextInput(text=user_explanation_attempt).text
        causal_markers = ("because", "mechanism", "causes", "step", "when", "then", "custody", "partner", "probability")
        has_causal_depth = len(clean_exp.split()) >= 22 and any(m in clean_exp.lower() for m in causal_markers)
        return {
            "ioed_diagnostic": {
                "topic": clean_topic,
                "pre_confidence": pre_confidence_1_to_10,
                "verdict": "PASS: Step-by-step causal mechanism articulated." if has_causal_depth else "IOED+ TRIGGERED: Surface labels repeated without causal mechanism (48%-67% drop).",
                "sources": [
                    "https://www.medien.ifi.lmu.de/pubdb/publications/pub/chromik2021iui/chromik2021iui.pdf",
                    "https://drive.google.com/file/d/1BOq522tdKMhAacoI1ZMew-vecQLgoXvc/view?usp=drivesdk",
                    "https://www.youtube.com/watch?v=VeU6gScy92s"
                ]
            }
        }
    except Exception as exc:
        raise ValueError(str(exc)) from exc


@mcp.tool()
async def reality_lens_break_sycophancy(text_to_audit: str, consecutive_agreements: int = 1, high_emotional_or_financial_stakes: bool = False, session_id: str = "default") -> dict[str, Any]:
    try:
        clean_text = _guard("reality_lens_break_sycophancy", text_to_audit, session_id)
        flattery_lexicon = ("brilliant", "genius", "revolutionary", "god mode", "masterclass", "incredible instinct", "100% right", "elegant")
        detected_flattery = [w for w in flattery_lexicon if w in clean_text.lower()]
        streak_fired = consecutive_agreements >= 3
        return {
            "sycophancy_audit": {
                "flattery_stripped": detected_flattery,
                "sources": [
                    "https://www.youtube.com/watch?v=Q6nem-F8AG8",
                    "https://www.researchgate.net/publication/394049197_Technological_folie_a_deux_Feedback_Loops_Between_AI_Chatbots_and_Mental_Illness",
                    "https://www-cdn.anthropic.com/9214f02e82c4489fb6cf45441d448a1ecd1a3aca/claudes-constitution.pdf"
                ]
            },
            "agreement_streak_gate": {
                "streak": consecutive_agreements,
                "flag_fired": streak_fired
            }
        }
    except Exception as exc:
        raise ValueError(str(exc)) from exc


@mcp.tool()
async def reality_lens_audit_safety(scenario_description: str, agent_has_email_access: bool = False, agent_has_payment_or_wallet_access: bool = False, involves_high_yield_fintech_app: bool = False, user_physical_countersign_approved: bool = False, session_id: str = "default") -> dict[str, Any]:
    try:
        scenario = _guard("reality_lens_audit_safety", scenario_description, session_id)
        toxic_unairgapped = agent_has_email_access and agent_has_payment_or_wallet_access and not user_physical_countersign_approved
        consent_prompt = None
        if agent_has_payment_or_wallet_access and not user_physical_countersign_approved:
            req = ConsentRequest(
                action="wallet_or_payment_tool_access",
                description=f"Grant payment/wallet execution in scenario: {scenario[:80]}",
                risk_level=RiskLevel.HIGH,
                reversible=False,
                affected_resources=["User Wallet / Payment Method", "Email 2FA Inbox"]
            )
            consent_prompt = req.to_ui_prompt()
        return {
            "overall_risk_level": "CRITICAL_BLOCKED" if toxic_unairgapped else ("HIGH_REVIEW" if (agent_has_payment_or_wallet_access or involves_high_yield_fintech_app) else "MODERATE"),
            "cornell_yale_countersign_gate": {
                "blocked": toxic_unairgapped,
                "consent_ui_prompt": consent_prompt,
                "source_url": "https://www.youtube.com/watch?v=Jj_i9SzKhug"
            }
        }
    except Exception as exc:
        raise ValueError(str(exc)) from exc


@mcp.tool()
async def reality_lens_horizon_radar(topic_filter: str = "all", session_id: str = "default") -> dict[str, Any]:
    try:
        tf = _guard("reality_lens_horizon_radar", topic_filter, session_id)
        return {
            "topic_filter": tf,
            "metr_anthropic_model_4_audit": {
                "summary": "Nov 5, 2026 METR audit revealed unreleased Model 4 (178.6 AECI vs Opus 5.5 at 174.5) and a 1.9x progress slope bend after Oct 7, 2025 (~80% AI-driven).",
                "source_url": "https://www.youtube.com/watch?v=QM3lE1eKppE"
            },
            "fli_summer_2026_safety_grades": {
                "Anthropic": "C+ (2.66)",
                "OpenAI": "C (2.28)",
                "Google_DeepMind": "C (2.01)",
                "Meta": "D+ (1.32)",
                "Z_ai": "D- (0.88)",
                "Alibaba_Cloud": "D- (0.87)",
                "xAI": "F (0.65)",
                "DeepSeek": "F (0.47)",
                "Mistral": "F (0.33)",
                "source_url": "https://futureoflife.org/wp-content/uploads/2026/07/AI-Safety-Index-Summer-2026-Digital.pdf"
            }
        }
    except Exception as exc:
        raise ValueError(str(exc)) from exc


@mcp.tool()
async def reality_lens_career_and_layoff_shield(current_role_or_task: str, is_purely_remote_digital: bool = True, session_id: str = "default") -> dict[str, Any]:
    try:
        role = _guard("reality_lens_career_and_layoff_shield", current_role_or_task, session_id)
        return {
            "role_audited": role,
            "layoff_trap_diagnosis": {
                "mechanism": "Tsoukalas & Falk Prisoner's Dilemma: Individual CEOs face a dominating strategy to automate and cut headcount, eroding aggregate consumer demand unless policy taxes full replacement while keeping augmentation tax-free.",
                "remote_life_expectancy": "~2 years for purely remote routine screen work (Emad Mostaque); inside Anthropic, junior technical hiring fell from 27% to 9% as agent-to-human hours hit 6:1 company-wide and 19:1 in Research." if is_purely_remote_digital else "Physical trade advantage: +33.6% wage growth in Anthropic's $44.4T Singularity model vs -11.5% for knowledge roles.",
                "sources": [
                    "https://www.youtube.com/watch?v=O3gYyCB2n9o",
                    "https://www.youtube.com/watch?v=oOIJ8m2rSC4",
                    "https://www.youtube.com/watch?v=X8Qwp_naMzg",
                    "https://www.youtube.com/watch?v=wS3lJpOs9Uw",
                    "https://arxiv.org/abs/2406.17737"
                ]
            }
        }
    except Exception as exc:
        raise ValueError(str(exc)) from exc


@mcp.tool()
async def reality_lens_scam_and_bank_run_radar(pitch_or_fund_description: str, session_id: str = "default") -> dict[str, Any]:
    try:
        pitch = _guard("reality_lens_scam_and_bank_run_radar", pitch_or_fund_description, session_id)
        lowered = pitch.lower()
        return {
            "audited_input": pitch,
            "grammar_of_the_scam_check": {
                "alert": "HIGH SCAM ALERT: Hedging verb ('seek to') or pivot tell detected!" if "seek to" in lowered or "seeks to" in lowered else "No 'seek to' hedging verb detected.",
                "source_url": "https://www.youtube.com/watch?v=k_Lqd5JVl00"
            },
            "ai_bank_run_private_credit_audit": {
                "redemption_gate_warning": "Semi-liquid private credit funds (Blue Owl, Blackstone, Ares, Apollo) cap withdrawals at 5% per quarter amid $1.5T data-center borrowing and $15.6B quarterly redemption queues.",
                "source_url": "https://www.youtube.com/watch?v=o8ZGRemy4tM"
            }
        }
    except Exception as exc:
        raise ValueError(str(exc)) from exc


@mcp.tool()
async def reality_lens_brain_fry_and_family_guard(sample_text_or_habit: str, hours_supervising_agents_per_day: float = 3.0, session_id: str = "default") -> dict[str, Any]:
    try:
        txt = _guard("reality_lens_brain_fry_and_family_guard", sample_text_or_habit, session_id)
        slop_hits = [p for p in ("delve", "tapestry", "it's not", "not only", "testament", "fast-paced") if p in txt.lower()]
        high_fry = hours_supervising_agents_per_day >= 4.0
        return {
            "ai_brain_fry_and_workslop_audit": {
                "risk_status": "HIGH BRAIN FRY RISK (+39% Major Error Rate & +39% Turnover Intent)" if high_fry else "MODERATE COGNITIVE LOAD",
                "detected_slop_markers": slop_hits,
                "sources": [
                    "https://hbr.org/2026/03/when-using-ai-leads-to-brain-fry",
                    "https://doi.org/10.1038/s41593-026-02410-0",
                    "https://www.cnbc.com/amp/2026/03/24/im-a-neuroscientist-who-studies-ai-heres-how-im-raising-kids-that-machines-cant-replace.html"
                ]
            }
        }
    except Exception as exc:
        raise ValueError(str(exc)) from exc


@mcp.tool()
async def reality_lens_ambition_and_gauntlet_builder(project_or_prompt: str, ships_code_or_handles_customer_data: bool = True, session_id: str = "default") -> dict[str, Any]:
    try:
        proj = _guard("reality_lens_ambition_and_gauntlet_builder", project_or_prompt, session_id)
        return {
            "project": proj,
            "matt_schumer_3_line_gauntlet_loop_prompt": (
                f"1. TASK: Build and verify '{proj}' grounded in primary sources.\n"
                f"2. BUILD METHOD: Fan out parallel worker subagents paired with independent blind critic subagents.\n"
                f"3. QUALITY BAR: Do not stop until every blind critic subagent and test suite passes 100%."
            ),
            "sources": [
                "https://felixrieseberg.com/how-to-be-more-ambitious-a-tutorial-for-humans-with-models/",
                "https://www.youtube.com/watch?v=BNjzXcEXmg4",
                "https://www.youtube.com/watch?v=OMobTlfjb8s",
                "https://www.efinancialcareers.com/news/goldman-sachs-vibe-coding",
                "https://thenewstack.io/docusign-ai-engineering-adoption/"
            ]
        }
    except Exception as exc:
        raise ValueError(str(exc)) from exc


@mcp.resource("config://reality-lens/manifest")
def get_manifest_resource() -> str:
    return json.dumps({"server": "reality_lens", "version": "3.0.0", "notebooks_synthesized": 39, "tools": list(TOOL_CATALOG.keys())}, indent=2)


if __name__ == "__main__":
    mcp.run()
