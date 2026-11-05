# Reality Lens Citizen Configuration (`assets/config.md`)

Update these preferences to tailor `navigating-ai-reality` to your daily workflow:

```yaml
user_profile:
  experience_level: "non_technical_citizen"
  default_collaboration_mode: "centaur"          # centaur | cyborg
  interruption_frequency: "high"                 # low | medium | high
  local_resume_card_dir: "./resume_cards"

safety_gates:
  countersign_strict_airgap: true                # Block Email/2FA + Wallet combos
  agreement_streak_threshold: 3                  # Fire Challenge Pass at 3 agreements
  enforce_ioed_second_why: true                  # Require causal check on summaries
  default_adversarial_tier: "STANDARD"           # LITE | STANDARD | HEAVY
```
