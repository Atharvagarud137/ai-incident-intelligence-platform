# LLM Provider Analysis Report

## AI Incident Intelligence Platform

**Document Type:** Technology Decision Report  
**Decision Area:** LLM Provider Selection  
**Status:** Under Review  
**Last Updated:** 2026-05-16

---

## 1. Context & Problem Statement

The AI Incident Intelligence Platform requires an LLM to power:

- RAG-based incident querying
- AI-generated root cause analysis (RCA)
- Incident summarization
- Log interpretation and anomaly explanation

The platform must operate under the following hard constraints:

- **Zero budget** — no paid API subscriptions, no cloud credits
- **No malware risk** — all dependencies must be from trusted, audited sources
- **Scalable** — the architecture must support growing data volumes without cost scaling
- **Production-ready** — the integration must be stable and maintainable

Three options were evaluated:

| Option | Type |
|---|---|
| Gemini API (Free Tier) | Cloud-hosted, API-based |
| Ollama (Local LLMs) | Self-hosted, locally-run |
| Hybrid (Gemini now, abstracted for swap) | Cloud + Local, provider-agnostic |

---

## 2. Option A — Gemini API (Free Tier)

### What It Is

Google's Gemini API offers a free tier via [Google AI Studio](https://aistudio.google.com/) with no credit card required to get started.

### Free Tier Limits (as of 2026)

| Model | Requests/min | Requests/day | Context Window |
|---|---|---|---|
| Gemini 1.5 Flash | 15 RPM | 1,500 RPD | 1M tokens |
| Gemini 1.5 Pro | 2 RPM | 50 RPD | 1M tokens |

> **Note:** Gemini 1.5 Flash is the recommended model for this platform — it has the most generous free limits and is fast enough for incident analysis workloads.

### Strengths

- No local hardware requirements
- Very large context window (1M tokens) — excellent for large log ingestion
- Fast inference
- Easy setup — just an API key
- No dependency on local GPU/CPU capacity
- Google-maintained, enterprise-grade reliability
- Python SDK available (`google-generativeai`)

### Weaknesses

- Rate limits can be hit under load (1,500 requests/day on free tier)
- Internet connection required — offline operation impossible
- Data is sent to Google's servers (privacy consideration for sensitive logs)
- Free tier may change or be deprecated at Google's discretion
- No SLA or uptime guarantees on free tier

### Privacy Risk

Operational logs sent to Gemini API will pass through Google's infrastructure. For sensitive enterprise environments, this may be a compliance concern. For MVP and portfolio purposes, this is acceptable.

---

## 3. Option B — Ollama (Local LLMs)

### What It Is

[Ollama](https://ollama.com/) is an open-source tool that allows running LLMs locally on your machine. It supports a wide range of open-source models including Llama 3, Mistral, Phi-3, and others.

### Recommended Models for This Platform

| Model | Size | RAM Required | Quality |
|---|---|---|---|
| `llama3.2:3b` | ~2GB | 8GB RAM | Good for summarization |
| `mistral:7b` | ~4GB | 8GB RAM | Strong reasoning |
| `phi3:mini` | ~2GB | 6GB RAM | Lightweight, fast |
| `llama3.1:8b` | ~5GB | 16GB RAM | Best local quality |

### Strengths

- Completely free — forever, no limits
- No internet required after model download
- Data never leaves your machine — full privacy
- No API key needed
- Unlimited requests — no rate limits
- Fully open-source, no vendor lock-in
- Works offline

### Weaknesses

- Requires significant local hardware (RAM, storage)
- Model quality is lower than Gemini 1.5 Pro/Flash for complex reasoning
- Slow on machines without a GPU
- Initial model download can be large (2–5GB per model)
- No 1M token context window — typically 4K–128K depending on model
- More complex setup

### Hardware Requirements

For this platform to run Ollama comfortably:

| Component | Minimum | Recommended |
|---|---|---|
| RAM | 8GB | 16GB |
| Storage | 10GB free | 20GB free |
| GPU | Not required | Helps significantly |
| CPU | Any modern CPU | Multi-core preferred |

---

## 4. Option C — Hybrid (Recommended)

### What It Is

The hybrid approach uses **Gemini free tier as the default LLM provider**, but builds the LLM integration behind a **provider abstraction layer**. This means the platform never directly calls `google.generativeai` in business logic — it calls an internal `LLMProvider` interface. Swapping to Ollama (or any other provider) requires changing a single config value, not rewriting code.

### Architecture Pattern

```
RAG Pipeline / Services
        ↓
  LLMProvider Interface  ← abstraction layer
        ↓
  ┌─────────────────────┐
  │  GeminiProvider     │  ← active (free tier)
  │  OllamaProvider     │  ← plug in anytime
  │  OpenAIProvider     │  ← future
  └─────────────────────┘
```

This is the standard **Strategy Pattern** applied to LLM provider selection.

### Why This is the Right Choice

1. **Starts free immediately** — Gemini free tier requires only an API key, no local hardware constraints.
2. **No rate limit lock-in** — if Gemini rate limits become a bottleneck, Ollama can be activated without touching business logic.
3. **Privacy upgrade path** — if sensitive log data requires local processing, switching to Ollama is a config change.
4. **Portfolio value** — demonstrates provider-agnostic architecture, which is a real engineering concern in production AI systems.
5. **Future-proof** — any new LLM provider can be added by implementing the interface.

---

## 5. Comparative Summary

| Criteria | Gemini Free Tier | Ollama Local | Hybrid |
|---|---|---|---|
| Cost | Free | Free | Free |
| Setup Complexity | Low | Medium | Medium |
| Response Quality | High | Medium | High (Gemini default) |
| Rate Limits | Yes (1,500/day) | None | Gemini limits; fallback to Ollama |
| Privacy | Low (cloud) | High (local) | Configurable |
| Offline Support | No | Yes | Partial |
| Hardware Requirements | Minimal | 8GB+ RAM | Minimal (Gemini default) |
| Context Window | 1M tokens | 4K–128K | 1M tokens (Gemini) |
| Scalability | Moderate | Hardware-bound | High |
| Architecture Flexibility | Low | Low | High |
| Production Readiness | Medium | Medium | High |
| **Portfolio Signal** | Weak | Weak | **Strong** |

---

## 6. Decision

**Selected Approach: Hybrid (Option C)**

**Primary provider:** Gemini 1.5 Flash (free tier)  
**Fallback / alternative provider:** Ollama (`mistral:7b` or `llama3.2:3b`)  
**Integration pattern:** Provider abstraction layer (`LLMProvider` interface)

---

## 7. Implementation Notes

### What Needs to Be Built

- `app/core/llm_provider.py` — Abstract base class / interface
- `app/core/providers/gemini_provider.py` — Gemini implementation
- `app/core/providers/ollama_provider.py` — Ollama implementation
- `app/core/config.py` — Provider selection via environment variable (`LLM_PROVIDER=gemini` or `LLM_PROVIDER=ollama`)

### Environment Variable Strategy

```env
# .env
LLM_PROVIDER=gemini
GEMINI_API_KEY=your_api_key_here
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=mistral:7b
```

No code changes required to switch providers — only `.env` changes.

---

## 8. Getting the Gemini API Key

1. Go to [https://aistudio.google.com/](https://aistudio.google.com/)
2. Sign in with a Google account
3. Click **"Get API Key"**
4. Create a new key (free, no billing required)
5. Copy the key into your `.env` file

---

## 9. Impact on Existing Documentation

| Document | Update Required |
|---|---|
| `TECH_STACK.md` | Update LLM section to reflect hybrid approach and provider abstraction |
| `AI_PIPELINE.md` | Update to show LLMProvider abstraction layer in the pipeline diagram |
| `ARCHITECTURE.md` | Minor update — LLM box to indicate provider-agnostic design |

---

## 10. References

- [Google AI Studio — Free Tier](https://aistudio.google.com/)
- [Gemini API Pricing & Limits](https://ai.google.dev/pricing)
- [Ollama Official Site](https://ollama.com/)
- [Ollama Model Library](https://ollama.com/library)
- [Strategy Pattern — Refactoring Guru](https://refactoring.guru/design-patterns/strategy)

---

---

# Updates

## Update 1 — Implementation Complete (2026-05-18)

**Status:** Decision implemented and operational.  
**Last Updated:** 2026-05-18

---

### Decision Outcome

The hybrid approach (Option C) was implemented as decided. The provider abstraction layer is live and working.

---

### Model Selection — Revised

The original decision specified `gemini-1.5-flash` as the primary model. During implementation, this model was found to be unavailable on the free tier API version. The following models were tested:

| Model | Result |
|---|---|
| `gemini-1.5-flash` | 404 — not found on API version v1beta |
| `gemini-1.5-flash-latest` | 404 — not found |
| `gemini-2.0-flash` | 429 — daily quota limit is 0 on free tier |
| `gemini-2.0-flash-lite` | 429 — daily quota limit is 0 on free tier |
| `gemini-2.5-flash` | ✅ Working — selected as active model |

**Revised active model:** `gemini-2.5-flash`

---

### Implementation Details

The abstraction layer was built exactly as planned, with one structural difference — the abstract base class lives at `app/core/providers/base.py` rather than `app/core/llm_provider.py` for better separation of concerns.

**Files implemented:**

| File | Purpose |
|---|---|
| `app/core/providers/base.py` | Abstract `BaseLLMProvider` interface |
| `app/core/providers/gemini_provider.py` | Gemini implementation with retry logic |
| `app/core/providers/ollama_provider.py` | Ollama implementation |
| `app/core/providers/__init__.py` | `get_llm_provider()` factory function |
| `app/core/config.py` | `LLM_PROVIDER`, `GEMINI_API_KEY`, `GEMINI_MODEL` settings |

---

### Retry Logic

The `GeminiProvider` implements automatic retry with exponential backoff using `tenacity`:
- Max attempts: 3
- Wait: exponential, min 2s, max 10s
- Handles transient 429 rate limit errors gracefully

---

### Free Tier Observations

The Gemini free tier has per-model daily quotas that vary significantly. New API keys may have zero quota on some models (`gemini-2.0-flash`) while having quota on others (`gemini-2.5-flash`). This is not documented clearly by Google and was discovered through testing.

**Recommendation:** Always test model availability with `provider.is_available()` before assuming a model works on a new API key.

---

### Environment Variable Strategy (as implemented)

```env
LLM_PROVIDER=gemini
GEMINI_API_KEY=your_api_key_here
GEMINI_MODEL=gemini-2.5-flash
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=mistral:7b
```

---

### Section 6 Correction

The decision table in Section 6 should be read with the following correction:

| Field | Original | Revised |
|---|---|---|
| Primary provider model | Gemini 1.5 Flash | `gemini-2.5-flash` |
| File path for base class | `app/core/llm_provider.py` | `app/core/providers/base.py` |