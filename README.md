# 🗳️ Promise Tracker
### AI-Powered Political Accountability — Nonpartisan, Evidence-Based

> *"Politicians make hundreds of promises. Nobody tracks them. We do."*

---

## 🏆 Hackathon Track

**Track 3: Governance & Accessibility**

Democracy is struggling because people feel unheard, divided, and too confused to participate. One of the biggest reasons citizens disengage from politics is broken trust — politicians promise things, get elected, and nobody systematically holds them accountable.

Promise Tracker directly addresses:
- **Legislative transparency** — every promise mapped to real news evidence and legislative action
- **Nonpartisan voter education** — no opinions, just facts and sources
- **Rebuilding trust** — citizens can see exactly what was promised and what happened
- **Accessibility** — complex political actions explained in plain English, not political jargon

---

## 🌍 What is Promise Tracker?

Promise Tracker is an AI-powered platform that:

1. Collects campaign promises from political leaders
2. Scrapes real news coverage daily from credible sources
3. Uses AI to analyze whether each promise was **kept, broken, in progress, partial, or reversed**
4. Presents verdicts in a clean, accessible interface — no political bias, no opinion

Currently tracking:
- 🇺🇸 **Donald Trump** — US President (2024 campaign promises)
- 🏛️ **Wes Moore** — Governor of Maryland
- 🇮🇳 **Narendra Modi** — Prime Minister of India

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────┐
│                   Promise Tracker                    │
│                                                     │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐ │
│  │ Trump Agent │  │Moore Agent  │  │ Modi Agent  │ │
│  │             │  │             │  │             │ │
│  │ US Sources  │  │ MD Sources  │  │ IN Sources  │ │
│  │ Google News │  │ Google News │  │ Google News │ │
│  │ NPR         │  │ NPR         │  │ The Hindu   │ │
│  │ WaPo        │  │ WaPo        │  │ NDTV        │ │
│  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘ │
│         │                │                │         │
│         └────────────────┼────────────────┘         │
│                          ↓                          │
│                   Claude AI (Verdict)               │
│                   Isolated per politician           │
│                          ↓                          │
│                   SQLite Database                   │
│                          ↓                          │
│              FastAPI Backend (REST API)             │
│                          ↓                          │
│              HTML/CSS/JS Frontend                   │
└─────────────────────────────────────────────────────┘
```

### Key Design Decision — Separate Agents Per Politician

Each politician runs as an **isolated agent** with its own:
- Promise database
- News sources (country/region specific)
- Claude AI context window (no cross-contamination)

This means when Claude analyzes Modi's promises, it has **zero knowledge** of Trump's promises in that context — eliminating hallucination risk and keeping verdicts laser-focused.

```python
# Each agent has its own system prompt
POLITICIAN_CONTEXT = {
    "trump": "US President Donald Trump's 2024 campaign promises.",
    "wes_moore": "Maryland Governor Wes Moore's campaign promises.",
    "modi": "Indian Prime Minister Narendra Modi's BJP manifesto promises.",
}
```

---

## 🤖 How Claude AI Powers This

We use the **Claude API** (via Groq's hosted Llama model for the hackathon, Claude API in production) as the reasoning engine for verdict generation.

### The Verdict Pipeline

```
Promise text + News headlines from 3-5 sources
              ↓
        Claude receives:
        - The exact promise
        - Recent news coverage as evidence
        - Strict nonpartisan instructions
              ↓
        Claude returns structured JSON:
        {
          "status": "kept|broken|in_progress|partial|reversed|unknown",
          "verdict": "2-3 sentence factual explanation",
          "confidence": "high|medium|low"
        }
              ↓
        Stored in SQLite, served via FastAPI
```

Claude is explicitly instructed to:
- Use **only the provided evidence** — no outside opinions
- Be **factual and nonpartisan** — no political leaning
- Cite **what actually happened** — not what should have happened
- Return **structured output** — not free-form text

---

## 📰 Data Sources

We pull from multiple credible, nonpartisan sources daily:

| Source | Type | Coverage |
|---|---|---|
| Google News RSS | Aggregator | All politicians |
| NPR Politics | Public radio | US politicians |
| Washington Post | Newspaper | US politicians |
| The Hindu | Newspaper | Modi/India |
| NDTV | News channel | Modi/India |

No opinion sites. No partisan blogs. No social media. Only established news organizations.

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| AI Reasoning | Claude API / Groq (llama-3.3-70b) |
| Backend | Python + FastAPI |
| Database | SQLite |
| News Scraping | Google News RSS + httpx |
| Frontend | HTML + CSS + Vanilla JS |
| Email Digest | SendGrid (roadmap) |

---

## 🚀 Running Locally

```bash
# Install dependencies
pip install fastapi uvicorn httpx groq pydantic

# Initialize database
cd backend
python database.py

# Scrape latest news
python scraper.py

# Generate AI verdicts
python verdict.py

# Start API server
python main.py

# Open frontend
# Just open frontend/index.html in your browser
```

Add your Groq API key in `verdict.py`:
```python
GROQ_API_KEY = "your_key_here"
```

---

## ⚠️ Ethical Concerns & Safeguards

### Can This Be Used as Propaganda?

This is a real and important concern we thought deeply about.

**The risks:**
- A bad actor could selectively add promises that make one politician look worse
- News sources could be cherry-picked to skew verdicts
- The "broken" label could be weaponized in political ads

**Our safeguards:**

**1. Evidence transparency**
Every verdict links to the actual news articles used. Users can click through and read the original source. Nothing is hidden.

**2. Confidence scoring**
Claude returns a confidence level (high/medium/low) with every verdict. Low-confidence verdicts are surfaced as "unknown" rather than a definitive judgment.

**3. Nonpartisan prompt engineering**
Claude is explicitly instructed to be nonpartisan in every prompt. The system prompt never contains political opinions or framing.

**4. Multi-source requirement**
Verdicts are only generated when multiple sources are available. A single biased article cannot determine a verdict.

**5. Equal treatment across politicians**
The same pipeline, same sources, same Claude prompt runs for every politician regardless of party, country, or ideology. A Democrat and Republican get identical treatment.

**6. Open source**
The entire codebase is open — anyone can audit exactly what sources were used and what Claude was told to analyze them.

### What We Don't Do
- ❌ We do not editorialize or add opinions
- ❌ We do not selectively show promises to make politicians look good or bad
- ❌ We do not use social media or partisan sources
- ❌ We do not take political donations or have political affiliations
- ❌ We do not allow users to submit promises (to prevent manipulation)

### Limitations We Acknowledge
- AI can make mistakes — verdicts should be verified by reading the linked sources
- News coverage has its own biases — we mitigate this with multiple sources
- Some promises are genuinely hard to measure — we label these "unknown" rather than guessing
- Our promise list is curated by humans — we are transparent about which promises we track and why

---

## 📬 Email Digest — Subscribe for Updates

Users can subscribe to receive a **daily email digest** of promise status changes for any politician they follow.

How it works:
1. Enter your email on any politician's page
2. Select which politician you want to follow
3. Every day, receive a summary of:
   - Promises whose status changed
   - New news coverage on tracked promises
   - Overall kept/broken rate update



Subscriptions are stored securely in the database. Email delivery via SendGrid.

---

## 🔮 Roadmap

- [ ] Add more world leaders (UK PM, French President, Canadian PM)
- [x] Daily email digest — users can subscribe to receive promise updates for their favorite politician
- [ ] Historical tracking — see how a verdict changed over time
- [ ] Congress.gov API integration for legislative evidence
- [ ] Public API for researchers and journalists
- [ ] Mobile app

---

## 🎯 Why This Matters

In 2024, trust in government hit historic lows across the world. People don't vote because they don't believe politicians follow through. Promise Tracker gives citizens a simple, honest answer to the most basic political question:

**"Did they do what they said they'd do?"**

No spin. No agenda. Just facts.

---

## 👥 Team

Built **solo** at the **Claude AI Hackathon** at University of Maryland, April 2026.

This entire project — architecture, backend, frontend, AI pipeline, data sources, and ethical framework — was designed and built by one person during the hackathon.

---

## 📄 License

MIT License — open source, free to use, audit encouraged.