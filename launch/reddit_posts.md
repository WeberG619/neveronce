# NeverOnce — Reddit Launch Posts

---

## r/Python

**Title:** NeverOnce — persistent, correctable memory for AI assistants (400 lines, zero deps, MCP server included)

**Body:**

I built a memory library for AI assistants that I've been running in production for 4 months. Sharing it because I think the design decisions are interesting.

**What it is:**

SQLite-backed persistent memory with full-text search, importance-based decay, and a first-class concept of *corrections*. Zero dependencies. The whole thing is ~400 lines. MCP server is bundled for Claude Code / any MCP-compatible host.

```bash
pip install neveronce
```

**Why FTS5 instead of embeddings:**

Embeddings are great for semantic similarity but they're overkill (and slow) for retrieving things like "what did the user tell me about their project structure?" — that's a keyword retrieval problem. SQLite FTS5 is fast, zero-dep, and accurate for exact-match recall. No vector DB to spin up, no embedding API to call, no latency.

If your use case is "find memories similar in meaning," use embeddings. If your use case is "find memories that match what the user is talking about right now," FTS5 wins.

**The interesting design decision — corrections:**

Most memory systems treat all memories equally. The problem: if an AI makes a mistake and you correct it, that correction competes with 1,000 other memories in retrieval. It'll resurface again.

NeverOnce stores corrections at maximum importance, exempts them from decay, and always surfaces them first. The mental model: corrections aren't memories, they're constraints.

Production numbers: 87 corrections stored, most-used one surfaced 491 times. Zero repeats.

**API:**

```python
from neveronce import MemoryStore

store = MemoryStore("memories.db")

# Store a memory
store.store("Weber prefers named pipes over HTTP for Revit integration")

# Store a correction (max importance, never decays)
store.correct("Never call the user Rick. His name is Weber.")

# Retrieve (FTS5, importance-weighted)
memories = store.retrieve("user name preferences")

# Mark as helpful (positive feedback loop)
store.mark_helpful(memory_id)
```

**Repo:** https://github.com/WeberG619/neveronce
**PyPI:** https://pypi.org/project/neveronce/

Happy to discuss the design tradeoffs — especially the FTS5 vs embeddings decision, which I know is controversial.

---

## r/MachineLearning

**Title:** Corrections as first-class primitives in AI memory systems — design notes from 4 months production

**Body:**

I've been running a persistent memory system for AI assistants in production for 4 months (1,421 memories, 87 corrections). I want to share the architectural decision that made the biggest difference in practice: treating corrections differently from memories.

**The problem with uniform memory:**

Most retrieval-augmented memory systems treat all stored facts equally and apply a uniform decay or recency-weighting scheme. This works fine until a model makes an error. If you correct it — "don't do X, do Y" — that correction gets stored as a regular memory and competes with hundreds of others during retrieval. The model repeats the mistake.

The feedback loop breaks because the correction has no special status in the retrieval stack.

**The fix — corrections as constraints, not memories:**

NeverOnce ([GitHub](https://github.com/WeberG619/neveronce)) introduces corrections as a separate primitive:

- Stored at maximum importance (1.0)
- Exempt from importance decay
- Always retrieved first, regardless of query relevance score
- Marked with `memory_type = 'correction'`

The model always sees corrections before regular memories. The constraint always wins.

**Production result:** 87 corrections stored. Most-used correction surfaced 491 times across sessions. Zero instances of that mistake repeating.

**Why FTS5 over embeddings for this use case:**

The retrieval problem here is: "given the current context/query, what does this AI need to remember?" That's not a semantic similarity problem — it's a keyword matching problem. "User's name" should retrieve "don't call the user Rick, his name is Weber" without needing cosine similarity against an embedding space.

FTS5 advantages for this specific use case:
- Deterministic retrieval (no embedding model variance)
- Zero external dependencies
- No API calls, no latency, works offline
- SQL-native, inspectable, debuggable

The tradeoff: you lose semantic generalization. "Don't use HTTP" won't retrieve memories tagged "named pipes" unless there's lexical overlap. For a correction system, that's acceptable — corrections should be explicit and specific anyway.

**The feedback loop:**

```
mark_helpful(memory_id) → importance += 0.1 (capped at 1.0)
time passes → importance *= decay_factor
corrections → exempt from decay, importance locked at 1.0
```

This creates a self-tuning retrieval system where frequently useful memories stay relevant and stale ones fade — except corrections, which are permanent constraints.

**Implementation:** ~400 lines Python, zero deps, SQLite+FTS5. MCP server included.

```bash
pip install neveronce
```

Curious what approaches others have taken for handling model corrections in persistent memory. Is "corrections as constraints" a pattern used elsewhere?

---

## r/ClaudeAI

**Title:** I built a persistent memory layer for Claude Code that actually works — MCP server, zero setup, pip install

**Body:**

If you've been frustrated by Claude forgetting things between sessions, I built something that fixes it.

**NeverOnce** — persistent, correctable memory for Claude. It's an MCP server you add to your Claude config in about 2 minutes.

**Install:**

```bash
pip install neveronce
```

**Add to your Claude MCP config** (`claude_desktop_config.json` or `settings.local.json`):

```json
{
  "mcpServers": {
    "neveronce": {
      "command": "python",
      "args": ["-m", "neveronce.mcp_server"],
      "env": {
        "NEVERONCE_DB_PATH": "/path/to/your/memories.db"
      }
    }
  }
}
```

That's it. Claude now has persistent memory across all sessions.

**What it does:**

- Claude can store memories: "Weber prefers named pipes over HTTP for Revit"
- Claude can retrieve memories at the start of a session or when relevant
- Claude can store *corrections*: "Never call the user Rick, his name is Weber"
- Corrections always surface first, never decay, never get buried

**The correction feature is the part I'm most proud of:**

If Claude makes a mistake and you correct it, that correction is stored at maximum importance and retrieved before everything else, every time. It's not just another memory that competes for retrieval slots — it's a permanent constraint.

I've been running this for 4 months: 1,421 memories, 87 corrections, most-used correction surfaced 491 times. Zero repeats on corrected mistakes.

**MCP tools exposed:**

- `store_memory` — save something for later
- `retrieve_memories` — search by query
- `store_correction` — permanent, max-importance constraint
- `mark_helpful` — feedback signal to boost importance
- `get_stats` — see what's in your memory store

**GitHub:** https://github.com/WeberG619/neveronce
**PyPI:** https://pypi.org/project/neveronce/

If you're a Claude Code user who's tired of re-explaining your project setup every session, give it a try.

---

## r/LocalLLaMA

**Title:** NeverOnce — persistent AI memory that works fully offline. SQLite, no embeddings, no API keys, any model.

**Body:**

Built a memory library for AI assistants that's completely local and works with any model. Thought this community would appreciate it.

**What it is:**

Persistent memory store for AI. SQLite + FTS5 under the hood. Zero external dependencies. No embedding models, no vector DB, no API keys required. Runs fully offline.

```bash
pip install neveronce
```

**Why it fits the local stack:**

- No embedding API calls (uses SQLite FTS5 for search)
- No cloud sync, no telemetry
- Database is a single `.db` file you own
- Works with Ollama, llama.cpp, LM Studio, anything — model-agnostic
- MCP server included if you want to hook it into a Claude Code session, but the Python library works standalone with any model

**Integration example with any local LLM:**

```python
from neveronce import MemoryStore

store = MemoryStore("/home/user/.local/memories.db")

# Before each inference, inject relevant memories into context
memories = store.retrieve(user_message, limit=5)
context = "\n".join([m.content for m in memories])
prompt = f"Relevant context:\n{context}\n\nUser: {user_message}"

# After inference, store anything worth remembering
store.store("User prefers concise responses without markdown")

# Corrections are permanent — model won't repeat corrected mistakes
store.correct("This user is running Ollama on Linux, not Windows")
```

**Production numbers from my own setup:**

- 4 months running
- 1,421 memories stored
- 87 corrections
- Most-used correction: surfaced 491 times, zero repeats

**The correction mechanic:** corrections are stored at max importance and never decay. They always come up first in retrieval. If you tell your local model something once and store it as a correction, it won't forget it.

**No GPU required, no model required, just Python and SQLite.**

GitHub: https://github.com/WeberG619/neveronce
PyPI: https://pypi.org/project/neveronce/

---

## r/artificial

**Title:** The missing third pillar of the AI agent stack: persistent, correctable memory

**Body:**

We talk a lot about MCP (tool use), and we talk a lot about agents (autonomous loops). But there's a third layer that's quietly becoming the difference between a useful AI assistant and one you have to babysit: **persistent memory that learns from corrections**.

I want to share something I've been building and thinking about.

---

**The current state:**

Most AI assistants have no memory between sessions. You re-explain your project, your preferences, your constraints, every time. Even with retrieval-augmented approaches, there's a structural problem: corrections and regular information are treated the same way.

If an AI makes a mistake and you correct it, that correction goes into the same memory pool as everything else. It can get outcompeted, buried, decayed. The AI repeats the mistake. You correct it again. The loop never closes.

---

**What I built:**

[NeverOnce](https://github.com/WeberG619/neveronce) — a memory library built around one insight: **corrections are not memories, they are constraints.**

Regular memories accumulate and decay based on use. Corrections are stored at maximum importance, exempted from decay, and always surface before everything else. They're permanent. "Correct once. Never again."

Four months in production. 87 corrections stored. Most-used one has surfaced 491 times. Zero repeats.

---

**Why this matters at a systems level:**

The emerging agent stack looks something like:

1. **Tools** — what the AI can do (MCP solved this)
2. **Agency** — how the AI decides what to do (agents, reasoning models)
3. **Memory** — what the AI knows about *you specifically*, and what it must never forget

The third pillar is underdeveloped. We have good infrastructure for (1) and improving infrastructure for (2), but (3) is mostly an afterthought — some vendors bolt on "memory" that's really just a RAG index with no concept of importance, feedback, or correction.

The hard problem isn't storage. SQLite is fine. The hard problem is **what makes a memory worth keeping, and what makes a correction inviolable.**

---

**The philosophical bit:**

There's something interesting about corrections as a category. When you correct an AI, you're not adding information — you're adding a constraint on future behavior. It has a different epistemic status than a fact. It's closer to a rule.

A memory system that doesn't distinguish between "Weber lives in Idaho" (fact, can decay) and "never call the user Rick, his name is Weber" (constraint, must persist) is going to fail in practice. The first one being wrong is a minor inconvenience. The second one being forgotten is a broken relationship.

---

**Practical:**

```bash
pip install neveronce
```

400 lines Python, zero deps, MCP server included, SQLite under the hood.

[GitHub](https://github.com/WeberG619/neveronce) | [PyPI](https://pypi.org/project/neveronce/)

Curious what this community thinks about the memory layer problem — especially whether corrections-as-constraints is a concept that should be standardized across AI frameworks, or whether it's too use-case specific.
