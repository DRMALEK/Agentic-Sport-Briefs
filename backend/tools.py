from typing import Dict, List, Any, Optional
from datetime import datetime
import json
import httpx
from sqlalchemy.orm import Session
from database import Brief, Knowledge


class ToolRegistry:
    """Registry of all available server-side tools"""
    
    def __init__(self, db: Session):
        self.db = db
        self.tools = {
            "fetch_live_scores": self.fetch_live_scores,
            "search_knowledge": self.search_knowledge,
            "save_brief": self.save_brief,
            "generate_statistics": self.generate_statistics,
            "export_brief": self.export_brief,
        }
    
    def get_tool_definitions(self) -> List[Dict[str, Any]]:
        """Return OpenAI function calling format tool definitions"""
        return [
            {
                "type": "function",
                "function": {
                    "name": "fetch_live_scores",
                    "description": "Fetch live sports scores and recent game results for specified sports or teams",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "sport": {
                                "type": "string",
                                "description": "Type of sport (football, basketball, soccer, etc.)",
                            },
                            "team": {
                                "type": "string",
                                "description": "Optional: specific team name to filter results",
                            },
                        },
                        "required": ["sport"],
                    },
                }
            },
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
                    "description": "Export a brief as a downloadable file. REQUIRES USER APPROVAL.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "brief_id": {
                                "type": "integer",
                                "description": "ID of the brief to export",
                            },
                            "format": {
                                "type": "string",
                                "description": "Export format (markdown, txt, json)",
                                "enum": ["markdown", "txt", "json"],
                            },
                        },
                        "required": ["brief_id", "format"],
                    },
                }
            },
        ]
    
    async def fetch_live_scores(self, sport: str, team: Optional[str] = None) -> Dict[str, Any]:
        """Tool 1: Fetch live sports scores"""
        # Simulated API response (in production, would call real sports API like ESPN, Sportradar, etc.)
        mock_data = {
            "football": [
                {"home": "Patriots", "away": "Chiefs", "home_score": 24, "away_score": 27, "status": "Final", "date": "2026-01-29"},
                {"home": "Cowboys", "away": "49ers", "home_score": 21, "away_score": 31, "status": "Final", "date": "2026-01-29"},
                {"home": "Bills", "away": "Ravens", "home_score": 28, "away_score": 24, "status": "Live - Q4", "date": "2026-01-30"},
            ],
            "basketball": [
                {"home": "Lakers", "away": "Celtics", "home_score": 112, "away_score": 108, "status": "Final", "date": "2026-01-29"},
                {"home": "Warriors", "away": "Nets", "home_score": 98, "away_score": 105, "status": "Live - Q3", "date": "2026-01-30"},
            ],
            "soccer": [
                {"home": "Manchester United", "away": "Liverpool", "home_score": 2, "away_score": 2, "status": "Final", "date": "2026-01-29"},
                {"home": "Barcelona", "away": "Real Madrid", "home_score": 3, "away_score": 1, "status": "Final", "date": "2026-01-29"},
            ],
        }
        
        games = mock_data.get(sport.lower(), [])
        
        if team:
            games = [g for g in games if team.lower() in g["home"].lower() or team.lower() in g["away"].lower()]
        
        return {
            "success": True,
            "sport": sport,
            "team_filter": team,
            "games": games,
            "total_games": len(games),
        }
    
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
            metadata={"created_by": "agent", "version": "1.0"}
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
    
    async def export_brief(self, brief_id: int, format: str) -> Dict[str, Any]:
        """Tool 5: Export brief (requires approval)"""
        brief = self.db.query(Brief).filter(Brief.id == brief_id).first()
        
        if not brief:
            return {"success": False, "error": "Brief not found"}
        
        export_data = {
            "title": brief.title,
            "content": brief.content,
            "category": brief.category,
            "created_at": brief.created_at.isoformat(),
        }
        
        if format == "json":
            content = json.dumps(export_data, indent=2)
        elif format == "markdown":
            content = f"# {export_data['title']}\n\n**Category:** {export_data['category']}\n**Created:** {export_data['created_at']}\n\n{export_data['content']}"
        else:  # txt
            content = f"{export_data['title']}\n{'='*len(export_data['title'])}\n\nCategory: {export_data['category']}\nCreated: {export_data['created_at']}\n\n{export_data['content']}"
        
        return {
            "success": True,
            "brief_id": brief_id,
            "format": format,
            "filename": f"brief_{brief_id}.{format}",
            "content": content,
        }
    
    async def execute_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a tool by name with given arguments"""
        if tool_name not in self.tools:
            return {"success": False, "error": f"Tool '{tool_name}' not found"}
        
        try:
            result = await self.tools[tool_name](**arguments)
            return result
        except Exception as e:
            return {"success": False, "error": str(e)}
