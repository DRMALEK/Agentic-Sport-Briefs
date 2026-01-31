from fastapi import FastAPI, Depends, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import os
import json
from datetime import datetime
import uuid

from database import get_db, init_db, Brief, Knowledge, Conversation
from agent import Agent
from tools import ToolRegistry

app = FastAPI(title="Sports Brief Builder API")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize database on startup
@app.on_event("startup")
async def startup_event():
    init_db()
    # Seed some initial knowledge
    db = next(get_db())
    if db.query(Knowledge).count() == 0:
        seed_knowledge(db)
    db.close()


def seed_knowledge(db: Session):
    """Seed initial sports knowledge"""
    knowledge_items = [
        {
            "title": "NFL Teams Overview",
            "content": "The NFL consists of 32 teams divided into two conferences: AFC and NFC. Popular teams include the Kansas City Chiefs (known for QB Patrick Mahomes), New England Patriots (historical dynasty), Dallas Cowboys (America's Team), and San Francisco 49ers.",
            "category": "teams"
        },
        {
            "title": "NBA Current Season Leaders",
            "content": "Top performers this season: Lakers remain strong with veteran leadership, Celtics showing championship potential, Warriors continuing their dynasty run, and emerging teams like the Nuggets showing promise.",
            "category": "teams"
        },
        {
            "title": "Soccer Major Leagues",
            "content": "Premier League (England), La Liga (Spain), Serie A (Italy), Bundesliga (Germany), and Ligue 1 (France) are the top 5 European leagues. Top teams include Manchester United, Liverpool, Barcelona, Real Madrid, Bayern Munich, and PSG.",
            "category": "teams"
        },
        {
            "title": "Basketball Statistics Explanation",
            "content": "Key basketball stats: PPG (Points Per Game), RPG (Rebounds Per Game), APG (Assists Per Game), FG% (Field Goal Percentage), 3P% (Three-Point Percentage), and PER (Player Efficiency Rating).",
            "category": "stats"
        },
        {
            "title": "Football Scoring Rules",
            "content": "NFL scoring: Touchdown = 6 points (+ 1 or 2 point conversion), Field Goal = 3 points, Safety = 2 points. A game consists of 4 quarters, 15 minutes each.",
            "category": "rules"
        },
        {
            "title": "Star Players 2026",
            "content": "Notable athletes: Patrick Mahomes (Chiefs QB), LeBron James (Lakers), Lionel Messi (Inter Miami), Nikola Jokic (Nuggets), and emerging talents across all sports.",
            "category": "players"
        },
    ]
    
    for item in knowledge_items:
        knowledge = Knowledge(**item)
        db.add(knowledge)
    
    db.commit()


# Pydantic models
class AgentRequest(BaseModel):
    goal: str
    session_id: Optional[str] = None
    use_knowledge: bool = True


class ApprovalRequest(BaseModel):
    session_id: str
    tool_call_index: int
    approved: bool


class BriefCreate(BaseModel):
    title: str
    content: str
    category: str


class KnowledgeCreate(BaseModel):
    title: str
    content: str
    category: str


class ClientAction(BaseModel):
    action_type: str
    parameters: Dict[str, Any]


# API Endpoints

@app.get("/")
async def root():
    return {
        "message": "Sports Brief Builder API",
        "version": "1.0.0",
        "status": "running"
    }


@app.post("/api/agent/execute")
async def execute_agent(request: AgentRequest, db: Session = Depends(get_db)):
    """Execute agent with user goal"""
    
    openai_api_key = os.getenv("OPENAI_API_KEY")
    if not openai_api_key:
        raise HTTPException(status_code=500, detail="OpenAI API key not configured")
    
    # Get or create session
    session_id = request.session_id or str(uuid.uuid4())
    
    # Get conversation history
    conversation = db.query(Conversation).filter(
        Conversation.session_id == session_id
    ).first()
    
    session_history = []
    if conversation:
        session_history = conversation.messages or []
    
    # Prepare knowledge context if requested
    knowledge_context = None
    if request.use_knowledge:
        # Simple knowledge retrieval (in production, use embeddings)
        knowledge_items = db.query(Knowledge).limit(5).all()
        if knowledge_items:
            knowledge_context = "\n\n".join([
                f"**{k.title}** ({k.category}):\n{k.content}"
                for k in knowledge_items
            ])
    
    # Execute agent
    agent = Agent(db, openai_api_key)
    result = await agent.execute_plan(
        user_goal=request.goal,
        knowledge_context=knowledge_context,
        session_history=session_history
    )
    
    # Update conversation history
    session_history.append({"role": "user", "content": request.goal})
    session_history.append({"role": "assistant", "content": result["response"]})
    
    if conversation:
        conversation.messages = session_history
        conversation.updated_at = datetime.utcnow()
    else:
        conversation = Conversation(
            session_id=session_id,
            messages=session_history
        )
        db.add(conversation)
    
    db.commit()
    
    # Add session_id to response
    result["session_id"] = session_id
    
    return result


@app.post("/api/agent/approve")
async def approve_action(request: ApprovalRequest, db: Session = Depends(get_db)):
    """Approve or reject an action that requires approval"""
    
    # In a production app, we'd store pending actions and execute upon approval
    # For this demo, we'll execute the action immediately if approved
    
    return {
        "success": True,
        "approved": request.approved,
        "message": "Action approved" if request.approved else "Action rejected"
    }


@app.post("/api/briefs")
async def create_brief(brief: BriefCreate, db: Session = Depends(get_db)):
    """Create a new brief"""
    new_brief = Brief(
        title=brief.title,
        content=brief.content,
        category=brief.category
    )
    db.add(new_brief)
    db.commit()
    db.refresh(new_brief)
    
    return {
        "success": True,
        "id": new_brief.id,
        "title": new_brief.title,
        "created_at": new_brief.created_at.isoformat(),
        "message": "Brief created successfully"
    }


@app.get("/api/briefs")
async def get_briefs(db: Session = Depends(get_db)):
    """Get all saved briefs"""
    briefs = db.query(Brief).order_by(Brief.created_at.desc()).all()
    return {
        "briefs": [
            {
                "id": b.id,
                "title": b.title,
                "content": b.content,
                "category": b.category,
                "created_at": b.created_at.isoformat(),
            }
            for b in briefs
        ]
    }


@app.get("/api/briefs/{brief_id}")
async def get_brief(brief_id: int, db: Session = Depends(get_db)):
    """Get a specific brief"""
    brief = db.query(Brief).filter(Brief.id == brief_id).first()
    if not brief:
        raise HTTPException(status_code=404, detail="Brief not found")
    
    return {
        "id": brief.id,
        "title": brief.title,
        "content": brief.content,
        "category": brief.category,
        "created_at": brief.created_at.isoformat(),
    }


@app.delete("/api/briefs/{brief_id}")
async def delete_brief(brief_id: int, db: Session = Depends(get_db)):
    """Delete a brief"""
    brief = db.query(Brief).filter(Brief.id == brief_id).first()
    if not brief:
        raise HTTPException(status_code=404, detail="Brief not found")
    
    db.delete(brief)
    db.commit()
    
    return {"success": True, "message": "Brief deleted"}


@app.delete("/api/briefs")
async def delete_all_briefs(db: Session = Depends(get_db)):
    """Delete all briefs"""
    count = db.query(Brief).count()
    db.query(Brief).delete()
    db.commit()
    
    return {"success": True, "message": f"Deleted {count} briefs"}


@app.get("/api/knowledge")
async def get_knowledge(category: Optional[str] = None, db: Session = Depends(get_db)):
    """Get knowledge items"""
    query = db.query(Knowledge)
    if category:
        query = query.filter(Knowledge.category == category)
    
    knowledge_items = query.order_by(Knowledge.created_at.desc()).all()
    
    return {
        "knowledge": [
            {
                "id": k.id,
                "title": k.title,
                "content": k.content,
                "category": k.category,
                "created_at": k.created_at.isoformat(),
            }
            for k in knowledge_items
        ]
    }


@app.post("/api/knowledge")
async def create_knowledge(knowledge: KnowledgeCreate, db: Session = Depends(get_db)):
    """Add new knowledge item"""
    new_knowledge = Knowledge(
        title=knowledge.title,
        content=knowledge.content,
        category=knowledge.category
    )
    db.add(new_knowledge)
    db.commit()
    db.refresh(new_knowledge)
    
    return {
        "success": True,
        "id": new_knowledge.id,
        "message": "Knowledge added successfully"
    }


@app.post("/api/knowledge/upload")
async def upload_knowledge(file: UploadFile = File(...), db: Session = Depends(get_db)):
    """Upload knowledge file (txt or md)"""
    
    if not file.filename.endswith(('.txt', '.md')):
        raise HTTPException(status_code=400, detail="Only .txt and .md files are supported")
    
    content = await file.read()
    text = content.decode('utf-8')
    
    # Create knowledge item from file
    knowledge = Knowledge(
        title=file.filename,
        content=text,
        category="uploaded"
    )
    db.add(knowledge)
    db.commit()
    db.refresh(knowledge)
    
    return {
        "success": True,
        "id": knowledge.id,
        "filename": file.filename,
        "message": "Knowledge file uploaded successfully"
    }


@app.post("/api/client-action")
async def handle_client_action(action: ClientAction):
    """Handle client-side action triggers"""
    # This endpoint allows the agent to trigger client-side actions
    # The frontend will poll or receive these actions
    
    return {
        "success": True,
        "action": action.action_type,
        "parameters": action.parameters
    }


@app.get("/api/stats")
async def get_stats(db: Session = Depends(get_db)):
    """Get application statistics"""
    return {
        "total_briefs": db.query(Brief).count(),
        "total_knowledge": db.query(Knowledge).count(),
        "total_conversations": db.query(Conversation).count(),
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
