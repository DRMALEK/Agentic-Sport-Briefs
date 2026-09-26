from typing import Dict, List, Any, Optional
from datetime import datetime
import json
import logging
import httpx
from sqlalchemy.orm import Session
from database import Brief, Knowledge
from mcp_client import ESPNMCPClient, get_espn_tools

logger = logging.getLogger(__name__)


class ToolRegistry:
    """Registry of all available server-side tools"""
    
    def __init__(self, db: Session):
        self.db = db
        self.tools = {
            "search_knowledge": self.search_knowledge,
            "save_brief": self.save_brief,
            "generate_statistics": self.generate_statistics,
            "export_brief": self.export_brief,
        }
        # Live sports data comes from the ESPN MCP server (Apify); tools are discovered at runtime
        self.mcp = ESPNMCPClient()
        self.mcp_definitions: List[Dict[str, Any]] = []
        self.mcp_error: Optional[str] = None
    
    async def load_mcp_tools(self) -> None:
        """Discover ESPN MCP tools. Failures are non-fatal: local tools keep working."""
        self.mcp_definitions = []
        self.mcp_error = None
        if not self.mcp.enabled:
            self.mcp_error = "APIFY_TOKEN is not set"
            return
        try:
            self.mcp_definitions = await get_espn_tools(self.mcp)
        except Exception as e:
            self.mcp_error = f"Could not reach ESPN MCP server: {e}"
            logger.warning(self.mcp_error)
    
    def get_tool_definitions(self) -> List[Dict[str, Any]]:
        """Return OpenAI function calling format tool definitions (local + ESPN MCP)"""
        return self.mcp_definitions + [
            {
                "type": "function",
                "function": {
                    "name": "search_knowledge",
                    "description": "Search the knowledge base for information about teams, players, statistics, or sports facts",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "query": {
                                "type": "string",
                                "description": "Search query for the knowledge base",
                            },
                            "category": {
                                "type": "string",
                                "description": "Optional: filter by category (teams, players, stats, rules)",
                            },
                        },
                        "required": ["query"],
                    },
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "save_brief",
                    "description": "Save a sports brief to the database. REQUIRES USER APPROVAL.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "title": {
                                "type": "string",
                                "description": "Title of the brief",
                            },
                            "content": {
                                "type": "string",
                                "description": "Content of the brief",
                            },
                            "category": {
                                "type": "string",
                                "description": "Category (football, basketball, soccer, general, etc.)",
                            },
                        },
                        "required": ["title", "content", "category"],
                    },
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "generate_statistics",
                    "description": "Generate statistical analysis and summaries from sports data",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "data_type": {
                                "type": "string",
                                "description": "Type of statistics (player_performance, team_comparison, season_summary, etc.)",
                            },
                            "parameters": {
                                "type": "object",
                                "description": "Additional parameters for the statistics generation",
                            },
                        },
                        "required": ["data_type"],
                    },
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "export_brief",
                    "description": "Export content as a formatted file (markdown, txt, or json). Use this to export generated briefs or content without saving to database. REQUIRES USER APPROVAL.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "title": {
                                "type": "string",
                                "description": "Title of the content to export",
                            },
                            "content": {
                                "type": "string",
                                "description": "The main content to export",
                            },
                            "category": {
                                "type": "string",
                                "description": "Category of the content (e.g., football, basketball, general)",
                            },
                            "format": {
                                "type": "string",
                                "description": "Export format: 'markdown' for .md files, 'txt' for plain text, or 'json' for JSON format",
                                "enum": ["markdown", "txt", "json"],
                            },
                        },
                        "required": ["title", "content", "format"],
                    },
                }
            },
        ]
    
    async def search_knowledge(self, query: str, category: Optional[str] = None) -> Dict[str, Any]:
        """Tool 2: Search knowledge base with RAG-like functionality"""
        # Search the knowledge database
        knowledge_query = self.db.query(Knowledge)
        
        if category:
            knowledge_query = knowledge_query.filter(Knowledge.category == category)
        
        # Simple text search (in production, would use embeddings/vector search)
        results = knowledge_query.filter(
            (Knowledge.content.contains(query)) | (Knowledge.title.contains(query))
        ).limit(5).all()
        
        knowledge_items = [
            {
                "id": k.id,
                "title": k.title,
                "content": k.content,
                "category": k.category,
                "relevance": "high" if query.lower() in k.title.lower() else "medium",
            }
            for k in results
        ]
        
        return {
            "success": True,
            "query": query,
            "category_filter": category,
            "results": knowledge_items,
            "total_found": len(knowledge_items),
        }
    
    async def save_brief(self, title: str, content: str, category: str) -> Dict[str, Any]:
        """Tool 3: Save brief to database (requires approval)"""
        brief = Brief(
            title=title,
            content=content,
            category=category,
            extra_data={"created_by": "agent", "version": "1.0"}
        )
        self.db.add(brief)
        self.db.commit()
        self.db.refresh(brief)
        
        return {
            "success": True,
            "brief_id": brief.id,
            "title": title,
            "category": category,
            "message": "Brief saved successfully",
        }
    
    async def generate_statistics(self, data_type: str, parameters: Optional[Dict] = None) -> Dict[str, Any]:
        """Tool 4: Generate statistical analysis"""
        # Ensure parameters is a dict, not None
        if parameters is None:
            parameters = {}
        
        # Mock statistics generation
        stats = {}
        
        if data_type == "player_performance":
            stats = {
                "player": parameters.get("player", "Sample Player"),
                "games_played": 15,
                "average_points": 24.5,
                "average_rebounds": 8.2,
                "average_assists": 6.1,
                "field_goal_percentage": 47.3,
                "trend": "improving",
            }
        elif data_type == "team_comparison":
            stats = {
                "teams": parameters.get("teams", ["Team A", "Team B"]),
                "metrics": {
                    "win_rate": [0.73, 0.65],
                    "points_per_game": [108.5, 102.3],
                    "defense_rating": [98.2, 104.7],
                },
                "prediction": "Team A has 62% chance to win based on current stats",
            }
        elif data_type == "season_summary":
            stats = {
                "total_games": 50,
                "wins": 32,
                "losses": 18,
                "win_percentage": 0.64,
                "top_scorers": [
                    {"name": "Player A", "ppg": 28.5},
                    {"name": "Player B", "ppg": 24.2},
                    {"name": "Player C", "ppg": 21.8},
                ],
                "trends": "Strong performance in last 10 games (8-2)",
            }
        else:
            stats = {"message": "Statistics type not recognized", "available_types": ["player_performance", "team_comparison", "season_summary"]}
        
        return {
            "success": True,
            "data_type": data_type,
            "statistics": stats,
        }
    
    async def export_brief(self, title: str, content: str, format: str, category: str = "general") -> Dict[str, Any]:
        """Tool 5: Export content in various formats (requires approval)"""
        
        export_data = {
            "title": title,
            "content": content,
            "category": category,
            "created_at": datetime.utcnow().isoformat(),
        }
        
        # Format the content based on requested format
        if format == "json":
            formatted_content = json.dumps(export_data, indent=2)
            file_ext = "json"
        elif format == "markdown":
            formatted_content = f"""# {export_data['title']}

**Category:** {export_data['category']}  
**Created:** {export_data['created_at']}

---

{export_data['content']}
"""
            file_ext = "md"
        elif format == "txt":
            title_underline = '=' * len(export_data['title'])
            formatted_content = f"""{export_data['title']}
{title_underline}

Category: {export_data['category']}
Created: {export_data['created_at']}

{export_data['content']}
"""
            file_ext = "txt"
        else:
            return {
                "success": False,
                "error": f"Unsupported format '{format}'. Please use 'markdown', 'txt', or 'json'."
            }
        
        # Generate a safe filename from the title
        safe_title = title.lower().replace(' ', '_').replace('/', '_')[:50]
        
        return {
            "success": True,
            "title": title,
            "format": format,
            "filename": f"{safe_title}.{file_ext}",
            "content": formatted_content,
            "message": f"Content '{title}' exported successfully as {format}",
        }
    
    async def execute_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a tool by name with given arguments"""
        mcp_names = {d["function"]["name"] for d in self.mcp_definitions}
        if tool_name in mcp_names:
            try:
                return await self.mcp.call_tool(tool_name, arguments)
            except Exception as e:
                return {"success": False, "source": "espn-mcp", "error": str(e)}
        
        if tool_name not in self.tools:
            return {"success": False, "error": f"Tool '{tool_name}' not found"}
        
        try:
            result = await self.tools[tool_name](**arguments)
            return result
        except Exception as e:
            return {"success": False, "error": str(e)}
