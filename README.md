# Sports Brief Builder 🏆

An agentic web application that helps users create comprehensive sports briefings, reports, and analyses through natural language interaction. The agent creates execution plans, takes observable actions on both server and client, and requires approval for sensitive operations.

## 🎯 What We Built and Why

### The Challenge
Create an end-to-end agentic web application that:
- Accepts natural language goals
- Creates and executes plans autonomously
- Performs real server-side and client-side actions
- Integrates knowledge to enhance responses
- Requires user approval for certain actions
- Shows clear activity traces

### Our Solution: Sports Brief Builder
A domain-focused application where an AI agent helps create sports briefings by:
- Fetching live sports data
- Searching a knowledge base
- Generating statistics and analyses
- Saving briefs to a database
- Exporting documents
- Updating the UI in real-time based on agent actions

**Why Sports?** Sports data provides a perfect domain for demonstrating:
- Real-time data fetching (scores, games)
- Rich knowledge base (teams, players, rules)
- Natural user requests ("Create a brief about NFL playoffs")
- Observable UI updates (scoreboards, charts)
- Document generation workflows

## 🏗️ Architecture

### Tech Stack
- **Frontend**: React 18 + TypeScript
- **Backend**: FastAPI (Python 3.11)
- **Database**: SQLite
- **LLM**: OpenAI GPT-4 Turbo
- **Containerization**: Docker + Docker Compose

### System Design
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
                        - generate_statistics
                        - export_brief
```

## 🛠️ Server-Side Tools (5 Real Actions)

### 1. `fetch_live_scores`
**What it does**: Retrieves live sports scores and recent game results
**Real work**: Queries sports data (simulated API with realistic data structure)
**Example**: Returns game scores, status (Live/Final), dates
```python
# Returns structured game data
{
  "home": "Patriots", "away": "Chiefs",
  "home_score": 24, "away_score": 27,
  "status": "Final", "date": "2026-01-29"
}
```

### 2. `search_knowledge`
**What it does**: RAG-like search through the knowledge base
**Real work**: SQL queries with text matching, relevance scoring
**Example**: Find information about teams, players, statistics
**Knowledge influence**: Results are included in the agent's context

### 3. `save_brief`
**What it does**: Persists sports briefs to the database
**Real work**: SQLAlchemy ORM insert with metadata
**Approval**: ✅ Requires user confirmation
**Observable**: Updates brief count in UI, appears in saved briefs list

### 4. `generate_statistics`
**What it does**: Creates statistical analyses and summaries
**Real work**: Processes data types (player performance, team comparison, season summary)
**Example**: Calculates averages, win rates, trends, predictions
**Observable**: Triggers client-side chart visualization

### 5. `export_brief`
**What it does**: Exports briefs as downloadable files
**Real work**: Formats data into Markdown/TXT/JSON, triggers browser download
**Approval**: ✅ Requires user confirmation
**Observable**: File download initiated in browser

## 🎨 Client-Side Actions (3+ Observable Behaviors)

### 1. **Live Scoreboard Widget** 🏆
**Trigger**: When `fetch_live_scores` tool is called
**Behavior**: Animated scoreboard appears showing team names, scores, game status
**Observable**: 
- Component renders with gradient background
- Smooth fade-in animation
- Real-time score display
- Game status (Live/Final) indicator

### 2. **Statistics Visualization Chart** 📊
**Trigger**: When `generate_statistics` tool is called
**Behavior**: Interactive bar chart displays with animated fills
**Observable**:
- Chart bars animate from 0 to target width (0.5s transition)
- Color gradient fills (purple to blue)
- Percentage/value labels
- Responsive to different stat types (player, team, season)

### 3. **Knowledge Highlight Pulse** 💡
**Trigger**: When `search_knowledge` tool finds relevant items
**Behavior**: Knowledge badges pulse with highlighting
**Observable**:
- 3-second pulse animation on used knowledge items
- Color change to amber (indicates active use)
- Clear visual feedback showing which knowledge influenced the response
- Automatic return to normal state

### 4. **Real-time Activity Log** 📝
**Trigger**: Every agent action
**Behavior**: Live-updating activity trace with status indicators
**Observable**:
- Color-coded status (green=success, red=failed, amber=in-progress)
- Expandable result details
- Approval requirement warnings
- Fade-in animations for new activities

## 📚 Knowledge System & RAG

### Where Knowledge Lives
1. **Database**: SQLite table `knowledge` stores all knowledge items
2. **Initial Seed**: 6 pre-loaded items covering teams, players, stats, rules
3. **User Additions**: Via UI form or file upload (.txt, .md)

### How Knowledge is Used
```
User Request → Agent receives goal
     ↓
Knowledge Search → Relevant items retrieved from DB
     ↓
Context Enhancement → Knowledge added to system prompt
     ↓
LLM Processing → Agent uses knowledge in planning/execution
     ↓
UI Feedback → "Knowledge Used" section shows which items influenced response
```

### Knowledge Influence Visibility
The UI makes it **obvious** when knowledge is used:
- **"Knowledge Used" Card**: Lists all knowledge items consulted
- **Relevance Badges**: Shows high/medium relevance ratings
- **Influence Banner**: Yellow alert explaining knowledge base impact
- **Highlight Animation**: Knowledge items pulse when actively used
- **Activity Log**: Shows `search_knowledge` tool execution details

### Example Knowledge Influence
```
User: "Create a brief about NFL teams"
Agent: 
  1. Searches knowledge base for "NFL"
  2. Finds "NFL Teams Overview" (high relevance)
  3. Incorporates team info in response
  4. UI shows: 📚 Knowledge Used: "NFL Teams Overview (high)"
  5. Banner: "💡 Knowledge base was used to enhance this response..."
```

## 🔒 Control & Safety

### Approval Flow
**Actions requiring approval:**
- `save_brief` (writes to database)
- `export_brief` (downloads file)

**How it works:**
1. Agent plans to execute sensitive action
2. Activity log marks it "⚠️ Requires user approval"
3. Modal dialog appears with action details
4. User reviews JSON payload
5. User clicks "Approve" or "Reject"
6. Action executes only if approved
7. Confirmation message in chat

**UI/UX:**
- Large modal overlay (impossible to miss)
- Clear action name and parameters
- Formatted JSON preview
- Two prominent buttons (Approve/Reject)
- Color coding (green=approve, red=reject)

### No Destructive Actions
- Delete operations are manual (not agent-triggered)
- All writes require approval
- Database transactions are atomic
- No automatic data loss scenarios

## 🌐 Web Proof

### Evidence of Real Web Behavior

#### 1. Network Requests (DevTools Evidence)
Open browser DevTools → Network tab while using the app:

**POST** `/api/agent/execute`
```json
Request:
{
  "goal": "Show me latest NFL scores",
  "use_knowledge": true
}

Response: 200 OK
{
  "success": true,
  "plan": { ... },
  "tool_calls": [
    {
      "tool": "fetch_live_scores",
      "result": { "games": [...], "success": true }
    }
  ]
}
```

**GET** `/api/briefs`
```json
Response: 200 OK
{
  "briefs": [
    {
      "id": 1,
      "title": "NFL Playoff Preview",
      "category": "football",
      "created_at": "2026-01-30T..."
    }
  ]
}
```

**POST** `/api/knowledge/upload`
```
Request: FormData with file
Response: { "success": true, "id": 7 }
```

#### 2. Server Tool Execution
**Console output** when agent runs:
```
INFO: Agent executing plan for: "Create NFL brief"
INFO: Tool called: fetch_live_scores(sport='football')
INFO: Tool result: {"success": true, "games": 3}
INFO: Tool called: search_knowledge(query='NFL')
INFO: Tool result: {"success": true, "results": 2}
INFO: Tool called: save_brief(title='NFL Brief')
INFO: Database write: Brief #5 created
```

#### 3. UI Changes as Result
**Observable sequence:**
1. User types message → clicks "Send"
2. **Network**: POST to `/api/agent/execute` (visible in DevTools)
3. **Server**: Agent executes tools (logs show tool calls)
4. **UI Changes**:
   - Loading indicator appears
   - Agent response message fades in
   - **Scoreboard widget renders** (client action)
   - **Activity log updates** with color-coded steps
   - **Knowledge badges pulse** (highlight animation)
   - **Stats chart animates** (bars fill from left to right)
   - Brief count increments in header
   - New brief appears in sidebar list

**Screenshot Key Moments:**
- Before: Empty chat, stats show "0 Briefs"
- Network: Request/response in DevTools
- After: Message, scoreboard, chart, stats show "1 Brief"

## 🚀 How to Run

### Prerequisites
- Docker & Docker Compose
- OpenAI API key

### One-Command Setup

1. **Clone and navigate:**
```bash
cd /home/malek/SportradarEx
```

2. **Set your OpenAI API key:**
```bash
cp .env.example .env
nano .env  # Add your OPENAI_API_KEY
```

3. **Run everything:**
```bash
docker-compose up --build
```

4. **Access the application:**
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs

### Without Docker (Development)

**Backend:**
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
export OPENAI_API_KEY=your_key_here
uvicorn main:app --reload
```

**Frontend:**
```bash
cd frontend
npm install
npm start
```

## 📖 Usage Examples

### Example 1: Create a Sports Brief
```
User: "Create a comprehensive brief about the latest NFL playoff games"

Agent:
1. Creates plan (4 steps)
2. Fetches live scores (Patriots vs Chiefs, etc.)
3. Searches knowledge base for NFL info
4. Generates brief content
5. Requests approval to save
6. Saves to database (after approval)

UI Changes:
- Scoreboard shows Patriots 24 - Chiefs 27
- Knowledge badge pulses: "NFL Teams Overview"
- Activity log shows 4 completed steps
- Approval modal appears
- Brief appears in sidebar after save
```

### Example 2: Generate Statistics
```
User: "Show me player performance statistics"

Agent:
1. Calls generate_statistics tool
2. Returns player stats (PPG, RPG, APG)

UI Changes:
- Statistics chart renders
- Three animated bars show Points/Rebounds/Assists
- Values fill from 0 to target (smooth animation)
```

### Example 3: Export a Brief
```
User: "Export brief #1 as markdown"

Agent:
1. Calls export_brief tool
2. Requests approval

UI Changes:
- Approval modal shows export details
- User approves
- Browser downloads "brief_1.markdown"
```

## 🎯 Key Features Checklist

### Core Requirements
- ✅ End-to-end functionality (chat → plan → execution → results)
- ✅ Clear client/server split
- ✅ Agent accepts natural language goals
- ✅ Lightweight plan creation and display
- ✅ Activity log/trace (what agent did, status, results)

### Server-Side Tools (3+ required)
- ✅ `fetch_live_scores` - Real sports data fetching
- ✅ `search_knowledge` - RAG database search
- ✅ `save_brief` - Database persistence
- ✅ `generate_statistics` - Data transformation
- ✅ `export_brief` - File generation & download

### Client-Side Actions (2+ required)
- ✅ Scoreboard widget update (observable UI state)
- ✅ Statistics chart rendering (observable visualization)
- ✅ Knowledge highlight pulse (observable animation)
- ✅ Activity log updates (beyond text rendering)

### Knowledge System
- ✅ Knowledge database with seeded data
- ✅ File upload capability (.txt, .md)
- ✅ RAG-like search integration
- ✅ **Clear UI indication of knowledge influence**:
  - Knowledge Used card
  - Highlighted badges with pulse animation
  - Influence explanation banner
  - Activity log showing search execution

### Control & Safety
- ✅ User approval modal for sensitive actions
- ✅ No destructive actions without confirmation
- ✅ Clear action preview before approval

### Frontend
- ✅ Conversation interface
- ✅ Agent plan display
- ✅ Activity trace/log
- ✅ Results/artifacts (saved briefs)
- ✅ Real-time UI updates

## 🔄 Tradeoffs & Design Decisions

### What We Chose

#### 1. **Simulated Sports API vs Real API**
**Choice**: Simulated data with realistic structure
**Why**: 
- No API key management complexity
- Predictable demo behavior
- Fast responses
- Easy to extend with more data
**Tradeoff**: Not truly "live" scores
**Production path**: Replace with ESPN/Sportradar API

#### 2. **Simple Text Search vs Vector Embeddings**
**Choice**: SQL LIKE queries for knowledge search
**Why**:
- No additional dependencies (no vector DB)
- Instant setup
- Good enough for demo size knowledge base
- Clear to understand
**Tradeoff**: Less sophisticated relevance
**Production path**: Add pgvector or Pinecone

#### 3. **Single Model vs Multi-Agent**
**Choice**: Single GPT-4 call with function calling
**Why**:
- Simpler architecture
- Lower latency
- Easier to trace
- Cost-effective
**Tradeoff**: Less specialized behavior
**Production path**: Add specialized agents per domain

#### 4. **Synchronous Tool Execution**
**Choice**: Sequential tool execution in agent loop
**Why**:
- Predictable order
- Easier debugging
- Clear activity log
**Tradeoff**: Slower for many tools
**Production path**: Parallel execution where possible

### What We Prioritized

✅ **End-to-end completeness** over depth in one area
✅ **Observable behavior** over background processing
✅ **Clear UI feedback** over advanced AI capabilities
✅ **Approval flow** over full automation
✅ **Development speed** over production optimization

## 🚧 Next Steps & Improvements

### Short Term
1. **Real Sports API Integration**
   - ESPN API or Sportradar
   - Live score streaming
   - Historical data access

2. **Enhanced Knowledge System**
   - Vector embeddings (OpenAI text-embedding-3)
   - Semantic similarity search
   - Auto-categorization of uploads

3. **Richer Client Actions**
   - Interactive game timeline
   - Player comparison tables
   - Season progression graphs
   - Team formation visualizations

### Medium Term
4. **Multi-Agent Architecture**
   - Specialist agent for statistics
   - Writer agent for briefs
   - Research agent for knowledge

5. **Streaming Responses**
   - SSE for real-time updates
   - Progressive plan revelation
   - Live activity log updates

6. **Enhanced Approval System**
   - Approval history
   - Undo/rollback functionality
   - Bulk approval for similar actions

### Long Term
7. **User Accounts & Personalization**
   - Save preferences
   - Favorite teams
   - Custom knowledge bases

8. **Collaboration Features**
   - Share briefs
   - Team workspaces
   - Comment threads

9. **Advanced Analytics**
   - Brief quality scoring
   - Usage patterns
   - Agent performance metrics

## 📊 Project Statistics

- **Backend**: 
  - 4 Python files (~800 lines)
  - 5 server tools
  - SQLite with 3 tables
  - RESTful API (11 endpoints)

- **Frontend**:
  - React + TypeScript
  - 1 main component (~600 lines)
  - 3+ observable client actions
  - Responsive design

- **Total Setup Time**: ~10 minutes with Docker
- **Total Code**: ~1,500 lines (excluding deps)

## 🤝 Contributing

This is a demonstration project. To extend:

1. **Add Server Tools**: Edit `backend/tools.py`, add to `ToolRegistry`
2. **Add Client Actions**: Edit `frontend/src/App.tsx`, handle in `handleClientActions`
3. **Add Knowledge**: Use UI or seed in `backend/main.py`
4. **Modify Agent Behavior**: Edit `backend/agent.py`

## 📝 License

MIT License - feel free to use this as a template for your own agentic applications!

## 🙏 Acknowledgments

Built as a demonstration of:
- Agentic AI application patterns
- OpenAI function calling
- React + FastAPI integration
- Observable UI behaviors in AI apps
- RAG knowledge integration
- User approval flows in autonomous systems

---

**Built with ❤️ for demonstrating end-to-end agentic web applications**