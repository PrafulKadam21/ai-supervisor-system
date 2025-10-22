import asyncio
import os
from typing import Optional
from groq import Groq
from livekit import agents, rtc
from livekit.agents import Agent, AgentSession, JobContext, WorkerOptions, cli
from livekit.plugins import openai, silero
from database.firebase_client import FirebaseClient
from database.models import CallLog
from agent.knowledge_base import KnowledgeBase
from agent.prompts import build_system_prompt
from services.help_request_service import HelpRequestService
from services.notification_service import NotificationService


class FrontdeskAIAgent:
    """AI Agent that handles calls and escalates when needed"""
    
    def __init__(self):
        self.groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))
        self.firebase_client = FirebaseClient()
        self.knowledge_base = KnowledgeBase(self.firebase_client)
        self.notification_service = NotificationService()
        self.help_request_service = HelpRequestService(
            self.firebase_client,
            self.knowledge_base,
            self.notification_service
        )
        
        self.current_call_id: Optional[str] = None
        self.current_caller_phone: Optional[str] = None
        self.conversation_history = []
    
    async def entrypoint(self, ctx: JobContext):
        """Main entry point for LiveKit agent"""
        
        print("\n" + "="*60)
        print("🤖 AI AGENT STARTING")
        print("="*60 + "\n")
        
        # Connect to room
        await ctx.connect()
        
        # Wait for participant
        participant = await ctx.wait_for_participant()
        
        # Create call log
        caller_id = participant.identity or "unknown"
        self.current_caller_phone = f"+1-555-{caller_id[-7:]}"  # Simulated phone
        
        call_log = CallLog(
            caller_id=caller_id,
            caller_phone=self.current_caller_phone
        )
        self.current_call_id = self.firebase_client.create_call_log(call_log)
        
        print(f"📞 New call from: {self.current_caller_phone}")
        print(f"   Call ID: {self.current_call_id}\n")
        
        # Build system prompt with knowledge
        knowledge_context = self.knowledge_base.get_context_for_prompt()
        system_instructions = build_system_prompt(knowledge_context)
        
        # Create agent session using new API
        session = AgentSession(
            stt=openai.STT(),
            llm=openai.LLM(model="gpt-4o-mini"),
            tts=openai.TTS(),
            vad=silero.VAD.load(),
        )
        
        # Create agent with instructions
        agent = Agent(instructions=system_instructions)
        
        # Set up event handlers before starting
        session.on("user_speech_committed", self._create_user_speech_handler())
        session.on("agent_speech_committed", self._create_agent_speech_handler())
        
        # Start the session
        await session.start(room=ctx.room, agent=agent)
        
        # Generate initial greeting
        await session.generate_reply(
            instructions="Greet the caller warmly and ask how you can help them today."
        )
        
        # Keep alive
        await asyncio.sleep(3600)  # 1 hour max call
    
    def _create_user_speech_handler(self):
        """Create handler for user speech"""
        async def handler(event):
            message = event.get("message", "")
            self.conversation_history.append({"role": "user", "content": message})
            print(f"👤 Caller: {message}")
            
            # Check knowledge base
            knowledge_match = self.knowledge_base.search(message)
            
            if knowledge_match:
                print(f"✅ Found answer in knowledge base: {knowledge_match.question}")
                return
            
            # Check if we need to escalate using Groq
            await self._check_for_escalation(message)
        
        return handler
    
    def _create_agent_speech_handler(self):
        """Create handler for agent speech"""
        async def handler(event):
            message = event.get("message", "")
            self.conversation_history.append({"role": "assistant", "content": message})
            print(f"🤖 Agent: {message}")
        
        return handler
    
    async def _check_for_escalation(self, user_message: str):
        """Check if we should escalate to supervisor"""
        
        # Build full context with knowledge base
        knowledge_context = self.knowledge_base.get_context_for_prompt()
        system_context = build_system_prompt(knowledge_context)
        
        # Use Groq to check if AI can answer
        escalation_prompt = f"""Based on the business information and learned knowledge provided in your system context, can you confidently answer this customer question?

Question: "{user_message}"

Answer with ONLY one word:
- "YES" if you can answer this confidently with the information you have
- "NO" if you need supervisor help because you don't have enough information

Remember:
- If the question is about hours, pricing, services, location from the business info → YES
- If the question matches learned knowledge → YES  
- If asking for specific stylist schedules, complex custom pricing, or something not in your knowledge → NO
- Unclear or gibberish questions → NO

One word answer:"""

        try:
            response = self.groq_client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {"role": "system", "content": system_context},
                    {"role": "user", "content": escalation_prompt}
                ],
                temperature=0.1,
                max_tokens=10
            )
            
            decision = response.choices[0].message.content.strip().upper()
            
            print(f"🤔 AI Decision: {decision}")
            
            if "NO" in decision:
                print("⚠️  AI Decision: Cannot answer confidently - ESCALATING")
                await self._escalate_to_supervisor(user_message)
            else:
                print("✅ AI Decision: Can answer confidently")
                
        except Exception as e:
            print(f"Error checking for escalation: {e}")
    
    async def _escalate_to_supervisor(self, question: str):
        """Escalate question to supervisor"""
        
        context = "\n".join([
            f"{msg['role']}: {msg['content']}" 
            for msg in self.conversation_history[-5:]
        ])
        
        request_id = self.help_request_service.create_request(
            caller_id=self.current_call_id,
            caller_phone=self.current_caller_phone,
            question=question,
            context=context
        )
        
        # Update call log
        if self.current_call_id:
            self.firebase_client.update_call_log(
                self.current_call_id,
                {
                    "help_requests": [request_id],
                    "resolved_by_ai": False
                }
            )


def start_agent():
    """Start the AI agent"""
    agent = FrontdeskAIAgent()
    
    # Run with LiveKit CLI using new API
    cli.run_app(
        WorkerOptions(
            entrypoint_fnc=agent.entrypoint,
        )
    )


if __name__ == "__main__":
    start_agent()