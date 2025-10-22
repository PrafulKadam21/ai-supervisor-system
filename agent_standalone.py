"""
Standalone agent runner - Run this directly with: python agent_standalone.py dev
"""
import asyncio
import os
from typing import Optional
from dotenv import load_dotenv

# Load environment variables FIRST
load_dotenv()

# Configure SSL for macOS
import certifi
os.environ['SSL_CERT_FILE'] = certifi.where()
os.environ['REQUESTS_CA_BUNDLE'] = certifi.where()

from groq import Groq
from livekit.agents import Agent, AgentSession, JobContext, WorkerOptions, cli
from livekit.plugins import openai, deepgram, silero

# Import our custom Groq LLM adapter
import sys
sys.path.insert(0, os.path.dirname(__file__))



async def entrypoint(ctx: JobContext):
    """Main entry point for LiveKit agent - Initialize everything HERE to avoid pickle errors"""
    
    # Import here to avoid pickle issues
    from database.firebase_client import FirebaseClient
    from database.models import CallLog
    from agent.knowledge_base import KnowledgeBase
    from agent.prompts import build_system_prompt
    from services.help_request_service import HelpRequestService
    from services.notification_service import NotificationService
    
    # Initialize services INSIDE the entrypoint (after fork/spawn)
    groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))
    firebase_client = FirebaseClient()
    knowledge_base = KnowledgeBase(firebase_client)
    notification_service = NotificationService()
    help_request_service = HelpRequestService(
        firebase_client,
        knowledge_base,
        notification_service
    )
    
    # Track conversation state
    conversation_history = []
    current_call_id: Optional[str] = None
    current_caller_phone: Optional[str] = None
    
    print("\n" + "="*60)
    print("🤖 AI AGENT STARTING")
    print("="*60 + "\n")
    
    # Connect to room
    await ctx.connect()
    
    # Wait for participant
    participant = await ctx.wait_for_participant()
    
    # Create call log
    caller_id = participant.identity or "unknown"
    current_caller_phone = f"+1-555-{caller_id[-7:]}"
    
    call_log = CallLog(
        caller_id=caller_id,
        caller_phone=current_caller_phone
    )
    current_call_id = firebase_client.create_call_log(call_log)
    
    print(f"📞 New call from: {current_caller_phone}")
    print(f"   Call ID: {current_call_id}\n")
    
    # Build system prompt with knowledge
    knowledge_context = knowledge_base.get_context_for_prompt()
    system_instructions = build_system_prompt(knowledge_context)
    
    # Helper function for escalation check
    async def check_for_escalation(user_message: str):
        """Check if we should escalate to supervisor"""
        knowledge_context = knowledge_base.get_context_for_prompt()
        system_context = build_system_prompt(knowledge_context)
        
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
            response = groq_client.chat.completions.create(
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
                
                # Escalate
                context = "\n".join([
                    f"{msg['role']}: {msg['content']}" 
                    for msg in conversation_history[-5:]
                ])
                
                request_id = help_request_service.create_request(
                    caller_id=current_call_id,
                    caller_phone=current_caller_phone,
                    question=user_message,
                    context=context
                )
                
                if current_call_id:
                    firebase_client.update_call_log(
                        current_call_id,
                        {
                            "help_requests": [request_id],
                            "resolved_by_ai": False
                        }
                    )
            else:
                print("✅ AI Decision: Can answer confidently")
                
        except Exception as e:
            print(f"Error checking for escalation: {e}")
    
    # Create agent with instructions (new API in LiveKit 1.2)
    agent = Agent(
        instructions=system_instructions,
    )
    
    # Create agent session with 100% FREE providers!
    session = AgentSession(
    vad=silero.VAD.load(),           # FREE
    stt=deepgram.STT(),              # FREE ($200 credits)
    llm=openai.LLM(model="gpt-3.5-turbo"),  # FREE ($5 credits = 1000+ conversations)
    tts=deepgram.TTS(),              # FREE ($200 credits)
)
    
    # Event handlers for tracking conversation (must be sync!)
    @session.on("user_speech_committed")
    def on_user_speech(event):
        message = event.get("content", "")
        if not message:
            return
            
        conversation_history.append({"role": "user", "content": message})
        print(f"👤 Caller: {message}")
        
        # Check knowledge base
        knowledge_match = knowledge_base.search(message)
        
        if knowledge_match:
            print(f"✅ Found answer in knowledge base: {knowledge_match.question}")
            return
        
        # Check if we need to escalate (run in background)
        asyncio.create_task(check_for_escalation(message))
    
    @session.on("agent_speech_committed")
    def on_agent_speech(event):
        message = event.get("content", "")
        if not message:
            return
            
        conversation_history.append({"role": "assistant", "content": message})
        print(f"🤖 Agent: {message}")
    
    # Start the session with agent and room
    await session.start(agent=agent, room=ctx.room)
    
    # Generate initial greeting
    await session.generate_reply(
        instructions="Greet the caller warmly and ask how you can help them today."
    )
    
    print("\n✅ Voice assistant started and ready!")
    print("Listening for participant speech...\n")


if __name__ == "__main__":
    # Run with LiveKit CLI
    cli.run_app(
        WorkerOptions(
            entrypoint_fnc=entrypoint,
        )
    )