from typing import List, Dict, Any, Optional
from openai import OpenAI
import json
import os
from tools import ToolRegistry


class Agent:
    """Agentic system that plans and executes tasks"""
    
    def __init__(self, db_session, openai_api_key: str):
        self.client = OpenAI(api_key=openai_api_key)
        self.tools = ToolRegistry(db_session)
        self.conversation_history = []
        self.activity_log = []
        
    def _create_system_prompt(self, knowledge_context: Optional[str] = None) -> str:
        """Create system prompt with optional knowledge context"""
        base_prompt = """You are a Sports Brief Builder Agent. Your role is to help users create comprehensive sports briefings, reports, and analyses.

You have access to the following capabilities:
1. Fetch live sports scores and recent game results
2. Search a knowledge base for teams, players, statistics, and sports facts
3. Save briefs to the database
4. Generate statistical analyses
5. Export briefs in various formats

When given a task:
1. First, create a clear plan with specific steps
2. Execute each step using available tools
3. Synthesize results into a coherent response
4. For save_brief and export_brief actions, inform the user that approval is required

Always be helpful, accurate, and concise. Use the knowledge base to enhance your responses with factual information."""
        
        if knowledge_context:
            base_prompt += f"\n\nRELEVANT KNOWLEDGE CONTEXT:\n{knowledge_context}\n\nUse this knowledge to provide accurate and detailed information in your response."
        
        return base_prompt
    
    async def create_plan(self, user_goal: str, knowledge_context: Optional[str] = None) -> Dict[str, Any]:
        """Create a lightweight plan for achieving the user's goal"""
        
        messages = [
            {"role": "system", "content": self._create_system_prompt(knowledge_context)},
            {"role": "user", "content": f"Create a step-by-step plan to accomplish this goal: {user_goal}\n\nProvide a concise plan with 3-5 specific steps."}
        ]
        
        response = self.client.chat.completions.create(
            model="gpt-4-turbo-preview",
            messages=messages,
            temperature=0.7,
        )
        
        plan_text = response.choices[0].message.content
        
        # Parse plan into structured format
        plan_steps = []
        for line in plan_text.split('\n'):
            line = line.strip()
            if line and (line[0].isdigit() or line.startswith('-') or line.startswith('•')):
                # Remove numbering/bullets
                step = line.lstrip('0123456789.-•) ').strip()
                if step:
                    plan_steps.append(step)
        
        return {
            "plan": plan_text,
            "steps": plan_steps,
            "total_steps": len(plan_steps),
        }
    
    async def execute_plan(self, user_goal: str, knowledge_context: Optional[str] = None, session_history: Optional[List[Dict]] = None) -> Dict[str, Any]:
        """Execute the plan to achieve user's goal"""
        
        self.activity_log = []
        
        # Initialize conversation with system prompt and history
        messages = [
            {"role": "system", "content": self._create_system_prompt(knowledge_context)}
        ]
        
        # Add session history if available
        if session_history:
            messages.extend(session_history[-6:])  # Last 3 exchanges
        
        messages.append({"role": "user", "content": user_goal})
        
        # First, create the plan
        self.activity_log.append({
            "step": "planning",
            "action": "Creating execution plan",
            "status": "in_progress",
        })
        
        plan_result = await self.create_plan(user_goal, knowledge_context)
        
        self.activity_log[-1]["status"] = "completed"
        self.activity_log[-1]["result"] = plan_result["plan"]
        
        # Execute with tool calling
        tool_calls_made = []
        max_iterations = 10
        iteration = 0
        
        current_messages = messages.copy()
        
        while iteration < max_iterations:
            iteration += 1
            
            response = self.client.chat.completions.create(
                model="gpt-4-turbo-preview",
                messages=current_messages,
                tools=self.tools.get_tool_definitions(),
                tool_choice="auto",
                temperature=0.7,
            )
            
            message = response.choices[0].message
            current_messages.append(message.model_dump())
            
            # Check if agent wants to call tools
            if message.tool_calls:
                for tool_call in message.tool_calls:
                    tool_name = tool_call.function.name
                    tool_args = json.loads(tool_call.function.arguments)
                    
                    # Log the tool call attempt
                    self.activity_log.append({
                        "step": f"tool_execution_{len(tool_calls_made) + 1}",
                        "action": f"Calling tool: {tool_name}",
                        "arguments": tool_args,
                        "status": "in_progress",
                    })
                    
                    # Execute the tool
                    result = await self.tools.execute_tool(tool_name, tool_args)
                    
                    # Update log
                    self.activity_log[-1]["status"] = "completed" if result.get("success") else "failed"
                    self.activity_log[-1]["result"] = result
                    
                    # Check if tool requires approval
                    requires_approval = tool_name in ["save_brief", "export_brief"]
                    if requires_approval:
                        self.activity_log[-1]["requires_approval"] = True
                    
                    tool_calls_made.append({
                        "tool": tool_name,
                        "arguments": tool_args,
                        "result": result,
                        "requires_approval": requires_approval,
                    })
                    
                    # Add tool result to conversation
                    current_messages.append({
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "content": json.dumps(result),
                    })
            else:
                # No more tool calls, agent has final response
                break
        
        # Get final response
        final_response = current_messages[-1].content if hasattr(current_messages[-1], 'content') else message.content
        
        # Determine which knowledge was used
        knowledge_used = []
        knowledge_sources_used = []
        
        if knowledge_context:
            knowledge_used.append({
                "source": "knowledge_base",
                "influence": "Used to enhance response with factual information",
            })
        
        for tool_call in tool_calls_made:
            if tool_call["tool"] == "search_knowledge":
                results = tool_call["result"].get("results", [])
                for r in results:
                    knowledge_sources_used.append({
                        "source": r.get("title", "Knowledge item"),
                        "category": r.get("category", "general"),
                        "relevance": r.get("relevance", "medium"),
                        "influence": f"Enhanced response with {r.get('title', 'knowledge')} ({r.get('relevance', 'medium')} relevance)",
                    })
        
        # Combine knowledge - prioritize specific search results, then general knowledge base
        if knowledge_sources_used:
            knowledge_used = knowledge_sources_used + knowledge_used
        
        return {
            "success": True,
            "plan": plan_result,
            "response": final_response,
            "tool_calls": tool_calls_made,
            "activity_log": self.activity_log,
            "knowledge_used": knowledge_used,
            "iterations": iteration,
        }
