---
title: "Why I Built NeverOnce: The Correction Pattern Nobody Is Doing"
published: false
description: I was tired of correcting my AI every session. After 4 months and 491 correction surfaces, I open-sourced the fix — 400 lines of Python, zero dependencies, corrections as first-class primitives.
tags: ai, python, opensource, machinelearning
cover_image:
---

One correction. 491 times surfaced. Zero repeats.

That number changed how I think about AI memory. And it's why I open-sourced [NeverOnce](https://github.com/WeberG619/neveronce) — a 400-line Python library that treats corrections as first-class primitives, not afterthoughts.

Let me back up.

---

## The Amnesia Tax

I'm a BIM specialist. I run AI-assisted workflows all day — Revit automation, construction document processing, client deliverables. Claude, Cursor, custom agents. AI is core to how I work.

And every single session, I was paying what I started calling the **amnesia tax**.

You know the feeling. You spend 15 minutes telling your AI assistant how you work. "I use named pipes, not HTTP." "Always format dates like this." "Never do X — I told you last week, we tried it, it broke everything." The AI nods along, does it right for the rest of the session. Then the session ends. Next morning, you start over.

The 1M context window isn't memory. It's short-term recall that dies when the tab closes. That's a brilliant employee with anterograde amnesia — perfect recall within a conversation, zero retention between them.

I got tired of it. So I built the fix.

---

## What I Actually Needed

Most AI memory systems I looked at do two things:

1. **Store** — Save some text to a database
2. **Recall** — Find relevant text when asked

That's it. And that's fine for general facts. But it completely fails for corrections.

Here's the difference:

- A **memory** is something I want the AI to know: "client prefers PDF deliverables"
- A **correction** is something the AI got wrong and must never get wrong again: "do NOT use the HTTP endpoint — it's deprecated and breaks silently"

These are architecturally different things. A correction isn't just a high-importance memory. It's a **behavioral override** — it should surface first, stay at full strength regardless of usage patterns, and never fade. It's the difference between a sticky note and a stop sign.

No library I found treated corrections as their own primitive. So I built one that does.

---

## NeverOnce: The Five-Step Loop

NeverOnce is built around a loop I call **Store → Recall → Correct → Feedback → Decay**.

```python
pip install neveronce
```

```python
from neveronce import Memory

mem = Memory("my_workflow")
```

### Step 1: Store

```python
mem.store("client prefers detailed cost breakdowns in proposals")
mem.store("Revit 2026 uses named pipes — not HTTP sockets")
```

Under the hood: SQLite + FTS5, BM25 ranking. No external dependencies. No API calls. Just Python's built-in `sqlite3`.

### Step 2: Recall

```python
results = mem.recall("how does the client want proposals formatted?")
for r in results:
    print(r['content'])
```

BM25 handles relevance ranking. Corrections always surface before regular memories — more on that in a second.

### Step 3: Correct (the important one)

```python
mem.correct("NEVER use HTTP for the Revit API — always use named pipes. HTTP causes silent timeouts.")
```

This is where NeverOnce diverges from everything else. Corrections are stored with:

- **Max importance score** (1.0) — they always rank first
- **Decay immunity** — they don't fade over time, ever
- **Type flag** — they're queryable separately from regular memories
- **Always-first surfacing** — when you call `recall()`, corrections matching the query come back before any regular memory, regardless of BM25 score

The implementation is dead simple, which is kind of the point:

```python
def correct(self, content: str, context: str = "") -> int:
    """Store a correction — max importance, immune to decay."""
    return self._store_memory(
        content=content,
        memory_type="correction",
        importance=1.0,
        tags=["correction"],
        context=context
    )
```

And in recall:

```python
# Corrections always surface first
corrections = self._query_corrections(query, limit=5)
regular = self._query_regular(query, limit - len(corrections))
return corrections + regular
```

Simple. Obvious. Nobody was doing it.

### Step 4: Feedback

```python
mem.feedback(memory_id, helpful=True)   # strengthens importance
mem.feedback(memory_id, helpful=False)  # weakens importance
```

When a memory helps, it gets stronger. When it doesn't, it gets weaker. This builds a signal over time about what's actually useful vs. what's just noise from months ago.

Corrections are immune to negative feedback decay — a behavioral override can't be weakened by "this wasn't relevant right now." It stays at 1.0.

### Step 5: Decay

```python
mem.decay()  # run periodically — daily, weekly, whatever makes sense
```

Regular memories fade if they're not helping. This keeps your memory store from becoming a graveyard of stale context. Corrections never decay. Everything else competes.

---

## The Pre-Flight Check Pattern

One pattern I use constantly in production:

```python
# Before taking any significant action, check for corrections
warnings = mem.check("setting up HTTP connection to Revit API")
if warnings:
    print("Warning — corrections apply:")
    for w in warnings:
        print(f"  [{w['importance']:.1f}] {w['content']}")
```

`check()` returns corrections that match the action you're about to take. It's a pre-flight gate. Run it before any consequential operation and you get a behavioral safety net built from your own correction history.

In my Revit automation workflows, every tool call goes through a check. The AI proposes an action, we check corrections, we either proceed or surface the override. This single pattern eliminated entire categories of repeated mistakes.

---

## Production Numbers (4 Months In)

I've been running this on my actual daily workflows since November. Here's what the database looks like today:

| Metric | Value |
|--------|-------|
| Total memories | 1,421 |
| Corrections | 87 |
| Most-surfaced correction | 491 times |
| Repeated mistakes after correction | 0 |

That most-surfaced correction? It's about a specific API behavior in my Revit bridge that bit me once in a spectacular way. I stored the correction, the feedback loop has surfaced it 491 times across dozens of sessions, and I have not made that mistake again. Not once.

That's the number that convinced me this architecture is right. It's not just "memory." It's **behavioral memory** — the AI's accumulated understanding of how I specifically work, what I specifically need, and what I specifically cannot tolerate it getting wrong.

---

## Why SQLite + FTS5 (And Not a Vector DB)

I want to address this directly because it always comes up.

NeverOnce uses SQLite with the FTS5 full-text search extension, not a vector database. No embeddings. No API calls. No external dependencies whatsoever.

The choice is intentional:

**Corrections are semantic overrides, not similarity queries.** When I store "never use HTTP — use named pipes," I need that to surface when someone asks about "connection method" or "API transport" or "socket setup." BM25 with FTS5 handles this well. It's keyword and phrase matching with TF-IDF weighting — fast, local, zero cost.

**Zero dependencies is a feature, not a limitation.** The library is 400 lines. You can read the whole thing in 20 minutes. There's nothing magic in it. You can fork it, audit it, modify it, understand it completely. Vector DBs introduce operational complexity — embedding models, API latency, rate limits, cost. For a correction system running on your local machine, that's the wrong tradeoff.

**SQLite is everywhere.** Python ships with sqlite3. No setup, no process, no daemon. The database is a single file on disk. Backup is `cp`. Migration is `cp`. Disaster recovery is `cp`.

For the use case NeverOnce is solving — behavioral corrections for a single developer's workflow — BM25 is the right tool. If you're building a knowledge base for 10,000 users with semantic search requirements, use a vector DB. If you're building a correction layer for your own AI workflows, SQLite is fine.

---

## The MCP Server

NeverOnce ships with an MCP server out of the box. If you're running Claude Code, Cursor, or any other MCP-compatible client:

```bash
# Install
pip install neveronce

# Add to your MCP config (Claude Code example)
# In settings.json:
{
  "mcpServers": {
    "neveronce": {
      "command": "python",
      "args": ["-m", "neveronce.mcp_server"]
    }
  }
}
```

Your AI client immediately gets access to `store_memory`, `recall_memory`, `store_correction`, `check_before_action`, and `memory_feedback` as tools it can call directly.

This is where it gets interesting. The AI isn't just passively reading from memory — it's actively building it. Claude Code can store what it learns about your codebase. It can correct itself when you push back. It can check its own correction history before proposing something it knows you've rejected before.

That's the vision: not just an AI with memory, but an AI that learns from its own behavioral history with you specifically.

---

## The Stack: MCP + Agents + NeverOnce

Here's how I think about the current AI tooling moment:

- **MCP** solves the tool connectivity problem — your AI can call external services
- **Agents** solve the multi-step reasoning problem — your AI can execute workflows
- **NeverOnce** (or something like it) solves the behavioral memory problem — your AI can learn from corrections

The first two are largely solved. The third is not. There are production-grade agent frameworks. There are MCP servers for everything. There is no standard for "here's what this AI has learned about how I work, and here's what it must never do again."

That's the gap I'm trying to fill. Not by building a better vector database or a smarter embedding model — by defining the correction as a primitive and building a system where corrections are first-class, permanent, and immune to drift.

---

## Getting Started

```bash
pip install neveronce
```

```python
from neveronce import Memory

mem = Memory("my_project")

# Store what matters
mem.store("client is in EST timezone — all meetings before 3pm PST")

# Correct what was wrong
mem.correct("NEVER send draft documents directly — always export to PDF first")

# Check before acting
warnings = mem.check("sending the document to client")
# Returns: [{'content': 'NEVER send draft documents...', 'importance': 1.0}]

# Recall relevant context
context = mem.recall("client communication preferences")
```

The full source is at [github.com/WeberG619/neveronce](https://github.com/WeberG619/neveronce). MIT licensed. 400 lines. 11 tests. Zero dependencies beyond Python's standard library.

---

## What I Learned Building This

The insight that made this project click for me: **AI memory systems are usually designed by people thinking about knowledge retrieval, not behavioral correction.**

Knowledge retrieval is "help me find the thing I stored." Behavioral correction is "make sure I never make that mistake again, regardless of context, regardless of how much time has passed, regardless of whether the specific query matches."

Those require different architectures. The correction can't just be a high-importance memory — it needs to be a behavioral override that surfaces proactively, stays immune to decay, and applies to related queries even when the wording doesn't match exactly.

Once I understood that distinction, the implementation became obvious. Corrections go in a separate type with separate surfacing logic and separate decay rules. They're not memories that happen to be important. They're a different thing entirely.

491 surfaces. Zero repeats. That's the proof it works.

---

*Weber Gouin is a BIM specialist and principal at [BIM Ops Studio](https://bimopsstudio.com), building AI-assisted workflows for the AEC industry. NeverOnce is at [github.com/WeberG619/neveronce](https://github.com/WeberG619/neveronce).*
