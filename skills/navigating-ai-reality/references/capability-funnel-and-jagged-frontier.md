# Capability Funnel, LLM Token Mechanics & The Jagged Frontier

## 1. Andrej Karpathy's 4-Tier AI Capability Funnel
- **Layer 1 (~6 Billion People / 75% of Humanity):** Zero or minimal interaction with Large Language Models ([Benzinga Report](https://www.benzinga.com/markets/tech/26/10/62292803/andrej-karpathy-warns-ai-capability-gap-is-widening-as-advanced-projects)).
- **Layer 2 (~1-2 Billion Casual Users):** Use free-tier chatbots like a slightly better search engine or paragraph writer ("using a chainsaw to sharpen a pencil"), encounter one-shot riddles, and write AI off ([The New Stack](https://thenewstack.io/karpathy-levie-ai-capability-gap/)).
- **Layer 3 (~20 Million Augmented Builders / 0.2%):** Use frontier models with context engineering, MCP tools, and verification harnesses to compress weeks of work into hours ([Karpathy Funnel Video](https://www.youtube.com/watch?v=6x_AIty3Nrs)).
- **Layer 4 (~5,000 Lab Insiders):** Orchestrate swarms of thousands of specialized agents across multi-week scientific, mathematical, and cyber operations.

## 2. The 5-Step LLM Next-Token Loop (Demystifying the Machine)
Per [How LLMs Actually Generate Text](https://www.youtube.com/watch?v=NKnZYvZA7w4), an LLM has zero advance plan of what it will say at token 50 when generating token 1:
1. **Tokenization:** Splits text into subword integers (~4,096 tokens = ~3,000 English words).
2. **Embeddings:** Converts each token ID into a 12,000+ dimensional meaning-space vector.
3. **Transformer Attention:** 80-96 stacked layers connect context with quadratic $O(N^2)$ compute cost—explaining why long, cluttered chats degrade.
4. **Softmax Probabilities:** Scores all ~128,000 vocabulary tokens so probabilities sum to 1.0.
5. **Sampling (Temperature & Top-P):**
   - `Temperature 0.2 - 0.4`: Sharpens distribution for code, math, budgets, and data extraction.
   - `Temperature 0.7 - 1.0`: Flattens distribution for brainstorming and creative variance.
   - **Core Insight:** Hallucinations are not "lies"—the probability distribution cannot distinguish factual truth from plausible-sounding pattern matches.

## 3. Wharton & BCG's Jagged Technological Frontier
In the pre-registered field experiment with 758 Boston Consulting Group consultants ([Ethan Mollick Wharton Research](https://mgmt.wharton.upenn.edu/profile/emollick/)):
- **Inside the Frontier:** Consultants completed **12.2% more tasks**, **25.1% faster**, with **>40% higher quality**. Bottom-half performers improved by **+43%** and top-half performers by **+17%**.
- **Enterprise Multipliers:** Industrial deployments report **3.4x analytical productivity** and **40% more favorable contract negotiations** ([Interlake Mecalux AI Moat](https://www.interlakemecalux.com/logistics-articles/ai-moat)).
- **Outside the Frontier Trap:** On tasks that look similar but require unverified edge judgment, AI users were **19 percentage points less likely** to produce correct solutions than humans working alone.
- **Centaur vs. Cyborg Modes:** *Centaurs* explicitly divide tasks between human judgment and AI computation; *Cyborgs* tightly interleave human verification at every sub-step.
