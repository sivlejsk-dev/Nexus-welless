# Nexus AI — Upgrade & Training Checklist

## Current State Assessment

Nexus is a multi-module Python AI system with the following existing components:

| Component | Status | Notes |
|---|---|---|
| `BirthChartGenerator` | ✅ Integrated & working | Real astronomical calculations |
| `DailyAstrologer` | ✅ Integrated & working | Personalized daily guidance |
| `AstrologyInterpreter` | ✅ Integrated & working | Full chart narratives |
| `guide_engine` | ✅ Integrated & working | Meditation + meal mapping |
| `InvestmentInsights` | ⚠️ Exists, not integrated | Basic stock analysis via yfinance |
| `ContextAwareFinancialAdvisor` | ⚠️ Exists, not integrated | User profile + follow-up logic |
| `MarketTrendAnalysis` | ⚠️ Exists, stub only | Sentiment + scraping scaffolding |
| `AdvancedReasoning` | ⚠️ Exists, not integrated | Multi-framework logic engine |
| `ContinuousLearner` | ⚠️ Exists, not integrated | Pattern recognition + skill tracking |
| `EnhancedConversationalUnderstanding` | ⚠️ Exists, not integrated | Dialogue threading + intent |
| Options trading | ❌ Does not exist | Needs to be built from scratch |
| Fine-tuning pipeline | ❌ Does not exist | Needs dataset + training setup |
| Wellness knowledge base | ❌ Stub only | Needs curated domain data |
| Vector memory / RAG | ❌ Does not exist | Needed for long-term context |

---

## Upgrade Checklist

Tasks are ordered by dependency — each group builds on the previous.

---

### PHASE 1 — Foundation: Conversation & Memory
*Nexus must hold context, remember users, and reason before it can specialize.*

- [ ] **1.1 — Integrate `EnhancedConversationalUnderstanding`**
  - Wire dialogue threading, pronoun resolution, and topic tracking into the backend
  - Every API call passes through the conversation context manager
  - Store conversation history per user in the database

- [ ] **1.2 — Integrate `ContinuousLearner`**
  - Connect pattern recognition to user interactions
  - Persist learned patterns per user in the database
  - Feed patterns back into recommendation logic

- [ ] **1.3 — Integrate `AdvancedReasoning` engine**
  - Wire deductive / inductive / causal reasoning frameworks into Nexus responses
  - Use for multi-step financial and wellness problem decomposition

- [ ] **1.4 — Build vector memory (RAG layer)**
  - Set up a vector store (ChromaDB or pgvector) for long-term semantic memory
  - Index all user conversations, profile data, and domain knowledge
  - Retrieve relevant context on every Nexus query

- [ ] **1.5 — Persistent conversation sessions**
  - Store full conversation history per user in PostgreSQL
  - Implement session continuity (Nexus remembers previous conversations)
  - Add conversation summary compression for long sessions

---

### PHASE 2 — Wellness Domain Training
*Curate and inject high-quality domain knowledge for each wellness module.*

- [ ] **2.1 — Nutrition knowledge base**
  - Curate dataset: PubMed nutrition studies, USDA food composition data, functional medicine protocols
  - Build structured knowledge: food → condition → mechanism → dosage
  - Train Nexus to cite sources and explain biochemical rationale
  - Cover: anti-inflammatory, gut microbiome, detox pathways, hormonal balance, longevity

- [ ] **2.2 — Meditation & mindfulness knowledge base**
  - Curate dataset: clinical mindfulness research (MBSR, MBCT), breathwork protocols, neuroscience of meditation
  - Map mental states → optimal practice → measurable outcomes
  - Add session progression logic (beginner → advanced journeys)
  - Cover: anxiety, sleep, trauma, focus, spiritual development

- [ ] **2.3 — Detox & functional medicine knowledge base**
  - Curate dataset: liver detox pathways, heavy metal chelation research, lymphatic protocols
  - Build contraindication logic (what NOT to do for each condition)
  - Add supplement interaction database
  - Cover: Phase 1/2 liver detox, gut healing, parasite protocols, mold illness

- [ ] **2.4 — Astrology wellness integration**
  - Expand Nexus interpretations to include medical astrology (body systems per sign/planet)
  - Build transit-to-wellness mapping (e.g., Saturn transits → bone/joint focus)
  - Add lunar cycle protocols (new moon detox, full moon release practices)
  - Integrate Vedic system (`vedic_system.py` already exists in nexus_core)

- [ ] **2.5 — Wellness fine-tuning dataset**
  - Compile 5,000+ high-quality Q&A pairs across all wellness domains
  - Format as instruction-tuning dataset (system prompt + user + assistant)
  - Sources: PubMed abstracts, clinical guidelines, functional medicine textbooks
  - Validate for accuracy before training

---

### PHASE 3 — Financial Intelligence
*Build Nexus into a serious financial analysis engine, culminating in options trading.*

- [ ] **3.1 — Integrate existing `InvestmentInsights` module**
  - Wire `analyze_stock()` into the backend API (`/finance/stock/{symbol}`)
  - Add SMA crossover signals, RSI, MACD to the existing yfinance pipeline
  - Expose portfolio optimization endpoint

- [ ] **3.2 — Integrate `ContextAwareFinancialAdvisor`**
  - Wire `UserFinancialProfile` to the user database (replace file-based persistence)
  - Connect follow-up pattern logic to conversation engine
  - Add goal tracking: retirement, wealth building, income generation

- [ ] **3.3 — Market data pipeline**
  - Integrate real-time market data: yfinance (free), Polygon.io, or Alpaca API
  - Build data ingestion for: price, volume, options chain, earnings, macro indicators
  - Set up Redis caching for market data (TTL: 1 minute for live, 1 hour for daily)

- [ ] **3.4 — Technical analysis engine**
  - Implement full indicator suite: RSI, MACD, Bollinger Bands, ATR, VWAP, OBV
  - Add candlestick pattern recognition (doji, engulfing, hammer, etc.)
  - Build multi-timeframe analysis (1m, 5m, 1h, 1d, 1w)
  - Integrate with `MarketTrendAnalysis` sentiment layer

- [ ] **3.5 — Options trading intelligence** *(core objective)*
  - Build options chain analyzer: fetch live chains via yfinance / Tradier / Tastytrade API
  - Implement Greeks calculator: Delta, Gamma, Theta, Vega, Rho
  - Build strategy analyzer:
    - Single leg: long/short calls and puts
    - Spreads: vertical (bull call, bear put), calendar, diagonal
    - Multi-leg: iron condor, iron butterfly, straddle, strangle
    - Defined risk: credit spreads, debit spreads
  - Implied volatility analysis: IV rank, IV percentile, IV crush detection
  - Probability of profit (POP) calculator using Black-Scholes
  - Expected move calculator (earnings plays, event-driven)
  - Build trade setup recommender: given market conditions → suggest optimal strategy

- [ ] **3.6 — Risk management engine**
  - Position sizing calculator (Kelly Criterion, fixed fractional)
  - Portfolio-level Greeks aggregation
  - Max loss / max profit / breakeven calculator for every strategy
  - Correlation analysis across positions
  - VaR (Value at Risk) and CVaR calculations

- [ ] **3.7 — Financial fine-tuning dataset**
  - Compile options trading Q&A: strategy selection, Greeks interpretation, IV analysis
  - Include real trade examples with entry, management, and exit logic
  - Add macro analysis: Fed policy, earnings seasons, sector rotation
  - Format as instruction-tuning dataset (5,000+ pairs)
  - Sources: CBOE education, tastytrade research, options alpha content

---

### PHASE 4 — Model Fine-Tuning
*Train Nexus on curated domain data to produce expert-level responses.*

- [ ] **4.1 — Select base model**
  - Evaluate: Llama 3.1 8B / 70B, Mistral 7B, Phi-3, Gemma 2
  - Decision criteria: context window, inference speed, fine-tuning cost, license
  - Recommended starting point: Llama 3.1 8B (fits on single A100, Apache 2.0 license)

- [ ] **4.2 — Set up fine-tuning infrastructure**
  - Configure training environment: CUDA, PyTorch, Hugging Face Transformers
  - Implement LoRA / QLoRA for parameter-efficient fine-tuning
  - Set up training pipeline: dataset loading, tokenization, training loop, evaluation
  - Tools: `trl` (SFTTrainer), `peft`, `bitsandbytes` for 4-bit quantization

- [ ] **4.3 — Fine-tune on wellness domain** (Phase 2 dataset)
  - Run supervised fine-tuning (SFT) on wellness Q&A dataset
  - Evaluate: perplexity, ROUGE scores, human evaluation on 100 test prompts
  - Iterate on dataset quality based on evaluation results

- [ ] **4.4 — Fine-tune on financial domain** (Phase 3 dataset)
  - Run SFT on financial + options trading dataset
  - Evaluate: accuracy of Greeks calculations, strategy recommendations, risk assessments
  - Red-team for hallucinated financial advice

- [ ] **4.5 — RLHF / preference alignment** *(advanced)*
  - Collect human preference data: rank Nexus responses (A vs B)
  - Train reward model on preference data
  - Run PPO or DPO alignment to improve response quality
  - Focus alignment on: accuracy, safety (no reckless financial advice), depth

- [ ] **4.6 — Merge and deploy fine-tuned model**
  - Merge LoRA adapters into base model
  - Quantize to GGUF (llama.cpp) or GPTQ for efficient inference
  - Deploy via Ollama (local) or vLLM (production)
  - Update `NEXUS_API_BASE_URL` in `.env` to point to self-hosted model

---

### PHASE 5 — Advanced Capabilities
*Elevate Nexus from expert to state-of-the-art.*

- [ ] **5.1 — Multi-modal input**
  - Wire `audio/` modules from nexus_core (voice emotion analyzer, prosody analyzer)
  - Add voice input to the frontend (Web Speech API)
  - Enable chart image analysis (upload a chart → Nexus interprets it)

- [ ] **5.2 — Agentic financial research**
  - Enable Nexus to autonomously research a ticker: pull news, earnings, options flow, analyst ratings
  - Build tool-use pipeline: Nexus calls financial APIs as tools, synthesizes findings
  - Add web search capability for real-time market news

- [ ] **5.3 — Backtesting engine**
  - Build options strategy backtester using historical options data
  - Allow Nexus to validate its own strategy recommendations against historical data
  - Integrate with `vectorbt` or `backtrader`

- [ ] **5.4 — Personalized financial coaching**
  - Build goal-based financial planning: income → expenses → savings → investment allocation
  - Add tax-aware options strategy guidance (short-term vs long-term capital gains)
  - Portfolio rebalancing recommendations based on market conditions

- [ ] **5.5 — Real-time alerts**
  - Build alert system: IV spike, unusual options flow, technical breakout, earnings approaching
  - Deliver via WebSocket to frontend dashboard
  - Nexus generates natural language explanation for each alert

---

## Execution Order

```
Phase 1 (Foundation)     → must complete before anything else
Phase 2 (Wellness)       → can run parallel with Phase 3
Phase 3 (Financial)      → can run parallel with Phase 2
Phase 4 (Fine-tuning)    → requires Phases 2 + 3 datasets complete
Phase 5 (Advanced)       → requires Phase 4 model deployed
```

## What We Tackle First

**Start with Phase 1.1** — integrating the conversation engine — because every other upgrade depends on Nexus being able to hold context across a conversation. Without it, even a perfectly fine-tuned model gives disconnected, stateless responses.

Ready to begin when you are.
