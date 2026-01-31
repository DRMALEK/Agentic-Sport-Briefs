# Project Structure 📁

```
SportradarEx/
├── README.md                      # Main documentation
├── QUICKSTART.md                  # Quick start guide
├── WEB_PROOF.md                   # Web behavior proof documentation
├── API.md                         # API reference
├── .gitignore                     # Git ignore rules
├── .env                          # Environment variables (add your API key here!)
├── .env.example                  # Environment template
├── docker-compose.yml            # Docker orchestration
├── start.sh                      # Easy start script
├── test.sh                       # Test script
│
├── backend/                      # FastAPI Backend
│   ├── Dockerfile               # Backend container config
│   ├── requirements.txt         # Python dependencies
│   ├── main.py                  # FastAPI application entry point
│   ├── agent.py                 # Agent logic and planning
│   ├── tools.py                 # Server-side tools (5 tools)
│   └── database.py              # SQLAlchemy models and DB setup
│
├── frontend/                     # React Frontend
│   ├── Dockerfile               # Frontend container config
│   ├── package.json             # Node dependencies
│   ├── tsconfig.json            # TypeScript configuration
│   │
│   ├── public/
│   │   └── index.html           # HTML template
│   │
│   └── src/
│       ├── index.tsx            # React entry point
│       ├── index.css            # Global styles
│       ├── App.tsx              # Main application component
│       ├── App.css              # Application styles
│       └── api.ts               # API client functions
│
└── data/                         # Data directory (created on first run)
    ├── sports_brief.db          # SQLite database (auto-created)
    └── sample_knowledge.md      # Sample knowledge file
```

## Key Files Description

### Root Level

**README.md** - Complete project documentation including:
- What was built and why
- Architecture overview
- Server tools (5) and client actions (3+)
- Knowledge system explanation
- How to run
- Tradeoffs and next steps

**QUICKSTART.md** - Step-by-step guide to get started quickly

**WEB_PROOF.md** - Detailed evidence of web behavior:
- Network requests (DevTools)
- Server execution (logs)
- UI changes (observable)

**API.md** - Complete API reference for all endpoints

**docker-compose.yml** - Orchestrates:
- Backend service (FastAPI on port 8000)
- Frontend service (React on port 3000)
- Shared network
- Volume mounts

**start.sh** - One-command startup script with validation

**test.sh** - Automated testing script

### Backend (`/backend`)

**main.py** (300+ lines)
- FastAPI app initialization
- 11 API endpoints
- Database seeding
- CORS configuration
- Request/response handling

**agent.py** (150+ lines)
- Agent class with planning logic
- OpenAI integration
- Tool execution orchestration
- Activity logging
- Knowledge context integration

**tools.py** (200+ lines)
- ToolRegistry class
- 5 server-side tools:
  1. `fetch_live_scores` - Get sports data
  2. `search_knowledge` - RAG search
  3. `save_brief` - Database persistence
  4. `generate_statistics` - Data analysis
  5. `export_brief` - File export
- OpenAI function calling format

**database.py** (80+ lines)
- SQLAlchemy setup
- 3 database models:
  - Brief (sports briefs)
  - Knowledge (knowledge base)
  - Conversation (chat history)
- Database initialization
- Session management

### Frontend (`/frontend`)

**App.tsx** (600+ lines)
- Main React component
- Chat interface
- Agent plan display
- Activity log rendering
- 3+ client-side actions:
  1. Scoreboard widget update
  2. Statistics chart rendering
  3. Knowledge highlight animation
  4. Real-time activity updates
- Approval modal
- Knowledge management
- Brief viewing

**App.css** (500+ lines)
- Complete styling
- Animations (fadeIn, pulse, slideUp)
- Responsive design
- Color scheme
- Card components
- Modal styling

**api.ts** (150+ lines)
- Axios HTTP client
- TypeScript interfaces
- API functions for:
  - Agent execution
  - Briefs management
  - Knowledge operations
  - Statistics

### Data (`/data`)

Created automatically on first run:
- SQLite database file
- Sample knowledge files

## Component Hierarchy

```
App
├── Header
│   └── Stats (Briefs, Knowledge, Sessions)
│
├── MainContainer
│   ├── MainContent
│   │   ├── ChatContainer
│   │   │   ├── Messages[]
│   │   │   │   ├── UserMessage
│   │   │   │   └── AgentMessage
│   │   │   │       ├── PlanDisplay
│   │   │   │       ├── ActivityLog
│   │   │   │       └── KnowledgeUsed
│   │   │   └── ChatInput
│   │   │
│   │   ├── Scoreboard (CLIENT ACTION 1)
│   │   └── StatsChart (CLIENT ACTION 2)
│   │
│   └── Sidebar
│       ├── SavedBriefs
│       └── KnowledgeBase (CLIENT ACTION 3)
│
└── Modals
    ├── ApprovalModal
    ├── KnowledgeModal
    └── BriefModal
```

## Data Flow

```
User Input
    ↓
ChatInput component
    ↓
handleSend() function
    ↓
agentAPI.executeAgent() [api.ts]
    ↓
HTTP POST /api/agent/execute
    ↓
FastAPI endpoint [main.py]
    ↓
Agent.execute_plan() [agent.py]
    ↓
ToolRegistry.execute_tool() [tools.py]
    ↓
Database query [database.py]
    ↓
Response back through stack
    ↓
handleClientActions() [App.tsx]
    ↓
UI updates (scoreboard, chart, highlights)
    ↓
User sees result
```

## Technology Stack by Layer

### Frontend Layer
- **Framework**: React 18
- **Language**: TypeScript 5.3
- **HTTP Client**: Axios 1.6
- **Styling**: CSS3 (custom)
- **Build**: React Scripts 5.0

### Backend Layer
- **Framework**: FastAPI 0.109
- **Language**: Python 3.11
- **ORM**: SQLAlchemy 2.0
- **Server**: Uvicorn 0.27
- **AI**: OpenAI 1.10

### Data Layer
- **Database**: SQLite 3
- **Storage**: File system (exports)

### Infrastructure Layer
- **Containers**: Docker
- **Orchestration**: Docker Compose
- **Networking**: Bridge network

## Line Count Summary

```
Backend:
  main.py:      ~350 lines
  agent.py:     ~180 lines
  tools.py:     ~250 lines
  database.py:  ~85 lines
  Total:        ~865 lines

Frontend:
  App.tsx:      ~650 lines
  App.css:      ~530 lines
  api.ts:       ~150 lines
  index.tsx:    ~15 lines
  Total:        ~1,345 lines

Documentation:
  README.md:    ~600 lines
  WEB_PROOF.md: ~580 lines
  API.md:       ~420 lines
  QUICKSTART.md:~150 lines
  Total:        ~1,750 lines

Grand Total:  ~3,960 lines (excluding dependencies)
```

## Docker Services

### Backend Container
- **Base Image**: python:3.11-slim
- **Exposed Port**: 8000
- **Volume Mounts**:
  - `./backend:/app` (code)
  - `./data:/app/data` (database)
- **Environment**:
  - OPENAI_API_KEY
  - DATABASE_URL
- **Command**: `uvicorn main:app --reload`

### Frontend Container
- **Base Image**: node:18-alpine
- **Exposed Port**: 3000
- **Volume Mounts**:
  - `./frontend:/app` (code)
  - `/app/node_modules` (dependencies)
- **Environment**:
  - REACT_APP_API_URL
- **Command**: `npm start`

## API Endpoints Summary

| Method | Endpoint | Purpose |
|--------|----------|---------|
| GET | `/` | Health check |
| POST | `/api/agent/execute` | Execute agent |
| POST | `/api/agent/approve` | Approve action |
| GET | `/api/briefs` | List briefs |
| GET | `/api/briefs/{id}` | Get brief |
| DELETE | `/api/briefs/{id}` | Delete brief |
| GET | `/api/knowledge` | List knowledge |
| POST | `/api/knowledge` | Add knowledge |
| POST | `/api/knowledge/upload` | Upload file |
| POST | `/api/client-action` | Client actions |
| GET | `/api/stats` | Get statistics |

## Database Schema

### Tables: 3

1. **briefs**
   - id (PRIMARY KEY)
   - title
   - content
   - category
   - created_at
   - metadata (JSON)

2. **knowledge**
   - id (PRIMARY KEY)
   - title
   - content
   - category
   - created_at

3. **conversations**
   - id (PRIMARY KEY)
   - session_id
   - messages (JSON)
   - created_at
   - updated_at

## Features Checklist

### Core Agent Features
- ✅ Natural language goal processing
- ✅ Lightweight plan creation
- ✅ Step-by-step execution
- ✅ Activity log/trace
- ✅ Error handling

### Server-Side Tools (5/5)
- ✅ fetch_live_scores (sports data)
- ✅ search_knowledge (RAG)
- ✅ save_brief (database)
- ✅ generate_statistics (analysis)
- ✅ export_brief (file)

### Client-Side Actions (4/2 required)
- ✅ Scoreboard update
- ✅ Chart rendering
- ✅ Knowledge highlighting
- ✅ Activity log updates

### Knowledge System
- ✅ Database storage
- ✅ File upload (.txt, .md)
- ✅ Search capability
- ✅ RAG-like integration
- ✅ UI influence display

### Control & Safety
- ✅ Approval modal
- ✅ Action preview
- ✅ Confirmation required
- ✅ Clear messaging

### Frontend Features
- ✅ Chat interface
- ✅ Plan display
- ✅ Activity trace
- ✅ Results view
- ✅ Real-time updates
- ✅ Responsive design

### Documentation
- ✅ Comprehensive README
- ✅ Quick start guide
- ✅ Web proof documentation
- ✅ API reference
- ✅ Code comments

## Setup Time

- **With Docker**: ~10 minutes
  - 2 min: Download and setup
  - 5 min: Docker build
  - 3 min: First run and validation

- **Without Docker**: ~15 minutes
  - 5 min: Install dependencies
  - 5 min: Configure environment
  - 5 min: Start services separately

## Development Workflow

1. **Edit Backend**:
   - Modify files in `backend/`
   - Auto-reload enabled (--reload flag)
   - See changes immediately

2. **Edit Frontend**:
   - Modify files in `frontend/src/`
   - Hot reload enabled (React Scripts)
   - See changes in browser

3. **View Logs**:
   ```bash
   docker-compose logs -f backend
   docker-compose logs -f frontend
   ```

4. **Rebuild**:
   ```bash
   docker-compose up --build
   ```

5. **Stop**:
   ```bash
   docker-compose down
   ```

## Extension Points

To extend the application:

1. **Add Server Tool**:
   - Edit `backend/tools.py`
   - Add method to ToolRegistry
   - Add to get_tool_definitions()

2. **Add Client Action**:
   - Edit `frontend/src/App.tsx`
   - Add state variable
   - Handle in handleClientActions()
   - Render in component

3. **Add Knowledge**:
   - Use UI upload feature
   - Or add to database seed
   - Or place file in data/

4. **Modify Agent Behavior**:
   - Edit `backend/agent.py`
   - Adjust system prompt
   - Change planning logic

5. **Style Changes**:
   - Edit `frontend/src/App.css`
   - Modify colors, animations
   - Adjust responsive breakpoints
