# 🏆 Sports Brief Builder

> An agentic web application that creates comprehensive sports briefings through natural language. The agent builds plans, fetches live data, searches knowledge, and requires user approval for sensitive actions.

---

## 📑 Table of Contents

| Section | Description |
|---------|-------------|
| [🚀 Quick Start](#quick-start) | Get up and running in 5 steps |
| [🎯 Features](#features) | Server tools, client actions, knowledge system |
| [🏗️ Architecture](#architecture) | Tech stack and system design |
| [📚 Tools & Actions](#tools-actions) | Detailed breakdown of all capabilities |
| [💡 Knowledge System](#knowledge-system) | How RAG works and adding knowledge |
| [🔒 Safety & Control](#safety-control) | Approval flows and data protection |
| [📖 Examples](#examples) | Real-world usage scenarios |
| [🤝 Contributing](#contributing) | How to extend the project |

---

<a id="quick-start"></a>

## 🚀 Quick Start

### ⚙️ Setup (5 minutes)

**Step 1: Get OpenAI API Key**
- Visit https://platform.openai.com/api-keys
- Create a new secret key

**Step 2: Configure Environment**
```bash
cd /home/malek/SportradarEx
cp .env.example .env
nano .env  # Add your OpenAI API key
```

**Step 3: Start Application**
```bash
bash start.sh
```

**Step 4: Open in Browser**
- **Frontend:** http://localhost:3000
- **Backend API:** http://localhost:8000
- **API Docs:** http://localhost:8000/docs

**Step 5: Verify Installation**
```bash
bash test.sh
```

### 🎯 Try These Prompts
| Prompt | What It Does |
|--------|-------------|
| "Create a brief about the latest NFL games" | Fetches scores & generates analysis |
| "Show me latest football scores" | Live sports data with visualization |
| "Generate player performance statistics" | Creates animated stat charts |
| "Tell me about NBA teams" | Searches knowledge base |
| "Create a brief and save it" | Full workflow with approval |

### 📚 Add Your Knowledge
1. Click "Add Knowledge" in the UI
2. Upload `.txt` or `.md` file (or fill form manually)
3. Agent now has access to your knowledge

### ✅ Test Approval Flow
1. Type: *"Create a brief about NFL and save it to database"*
2. Review action in **Approval Modal**
3. Click **Approve** or **Reject**
4. Check **Saved Briefs** sidebar for result

### ❌ Troubleshooting

| ⚠️ Issue | ✅ Solution |
|---------|---------|
| Port already in use | `docker-compose down` |
| OpenAI API Error | Check API key, verify credits |
| Frontend won't load | `docker-compose up --build frontend` |
| Database issues | `rm -rf data/*.db && docker-compose restart backend` |

---

<a id="architecture"></a>

## 🏗️ Architecture

### 🔧 Tech Stack
| Component | Technology |
|-----------|-----------|
| **Frontend** | React 18 + TypeScript |
| **Backend** | FastAPI (Python 3.11) |
| **Database** | SQLite |
| **LLM** | OpenAI GPT-4 Turbo |
| **Deployment** | Docker + Docker Compose |

### 📊 System Design
```
┌─────────────┐         ┌──────────────┐         ┌─────────────┐
│   React UI  │ ◄────► │  FastAPI     │ ◄────► │  SQLite DB  │
│ (TypeScript)│  HTTP   │  (Python)    │         │             │
└─────────────┘         └──────────────┘         └─────────────┘
      │                        │
      │                        │
      ▼                        ▼
 Client Actions          Server Tools
 - Scoreboard           - fetch_live_scores
 - Charts               - search_knowledge
 - Highlights           - save_brief
 - Activity Log         - generate_statistics
                        - export_brief
```

<a id="features"></a>

## 🎯 Features

### 🛠️ Server Tools (5 Actions)

| Tool | Purpose | Details |
|------|---------|---------|
| **📊 fetch_live_scores** | Get live sports data | Returns game scores, status, dates |
| **🔍 search_knowledge** | RAG search | SQL queries with relevance scoring |
| **💾 save_brief** | Store briefs | Database persistence (⚠️ requires approval) |
| **📈 generate_statistics** | Create analyses | Calculates stats, trends, predictions |
| **📥 export_brief** | Download briefs | Markdown/TXT/JSON export (⚠️ requires approval) |

### 🎨 Client-Side Actions (Observable Behaviors)

| Action | Trigger | Effect |
|--------|---------|--------|
| **🏆 Scoreboard Widget** | `fetch_live_scores` call | Animated scores with gradient background |
| **📊 Statistics Chart** | `generate_statistics` call | Animated bar charts (0.5s transition) |
| **💡 Knowledge Pulse** | `search_knowledge` call | 3-second pulse animation on used items |
| **📝 Activity Log** | Every agent action | Real-time updates with color-coded status |

---

<a id="tools-actions"></a>

## 📚 Tools & Actions

### Detailed Tool Breakdown

**📊 fetch_live_scores**
```python
# Returns structured game data
{
  "home": "Patriots", "away": "Chiefs",
  "home_score": 24, "away_score": 27,
  "status": "Final", "date": "2026-01-29"
}
```

**🔍 search_knowledge** - SQL queries with text matching and relevance scoring

**💾 save_brief** - SQLAlchemy ORM insert with metadata (requires approval)

**📈 generate_statistics** - Processes player, team, and season data

**📥 export_brief** - Generates Markdown/TXT/JSON downloads (requires approval)

---

<a id="knowledge-system"></a>

## 💡 Knowledge System

### 📚 How It Works
1. **Storage**: SQLite table `knowledge` with 6 pre-loaded items
2. **Search**: RAG-like text matching with relevance scoring
3. **Enhancement**: Knowledge added to agent's system prompt
4. **Feedback**: UI shows which knowledge items influenced response

### 🎯 Knowledge Flow
```
User Request
    ↓
Knowledge Search (relevant items retrieved)
    ↓
Context Enhancement (added to system prompt)
    ↓
LLM Processing (agent uses knowledge)
    ↓
UI Feedback (Knowledge Used card + pulse animations)
```

### 👤 Add Your Own Knowledge
- **Via UI**: Click "Add Knowledge" → upload `.txt`/`.md` OR fill form
- **Via File**: Create `.txt` or `.md` in `data/` directory
- **Automatic**: Agent learns from your additions

---

<a id="safety-control"></a>

## 🔒 Safety & Control

### ⚠️ Approval Flow for Sensitive Actions

**Actions requiring user approval:**
- ✅ `save_brief` - Writes to database
- ✅ `export_brief` - Downloads files

**How it works:**
1. Agent plans to execute sensitive action
2. Activity log marks: *"⚠️ Requires user approval"*
3. **Approval Modal** appears with action details
4. User reviews JSON payload
5. Click **Approve** ✅ or **Reject** ❌
6. Action executes only if approved
7. Confirmation message in chat

**Safety Features:**
- ✅ Delete operations are manual only (not auto)
- ✅ All database writes require approval
- ✅ Atomic database transactions
- ✅ No automatic data loss scenarios

---

<a id="examples"></a>

## 📖 Examples

### Example 1: Create & Save a Brief 📋

**User Request:** *"Create a comprehensive brief about NFL playoff games"*

| Step | Action |
|------|--------|
| 1 | Creates execution plan (4 steps) |
| 2 | Fetches live scores (Patriots vs Chiefs) |
| 3 | Searches knowledge base for NFL info |
| 4 | Generates brief content |
| 5 | Requests user approval |
| 6 | Saves to database (after approval) |

**Observable UI Changes:**
- 🏆 Scoreboard shows Patriots 24 - Chiefs 27
- 💡 Knowledge badge pulses: "NFL Teams Overview"
- 📝 Activity log shows 4 completed steps
- ⚠️ Approval modal appears
- ✅ Brief appears in sidebar

### Example 2: Generate Statistics 📊

**User Request:** *"Show me player performance statistics"*

| Step | Action |
|------|--------|
| 1 | Calls `generate_statistics` tool |
| 2 | Returns PPG, RPG, APG metrics |

**Observable UI Changes:**
- 📊 Statistics chart renders
- 📈 Bars animate from 0 to target
- 🎨 Color gradients fill (0.5s transition)
- 📋 Percentage labels display

### Example 3: Export a Brief 📥

**User Request:** *"Export brief #1 as markdown"*

| Step | Action |
|------|--------|
| 1 | Calls `export_brief` tool |
| 2 | Requests user approval |
| 3 | User clicks Approve ✅ |
| 4 | Browser downloads file |

**Observable UI Changes:**
- ⚠️ Approval modal shows export details
- 📥 File downloads to device
- ✅ Success message displays

---

<a id="contributing"></a>

## 🤝 Contributing

### 🚀 How to Extend

| Feature | Edit | Details |
|---------|------|---------|
| **New Tools** | `backend/tools.py` | Add to `ToolRegistry` |
| **UI Actions** | `frontend/src/App.tsx` | Handle in `handleClientActions` |
| **Knowledge** | UI or `backend/main.py` | Add via UI or code seed |
| **Agent Logic** | `backend/agent.py` | Modify planning/execution |

This is a demonstration project - feel free to fork and customize!

---

## 📝 License

MIT License - Use as a template for your own agentic applications!

## 🙏 Acknowledgments

Built as a demonstration of:
- ✅ Agentic AI application patterns
- ✅ OpenAI function calling
- ✅ React + FastAPI integration
- ✅ Observable UI behaviors in AI apps
- ✅ RAG knowledge integration
- ✅ User approval flows in autonomous systems

---

**Built with ❤️ for demonstrating end-to-end agentic web applications**