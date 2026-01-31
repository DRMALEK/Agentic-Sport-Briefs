# Architecture Diagrams 🏗️

## System Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                         USER BROWSER                            │
│                                                                 │
│  ┌────────────────────────────────────────────────────────┐   │
│  │              React Frontend (TypeScript)                │   │
│  │                                                          │   │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌────────┐ │   │
│  │  │  Chat    │  │  Plan    │  │ Activity │  │ Brief  │ │   │
│  │  │Interface │  │ Display  │  │   Log    │  │  List  │ │   │
│  │  └──────────┘  └──────────┘  └──────────┘  └────────┘ │   │
│  │                                                          │   │
│  │  CLIENT ACTIONS:                                        │   │
│  │  • Scoreboard Widget  🏆                                │   │
│  │  • Statistics Chart   📊                                │   │
│  │  • Knowledge Pulse    💡                                │   │
│  │  • Activity Updates   📝                                │   │
│  └─────────────────┬────────────────────────────────────────┘   │
│                    │ HTTP/JSON                                  │
└────────────────────┼────────────────────────────────────────────┘
                     │
                     │ Port 3000 → 8000
                     │
┌────────────────────▼────────────────────────────────────────────┐
│                    FastAPI Backend (Python)                     │
│                                                                 │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │                    Agent System                           │  │
│  │  ┌────────────┐  ┌──────────┐  ┌───────────────────┐   │  │
│  │  │  Planning  │→ │Execution │→ │  Activity Logger  │   │  │
│  │  └────────────┘  └──────────┘  └───────────────────┘   │  │
│  │         │                │                               │  │
│  │         │                │                               │  │
│  │         ▼                ▼                               │  │
│  │  ┌────────────────────────────────────────────────────┐ │  │
│  │  │            Tool Registry (5 Tools)                 │ │  │
│  │  ├────────────────────────────────────────────────────┤ │  │
│  │  │ 1. fetch_live_scores    → Sports Data API         │ │  │
│  │  │ 2. search_knowledge     → SQLite Query            │ │  │
│  │  │ 3. save_brief          → Database INSERT          │ │  │
│  │  │ 4. generate_statistics  → Data Processing         │ │  │
│  │  │ 5. export_brief        → File Generation          │ │  │
│  │  └────────────────────────────────────────────────────┘ │  │
│  └──────────────────────────────────────────────────────────┘  │
│                           │                                     │
│                           ▼                                     │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │                 SQLite Database                          │  │
│  │  ┌──────────┐  ┌───────────┐  ┌──────────────────┐     │  │
│  │  │  briefs  │  │ knowledge │  │ conversations    │     │  │
│  │  └──────────┘  └───────────┘  └──────────────────┘     │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                 │
│  External: OpenAI API (GPT-4 Turbo)                           │
└─────────────────────────────────────────────────────────────────┘
```

## Request Flow Diagram

```
USER TYPES MESSAGE
    │
    ├─→ "Show me latest NFL scores"
    │
    ▼
┌─────────────────┐
│ React Component │
│   (App.tsx)     │
└────────┬────────┘
         │
         │ handleSend()
         │
         ▼
┌─────────────────┐
│   API Client    │
│   (api.ts)      │
└────────┬────────┘
         │
         │ POST /api/agent/execute
         │ { goal: "...", use_knowledge: true }
         │
         ▼
┌─────────────────────────────────────┐
│      FastAPI Endpoint               │
│      /api/agent/execute             │
└───────────┬─────────────────────────┘
            │
            │ Create Agent instance
            │
            ▼
┌─────────────────────────────────────┐
│      Agent.execute_plan()           │
│                                     │
│  Step 1: Create Plan                │
│  ├─→ Call OpenAI API                │
│  └─→ Parse into steps               │
│                                     │
│  Step 2: Knowledge Context          │
│  ├─→ Query Knowledge DB             │
│  └─→ Add to system prompt           │
│                                     │
│  Step 3: Execute Tools              │
│  ├─→ Tool 1: fetch_live_scores      │
│  │    ├─→ Get sports data           │
│  │    └─→ Log activity              │
│  │                                  │
│  ├─→ Tool 2: search_knowledge       │
│  │    ├─→ SQL query                 │
│  │    ├─→ Relevance scoring         │
│  │    └─→ Log activity              │
│  │                                  │
│  └─→ Generate final response        │
│       └─→ Log completion            │
└───────────┬─────────────────────────┘
            │
            │ Return response
            │ {
            │   plan: {...},
            │   tool_calls: [...],
            │   activity_log: [...],
            │   knowledge_used: [...]
            │ }
            │
            ▼
┌─────────────────────────────────────┐
│    handleClientActions()            │
│                                     │
│  Parse tool_calls:                  │
│  ├─→ fetch_live_scores found        │
│  │    └─→ setScoreboard(game)       │
│  │                                  │
│  ├─→ generate_statistics found      │
│  │    └─→ setChartData(stats)       │
│  │                                  │
│  └─→ search_knowledge found         │
│       └─→ setHighlightedKnowledge() │
└───────────┬─────────────────────────┘
            │
            │ State updates trigger re-render
            │
            ▼
┌─────────────────────────────────────┐
│       React Re-renders              │
│                                     │
│  🏆 Scoreboard widget appears       │
│  📊 Chart bars animate              │
│  💡 Knowledge badges pulse          │
│  📝 Activity log updates            │
└─────────────────────────────────────┘
            │
            ▼
        USER SEES RESULT
```

## Tool Execution Flow

```
Agent decides to call tool
    │
    ▼
┌──────────────────────────┐
│  ToolRegistry.execute()  │
└───────────┬──────────────┘
            │
            ├─→ Tool: fetch_live_scores
            │   ├─→ Arguments: { sport: "football" }
            │   ├─→ Execute: Query mock data
            │   └─→ Return: { success: true, games: [...] }
            │
            ├─→ Tool: search_knowledge
            │   ├─→ Arguments: { query: "NFL" }
            │   ├─→ Execute: SQL SELECT with LIKE
            │   │   SELECT * FROM knowledge
            │   │   WHERE content LIKE '%NFL%'
            │   └─→ Return: { results: [...] }
            │
            ├─→ Tool: save_brief ⚠️ REQUIRES APPROVAL
            │   ├─→ Arguments: { title, content, category }
            │   ├─→ Check: requires_approval = True
            │   ├─→ Wait: User approval modal
            │   ├─→ If approved: SQL INSERT
            │   │   INSERT INTO briefs VALUES (...)
            │   └─→ Return: { brief_id: 5 }
            │
            ├─→ Tool: generate_statistics
            │   ├─→ Arguments: { data_type: "player_performance" }
            │   ├─→ Execute: Calculate stats
            │   └─→ Return: { statistics: {...} }
            │
            └─→ Tool: export_brief ⚠️ REQUIRES APPROVAL
                ├─→ Arguments: { brief_id: 1, format: "markdown" }
                ├─→ Execute: Format as markdown
                ├─→ Return: { content: "...", filename: "..." }
                └─→ Trigger: Browser download
```

## Knowledge RAG Flow

```
User asks question about sports
    │
    ▼
┌─────────────────────────────────┐
│  Agent receives goal            │
└───────────┬─────────────────────┘
            │
            │ use_knowledge = true
            │
            ▼
┌─────────────────────────────────┐
│  Query Knowledge Database       │
│                                 │
│  SELECT * FROM knowledge        │
│  LIMIT 5                        │
└───────────┬─────────────────────┘
            │
            │ Returns 5 items
            │
            ▼
┌─────────────────────────────────┐
│  Format as Context              │
│                                 │
│  **NFL Teams Overview** (teams) │
│  The NFL consists of...         │
│                                 │
│  **NBA Statistics** (stats)     │
│  Key metrics include...         │
└───────────┬─────────────────────┘
            │
            │ Add to system prompt
            │
            ▼
┌─────────────────────────────────┐
│  OpenAI API Call                │
│                                 │
│  System: "You are a sports...   │
│           KNOWLEDGE CONTEXT:    │
│           [knowledge items]"    │
│                                 │
│  User: "Tell me about NFL"      │
└───────────┬─────────────────────┘
            │
            │ LLM uses knowledge
            │
            ▼
┌─────────────────────────────────┐
│  Response Enhanced              │
│                                 │
│  "The NFL has 32 teams..."      │
│  [uses knowledge base facts]    │
└───────────┬─────────────────────┘
            │
            │ Track which items used
            │
            ▼
┌─────────────────────────────────┐
│  UI Shows Knowledge Used        │
│                                 │
│  📚 Knowledge Used:             │
│  • NFL Teams Overview (high)    │
│  • NBA Statistics (medium)      │
│                                 │
│  💡 Knowledge base enhanced...  │
└─────────────────────────────────┘
```

## Approval Flow

```
Agent wants to save/export
    │
    ▼
┌─────────────────────────────────┐
│  Tool marked requires_approval  │
└───────────┬─────────────────────┘
            │
            │ In response
            │
            ▼
┌─────────────────────────────────┐
│  Frontend detects approval flag │
│                                 │
│  if (tool.requires_approval) {  │
│    setPendingApproval(tool)     │
│    setShowApprovalModal(true)   │
│  }                              │
└───────────┬─────────────────────┘
            │
            │ Modal appears
            │
            ▼
┌─────────────────────────────────┐
│      Approval Modal             │
│                                 │
│  ⚠️ Approval Required           │
│                                 │
│  Action: save_brief             │
│  Details:                       │
│  {                              │
│    "title": "NFL Brief",        │
│    "content": "...",            │
│    "category": "football"       │
│  }                              │
│                                 │
│  [Reject]  [Approve]            │
└───────────┬─────────────────────┘
            │
            ├─→ User clicks "Approve"
            │   │
            │   ▼
            │   POST /api/agent/approve
            │   { approved: true }
            │   │
            │   ▼
            │   Execute tool
            │   └─→ INSERT INTO briefs
            │
            └─→ User clicks "Reject"
                │
                ▼
                Cancel operation
                Show rejection message
```

## Client Action Trigger Flow

```
Backend returns tool_calls
    │
    ├─→ { tool: "fetch_live_scores", result: {...} }
    ├─→ { tool: "generate_statistics", result: {...} }
    └─→ { tool: "search_knowledge", result: {...} }
    │
    ▼
┌─────────────────────────────────────────┐
│  handleClientActions(response)          │
└───────────┬─────────────────────────────┘
            │
            │ Iterate tool_calls
            │
            ├─→ Tool: "fetch_live_scores"
            │   │
            │   ▼
            │   ┌─────────────────────────┐
            │   │ CLIENT ACTION 1:        │
            │   │ Update Scoreboard       │
            │   │                         │
            │   │ const game = result     │
            │   │ setScoreboard(game)     │
            │   │                         │
            │   │ → Component renders     │
            │   │ → Gradient background   │
            │   │ → Team names & scores   │
            │   │ → Fade-in animation     │
            │   └─────────────────────────┘
            │
            ├─→ Tool: "generate_statistics"
            │   │
            │   ▼
            │   ┌─────────────────────────┐
            │   │ CLIENT ACTION 2:        │
            │   │ Render Chart            │
            │   │                         │
            │   │ const stats = result    │
            │   │ setChartData(stats)     │
            │   │                         │
            │   │ → Chart component       │
            │   │ → Bars animate width    │
            │   │ → 0% → target % (0.5s)  │
            │   │ → Gradient fills        │
            │   └─────────────────────────┘
            │
            └─→ Tool: "search_knowledge"
                │
                ▼
                ┌─────────────────────────┐
                │ CLIENT ACTION 3:        │
                │ Highlight Knowledge     │
                │                         │
                │ const ids = result.ids  │
                │ setHighlighted(ids)     │
                │                         │
                │ → Badges change color   │
                │ → Pulse animation (3x)  │
                │ → Auto-clear (3s)       │
                └─────────────────────────┘
```

## Component Tree

```
App (Root)
│
├── Header
│   ├── Title: "Sports Brief Builder 🏆"
│   └── Stats
│       ├── Briefs Count
│       ├── Knowledge Count
│       └── Sessions Count
│
├── MainContainer
│   ├── MainContent
│   │   │
│   │   ├── ChatContainer (Card)
│   │   │   ├── ChatMessages
│   │   │   │   └── Message[]
│   │   │   │       ├── UserMessage
│   │   │   │       │   └── MessageContent
│   │   │   │       │
│   │   │   │       └── AgentMessage
│   │   │   │           ├── MessageContent
│   │   │   │           ├── PlanDisplay
│   │   │   │           │   └── StepsList[]
│   │   │   │           ├── ActivityLog
│   │   │   │           │   └── ActivityItem[]
│   │   │   │           │       ├── Action
│   │   │   │           │       ├── Status (badge)
│   │   │   │           │       └── Result
│   │   │   │           └── KnowledgeUsed
│   │   │   │               └── KnowledgeBadge[]
│   │   │   │
│   │   │   └── ChatInput
│   │   │       ├── TextInput
│   │   │       └── SendButton
│   │   │
│   │   ├── Scoreboard (Card) - CLIENT ACTION 1
│   │   │   ├── Team (home)
│   │   │   ├── Separator
│   │   │   ├── Team (away)
│   │   │   └── GameStatus
│   │   │
│   │   └── StatsChart (Card) - CLIENT ACTION 2
│   │       └── ChartBar[]
│   │           ├── Label
│   │           ├── BarBackground
│   │           └── BarFill (animated)
│   │
│   └── Sidebar
│       ├── SavedBriefs (Card)
│       │   └── BriefItem[]
│       │       ├── Title
│       │       └── Meta (category, date)
│       │
│       └── KnowledgeBase (Card) - CLIENT ACTION 3
│           ├── KnowledgeBadge[] (pulse animation)
│           └── AddButton
│
└── Modals (conditional)
    ├── ApprovalModal
    │   ├── Header ("⚠️ Approval Required")
    │   ├── Content (action details)
    │   └── Actions
    │       ├── RejectButton
    │       └── ApproveButton
    │
    ├── KnowledgeModal
    │   ├── Header ("Add Knowledge")
    │   └── KnowledgeForm
    │       ├── FileUpload
    │       ├── TitleInput
    │       ├── ContentTextarea
    │       ├── CategorySelect
    │       └── SubmitButton
    │
    └── BriefModal
        ├── Header (brief title)
        ├── Content (brief details)
        └── CloseButton
```

## State Management

```
App Component State:

messages: Message[]
  ├─→ Conversation history
  └─→ Includes agent data (plan, logs, etc.)

input: string
  └─→ Current chat input

loading: boolean
  └─→ Agent execution in progress

sessionId: string
  └─→ Conversation session ID

briefs: Brief[]
  └─→ Saved briefs from database

knowledge: Knowledge[]
  └─→ Knowledge base items

stats: {total_briefs, total_knowledge, total_conversations}
  └─→ Application statistics

showApprovalModal: boolean
  └─→ Approval modal visibility

pendingApproval: ToolCall
  └─→ Tool awaiting approval

scoreboard: Game | null - CLIENT ACTION STATE
  └─→ Current game to display

chartData: Stats | null - CLIENT ACTION STATE
  └─→ Statistics to visualize

highlightedKnowledge: number[] - CLIENT ACTION STATE
  └─→ IDs of knowledge items to highlight
```

---

These diagrams show the complete flow from user input to observable UI changes, demonstrating the full-stack agentic architecture.
