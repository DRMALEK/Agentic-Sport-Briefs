# API Documentation 📡

Complete API reference for the Sports Brief Builder backend.

## Base URL

```
http://localhost:8000
```

## Authentication

Currently no authentication required (demo application).

## Endpoints

### Health & Info

#### GET `/`
Get API information and health status.

**Response:**
```json
{
  "message": "Sports Brief Builder API",
  "version": "1.0.0",
  "status": "running"
}
```

---

### Agent Operations

#### POST `/api/agent/execute`
Execute the agent with a user goal.

**Request Body:**
```json
{
  "goal": "Create a brief about NFL playoffs",
  "session_id": "optional-uuid",
  "use_knowledge": true
}
```

**Parameters:**
- `goal` (string, required): Natural language goal for the agent
- `session_id` (string, optional): Session ID for conversation continuity
- `use_knowledge` (boolean, optional, default: true): Whether to use knowledge base

**Response:**
```json
{
  "success": true,
  "plan": {
    "plan": "1. Fetch scores\n2. Search knowledge\n3. Generate brief",
    "steps": ["Fetch scores", "Search knowledge", "Generate brief"],
    "total_steps": 3
  },
  "response": "Here is your sports brief...",
  "tool_calls": [
    {
      "tool": "fetch_live_scores",
      "arguments": {"sport": "football"},
      "result": {"success": true, "games": [...]},
      "requires_approval": false
    }
  ],
  "activity_log": [
    {
      "step": "planning",
      "action": "Creating execution plan",
      "status": "completed",
      "result": "Plan created"
    }
  ],
  "knowledge_used": [
    {
      "source": "NFL Teams Overview",
      "category": "teams",
      "relevance": "high"
    }
  ],
  "session_id": "550e8400-e29b-41d4-a716-446655440000"
}
```

**Status Codes:**
- 200: Success
- 500: Server error (e.g., OpenAI API key not configured)

---

#### POST `/api/agent/approve`
Approve or reject an action requiring user approval.

**Request Body:**
```json
{
  "session_id": "550e8400-e29b-41d4-a716-446655440000",
  "tool_call_index": 0,
  "approved": true
}
```

**Response:**
```json
{
  "success": true,
  "approved": true,
  "message": "Action approved"
}
```

---

### Briefs Management

#### POST `/api/briefs`
Create a new brief.

**Request Body:**
```json
{
  "title": "NFL Playoff Preview",
  "content": "The NFL playoffs are heating up with the top teams competing...",
  "category": "football"
}
```

**Parameters:**
- `title` (string, required): Brief title
- `content` (string, required): Brief content
- `category` (string, required): Category (e.g., football, basketball, soccer)

**Response:**
```json
{
  "success": true,
  "id": 1,
  "title": "NFL Playoff Preview",
  "created_at": "2026-01-30T10:30:00",
  "message": "Brief created successfully"
}
```

**Status Codes:**
- 200: Success
- 422: Validation error

---

#### GET `/api/briefs`
Get all saved briefs.

**Response:**
```json
{
  "briefs": [
    {
      "id": 1,
      "title": "NFL Playoff Preview",
      "content": "The NFL playoffs are heating up...",
      "category": "football",
      "created_at": "2026-01-30T10:30:00"
    }
  ]
}
```

---

#### GET `/api/briefs/{brief_id}`
Get a specific brief by ID.

**Path Parameters:**
- `brief_id` (integer): Brief ID

**Response:**
```json
{
  "id": 1,
  "title": "NFL Playoff Preview",
  "content": "The NFL playoffs are heating up...",
  "category": "football",
  "created_at": "2026-01-30T10:30:00"
}
```

**Status Codes:**
- 200: Success
- 404: Brief not found

---

#### DELETE `/api/briefs/{brief_id}`
Delete a brief.

**Path Parameters:**
- `brief_id` (integer): Brief ID

**Response:**
```json
{
  "success": true,
  "message": "Brief deleted"
}
```

**Status Codes:**
- 200: Success
- 404: Brief not found

---

### Knowledge Management

#### GET `/api/knowledge`
Get knowledge items, optionally filtered by category.

**Query Parameters:**
- `category` (string, optional): Filter by category (teams, players, stats, rules, etc.)

**Response:**
```json
{
  "knowledge": [
    {
      "id": 1,
      "title": "NFL Teams Overview",
      "content": "The NFL consists of 32 teams...",
      "category": "teams",
      "created_at": "2026-01-30T09:00:00"
    }
  ]
}
```

---

#### POST `/api/knowledge`
Add a new knowledge item.

**Request Body:**
```json
{
  "title": "NBA Statistics Guide",
  "content": "Key basketball stats include PPG, RPG, APG...",
  "category": "stats"
}
```

**Response:**
```json
{
  "success": true,
  "id": 7,
  "message": "Knowledge added successfully"
}
```

---

#### POST `/api/knowledge/upload`
Upload a knowledge file (.txt or .md).

**Request:**
- Content-Type: `multipart/form-data`
- Field name: `file`
- Accepted formats: `.txt`, `.md`

**Response:**
```json
{
  "success": true,
  "id": 8,
  "filename": "team_info.txt",
  "message": "Knowledge file uploaded successfully"
}
```

**Status Codes:**
- 200: Success
- 400: Invalid file format

---

### Statistics

#### GET `/api/stats`
Get application statistics.

**Response:**
```json
{
  "total_briefs": 5,
  "total_knowledge": 8,
  "total_conversations": 12
}
```

---

### Client Actions

#### POST `/api/client-action`
Handle client-side action triggers (future use).

**Request Body:**
```json
{
  "action_type": "update_scoreboard",
  "parameters": {
    "game_id": 123
  }
}
```

**Response:**
```json
{
  "success": true,
  "action": "update_scoreboard",
  "parameters": {"game_id": 123}
}
```

---

## Server-Side Tools

These tools are called internally by the agent:

### fetch_live_scores
Fetch live sports scores and recent game results.

**Arguments:**
```json
{
  "sport": "football",
  "team": "Patriots"  // optional
}
```

**Returns:**
```json
{
  "success": true,
  "sport": "football",
  "team_filter": "Patriots",
  "games": [
    {
      "home": "Patriots",
      "away": "Chiefs",
      "home_score": 24,
      "away_score": 27,
      "status": "Final",
      "date": "2026-01-29"
    }
  ],
  "total_games": 1
}
```

---

### search_knowledge
Search the knowledge base.

**Arguments:**
```json
{
  "query": "NFL teams",
  "category": "teams"  // optional
}
```

**Returns:**
```json
{
  "success": true,
  "query": "NFL teams",
  "category_filter": "teams",
  "results": [
    {
      "id": 1,
      "title": "NFL Teams Overview",
      "content": "The NFL consists of...",
      "category": "teams",
      "relevance": "high"
    }
  ],
  "total_found": 1
}
```

---

### save_brief
Save a brief to the database. **Requires approval**.

**Arguments:**
```json
{
  "title": "NFL Weekly Recap",
  "content": "This week in the NFL...",
  "category": "football"
}
```

**Returns:**
```json
{
  "success": true,
  "brief_id": 6,
  "title": "NFL Weekly Recap",
  "category": "football",
  "message": "Brief saved successfully"
}
```

---

### generate_statistics
Generate statistical analysis.

**Arguments:**
```json
{
  "data_type": "player_performance",
  "parameters": {
    "player": "LeBron James"
  }
}
```

**Data Types:**
- `player_performance`: Individual player stats
- `team_comparison`: Compare two teams
- `season_summary`: Season overview

**Returns:**
```json
{
  "success": true,
  "data_type": "player_performance",
  "statistics": {
    "player": "Sample Player",
    "games_played": 15,
    "average_points": 24.5,
    "average_rebounds": 8.2,
    "average_assists": 6.1,
    "field_goal_percentage": 47.3,
    "trend": "improving"
  }
}
```

---

### export_brief
Export a brief as a downloadable file. **Requires approval**.

**Arguments:**
```json
{
  "brief_id": 1,
  "format": "markdown"
}
```

**Formats:**
- `markdown`: .md file
- `txt`: Plain text
- `json`: JSON format

**Returns:**
```json
{
  "success": true,
  "brief_id": 1,
  "format": "markdown",
  "filename": "brief_1.markdown",
  "content": "# NFL Playoff Preview\n\n**Category:** football..."
}
```

---

## Error Responses

All endpoints may return error responses in this format:

```json
{
  "detail": "Error message here"
}
```

**Common Status Codes:**
- 400: Bad Request (invalid parameters)
- 404: Not Found (resource doesn't exist)
- 500: Internal Server Error

---

## Database Schema

### Briefs Table
```sql
CREATE TABLE briefs (
    id INTEGER PRIMARY KEY,
    title VARCHAR,
    content TEXT,
    category VARCHAR,
    created_at DATETIME,
    metadata JSON
);
```

### Knowledge Table
```sql
CREATE TABLE knowledge (
    id INTEGER PRIMARY KEY,
    title VARCHAR,
    content TEXT,
    category VARCHAR,
    created_at DATETIME
);
```

### Conversations Table
```sql
CREATE TABLE conversations (
    id INTEGER PRIMARY KEY,
    session_id VARCHAR,
    messages JSON,
    created_at DATETIME,
    updated_at DATETIME
);
```

---

## Rate Limits

No rate limits currently (demo application).

## CORS

CORS is enabled for all origins in development mode.

---

## Interactive API Docs

Visit http://localhost:8000/docs for interactive Swagger documentation.
