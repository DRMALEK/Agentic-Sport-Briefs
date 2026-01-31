# Quick Start Guide

## First Time Setup

1. **Get your OpenAI API key:**
   - Go to https://platform.openai.com/api-keys
   - Create a new secret key
   - Copy the key

2. **Configure the environment:**
   ```bash
   cd /home/malek/SportradarEx
   cp .env.example .env
   nano .env
   ```
   
   Replace `your_openai_api_key_here` with your actual key

3. **Start the application:**
   ```bash
   docker-compose up --build
   ```

4. **Wait for services to start:**
   - Backend will be ready when you see: "Application startup complete"
   - Frontend will be ready when you see: "webpack compiled successfully"

5. **Open your browser:**
   - Navigate to http://localhost:3000

## Example Prompts to Try

### Create Sports Briefs
- "Create a brief about the latest NFL games"
- "Write a basketball season summary"
- "Generate a soccer match preview for Premier League"

### Get Live Data
- "Show me latest football scores"
- "What are the current basketball games?"
- "Get soccer match results"

### Generate Statistics
- "Generate player performance statistics"
- "Show me team comparison stats"
- "Create a season summary with statistics"

### Use Knowledge Base
- "Tell me about NBA teams using the knowledge base"
- "Explain football scoring rules"
- "What are the key basketball statistics?"

### Complete Workflows
- "Create a comprehensive NFL playoff brief and save it"
- "Generate player stats, create a brief, and export as markdown"
- "Find latest scores, search for team info, and write a summary"

## Verify Web Proof

### Check Network Requests
1. Open browser DevTools (F12)
2. Go to Network tab
3. Send a message in the chat
4. Watch for:
   - POST to `/api/agent/execute`
   - Response with tool_calls array
   - Subsequent GET requests for briefs/knowledge

### Observe Server Execution
1. Look at terminal where docker-compose is running
2. You'll see logs like:
   ```
   backend_1   | INFO: Tool called: fetch_live_scores
   backend_1   | INFO: Tool result: {"success": true, ...}
   ```

### Watch UI Changes
1. Type: "Show me latest NFL scores"
2. Observe:
   - Scoreboard widget appears (CLIENT ACTION)
   - Activity log updates with color coding
   - Knowledge badges may pulse if knowledge used
3. Type: "Generate player statistics"
4. Observe:
   - Chart appears with animated bars (CLIENT ACTION)

## Troubleshooting

### Port Already in Use
```bash
# Stop existing services
docker-compose down

# Or change ports in docker-compose.yml
```

### OpenAI API Error
- Check your API key in .env file
- Ensure you have credits in your OpenAI account
- Verify internet connection

### Frontend Won't Load
```bash
# Rebuild frontend
docker-compose up --build frontend
```

### Database Issues
```bash
# Reset database
rm -rf data/*.db
docker-compose restart backend
```

## Adding Your Own Knowledge

### Via UI
1. Click "Add Knowledge" button in Knowledge Base card
2. Either:
   - Upload a .txt or .md file, OR
   - Fill the form manually
3. Click "Add Knowledge"

### Via File
1. Create a .txt or .md file in `data/` directory
2. Use the upload feature in the UI
3. Agent will now have access to this knowledge

## Testing Approval Flow

1. Type: "Create a brief about NFL and save it to database"
2. Agent will execute and prepare to save
3. **Approval modal will appear**
4. Review the action details
5. Click "Approve" to execute or "Reject" to cancel
6. Check saved briefs sidebar to see result

## Next Steps

- Explore the saved briefs
- Add your own knowledge
- Try combining multiple tools in one request
- Export briefs in different formats
- Watch the activity logs to understand agent behavior
