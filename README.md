# 🏆 Sports Brief Builder

> An agentic web application that creates sports briefings through natural language. The agent builds plans, executes tools, and requires user approval for sensitive actions.

---

## 📑 Table of Contents

| Section | Description |
|---------|-------------|
| [What & Why](#what-and-why) | Project overview and purpose |
| [Tools & Actions](#tools-and-actions) | Server tools and client behaviors |
| [Knowledge System](#knowledge-system) | Where knowledge lives and how it's used |
| [How to Run](#how-to-run) | Setup and testing |
| [Tradeoffs & Next Steps](#tradeoffs-and-next-steps) | Design decisions and improvements |

---

## What and Why

### What We Built
An end-to-end agentic application where an AI agent:
- Accepts natural language goals
- Creates execution plans autonomously
- Executes real server-side and client-side actions
- Searches a knowledge base (RAG)
- Requires user approval for sensitive operations
- Shows clear activity traces

### Why Sports?
Sports data provides an ideal domain for demonstrating:
- **Real-time data**: Live scores and game results
- **Rich knowledge**: Teams, players, rules, statistics
- **Natural requests**: "Create a brief about NFL playoffs"
- **Observable UI**: Scoreboards, charts, animations
- **Document workflows**: Brief creation, editing, exporting

**Tech Stack:** React + TypeScript, FastAPI + Python 3.11, SQLite, OpenAI GPT-4 Turbo, Docker

---

## Tools and Actions

### 🛠️ Server Tools (5 Real Actions)

| Tool | What It Does | Approval Required |
|------|-------------|-------------------|
| **fetch_live_scores** | Retrieves live sports scores and game results | No |
| **search_knowledge** | RAG search through knowledge base with relevance scoring | No |
| **save_brief** | Persists briefs to SQLite database | ✅ Yes |
| **generate_statistics** | Creates statistical analyses (player/team/season) | No |
| **export_brief** | Exports briefs as Markdown/TXT/JSON files | ✅ Yes |

### 🎨 Client Actions (Observable UI Changes)

| Action | Trigger | Observable Behavior |
|--------|---------|-------------------|
| **Scoreboard Widget** | `fetch_live_scores` | Animated card appears with team scores |
| **Statistics Chart** | `generate_statistics` | Bar chart animates (0.5s transitions) |
| **Knowledge Pulse** | `search_knowledge` | Used knowledge badges pulse 3x in amber |
| **Activity Log** | Every tool call | Real-time updates with color-coded status |
| **Brief Count** | `save_brief` (approved) | Counter increments, brief appears in sidebar |

---

## Knowledge System

### Where Knowledge Lives
1. **Database:** SQLite table `knowledge` (6 pre-loaded items: teams, players, rules, stats)
2. **User Additions:** Via UI upload (.txt/.md files) or manual form input
3. **No Vector DB:** Uses SQL LIKE queries for text matching and basic relevance scoring

### How It's Used
```
User Request → Knowledge Search → Relevant items retrieved from DB
     ↓
Context Enhancement → Knowledge added to agent's system prompt
     ↓
Agent Uses Knowledge → LLM generates response informed by knowledge
     ↓
UI Feedback → "Knowledge Used" card shows which items influenced response
```

**Visibility:** The UI makes knowledge influence obvious through:
- Knowledge Used card with relevance badges (high/medium/low)
- Pulse animations on knowledge items when actively used
- Activity log showing `search_knowledge` execution details
- Influence banner explaining knowledge impact

---

## How to Run

### Quick Start (5 minutes)

1. **Get OpenAI API key** from https://platform.openai.com/api-keys

2. **Configure environment:**
   ```bash
   cp .env.example .env
   nano .env  # Add your OpenAI API key
   ```

3. **Start application:**
   ```bash
   bash start.sh
   ```

4. **Test it works:**
   ```bash
   bash test.sh
   ```

5. **Open browser:** http://localhost:3000

### Try These Prompts
- "Create a brief about the latest NFL games"
- "Show me latest football scores"
- "Generate player performance statistics"
- "Tell me about NBA teams using the knowledge base"
- "Create a brief and save it to database" *(tests approval flow)*

### Architecture
```
React UI (TypeScript) ←→ FastAPI (Python) ←→ SQLite DB
     ↓                          ↓
Client Actions           Server Tools
- Scoreboard            - fetch_live_scores
- Charts                - search_knowledge
- Animations            - save_brief
                        - generate_statistics
                        - export_brief
```

---

## Tradeoffs and Next Steps

### Design Decisions

| Choice | Why | Tradeoff | Production Path |
|--------|-----|----------|-----------------|
| **Simulated Sports API** | No API key complexity, predictable demos | Not truly "live" data | Replace with ESPN/Sportradar API |
| **SQL LIKE Search** | No extra dependencies, instant setup | Less sophisticated relevance | Add pgvector or Pinecone embeddings |
| **Single GPT-4 Call** | Simple architecture, low latency | Less specialized behavior | Multi-agent system (planner/executor/writer) |
| **Synchronous Tools** | Predictable order, easier debugging | Slower for many tools | Parallel execution where safe |
| **SQLite** | Zero setup, embedded database | Limited concurrency | PostgreSQL for production |

### What We Prioritized
✅ **End-to-end completeness** over depth in one area  
✅ **Observable behavior** over background processing  
✅ **Clear UI feedback** over advanced AI capabilities  
✅ **User approval** over full automation  
✅ **Development speed** over production optimization  

### Next Steps

**Short Term:**
- Real sports API integration (ESPN/Sportradar)
- Vector embeddings for semantic search (OpenAI text-embedding-3)
- Streaming responses via SSE

**Medium Term:**
- Multi-agent architecture (specialist agents per domain)
- Approval history and undo functionality
- Rich client visualizations (timelines, formation diagrams)

**Long Term:**
- User accounts and personalization
- Collaboration features (share briefs, comments)
- Advanced analytics on agent performance

---

## 📝 License

MIT License - Use as a template for your own agentic applications!

---

**Built with ❤️ for demonstrating end-to-end agentic web applications**

**See detailed documentation:** [API.md](API.md) | [PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md) | [WEB_PROOF.md](WEB_PROOF.md)