"""
Simplified AI Agent for testing without LiveKit
Run this to test the system end-to-end without voice
"""
import os
from groq import Groq
from dotenv import load_dotenv
from database.firebase_client import FirebaseClient
from database.models import CallLog
from agent.knowledge_base import KnowledgeBase
from agent.prompts import build_system_prompt
from services.help_request_service import HelpRequestService
from services.notification_service import NotificationService

load_dotenv()


class SimpleTestAgent:
    """Text-based AI agent for testing"""
    
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
        
        self.conversation_history = []
        self.current_call_id = None
        self.current_caller_phone = None
    
    def start_call(self, caller_phone: str):
        """Start a new call session"""
        print("\n" + "="*60)
        print(f"📞 INCOMING CALL from {caller_phone}")
        print("="*60 + "\n")
        
        self.current_caller_phone = caller_phone
        
        # Create call log
        call_log = CallLog(
            caller_id=f"test_{caller_phone}",
            caller_phone=caller_phone
        )
        self.current_call_id = self.firebase_client.create_call_log(call_log)
        
        self.conversation_history = []
        
        print("🤖 AI: Hello! Thank you for calling. How can I help you today?\n")
    
    def process_message(self, user_message: str) -> str:
        """Process user message and return AI response"""
        print(f"👤 Caller: {user_message}\n")
        
        # Add to history
        self.conversation_history.append({
            "role": "user",
            "content": user_message
        })
        
        # Check if we should escalate
        should_escalate = self._should_escalate(user_message)
        
        if should_escalate:
            # Escalate to supervisor
            context = "\n".join([
                f"{msg['role']}: {msg['content']}" 
                for msg in self.conversation_history[-5:]
            ])
            
            request_id = self.help_request_service.create_request(
                caller_id=self.current_call_id,
                caller_phone=self.current_caller_phone,
                question=user_message,
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
            
            response = (
                "That's a great question! Let me check with my manager to get you "
                "the most accurate information. I'll text you the answer within a few minutes. "
                "Is there anything else I can help you with right now?"
            )
        else:
            # Generate normal response
            response = self._generate_response(user_message)
        
        self.conversation_history.append({
            "role": "assistant",
            "content": response
        })
        
        print(f"🤖 AI: {response}\n")
        return response
    
    def _should_escalate(self, user_message: str) -> bool:
        """Determine if question should be escalated"""
        
        # Build context with knowledge
        knowledge_context = self.knowledge_base.get_context_for_prompt()
        system_prompt = build_system_prompt(knowledge_context)
        
        # Ask Groq if it can answer
        escalation_check = f"""Based on the business information and learned knowledge provided in your context, can you confidently and accurately answer this customer question?

Question: "{user_message}"

Answer with ONLY one word - "YES" or "NO":

- Answer YES if:
  * Question is about hours, pricing, services, location (from business info)
  * Question matches your learned knowledge
  * Customer is making small talk, saying thanks, yes, no, goodbye
  * Customer wants to book an appointment (you can tell them to hold)
  
- Answer NO if:
  * Asking about specific stylist schedules or availability
  * Complex custom pricing questions
  * Special accommodations or complaints
  * Something truly outside your knowledge

One word only:"""

        try:
            response = self.groq_client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": escalation_check}
                ],
                temperature=0.1,
                max_tokens=10
            )
            
            decision = response.choices[0].message.content.strip().upper()
            
            # If response contains "NO", escalate
            if "NO" in decision:
                print(f"⚠️  AI Decision: Cannot answer confidently - ESCALATING")
                return True
            else:
                print(f"✅ AI Decision: Can answer confidently")
                return False
                
        except Exception as e:
            print(f"Error in escalation check: {e}")
            # On error, escalate to be safe
            return True
    
    def _generate_response(self, user_message: str) -> str:
        """Generate AI response"""
        
        knowledge_context = self.knowledge_base.get_context_for_prompt()
        system_prompt = build_system_prompt(knowledge_context)
        
        # Build message history for context
        messages = [{"role": "system", "content": system_prompt}]
        messages.extend(self.conversation_history[-10:])  # Last 10 messages
        
        try:
            response = self.groq_client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=messages,
                temperature=0.7,
                max_tokens=150
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            print(f"Error generating response: {e}")
            return "I apologize, I'm having trouble right now. Could you please try again?"
    
    def end_call(self):
        """End the call session"""
        if self.current_call_id:
            from datetime import datetime, UTC
            self.firebase_client.update_call_log(
                self.current_call_id,
                {"ended_at": datetime.now(UTC)}
            )
        
        print("\n" + "="*60)
        print("📞 CALL ENDED")
        print("="*60 + "\n")


def interactive_mode():
    """Run interactive test mode"""
    agent = SimpleTestAgent()
    
    print("\n" + "="*70)
    print("🤖 FRONTDESK AI - INTERACTIVE TEST MODE")
    print("="*70)
    print("\nCommands:")
    print("  - Type your message to talk to the AI")
    print("  - Type 'new' to start a new call")
    print("  - Type 'quit' to exit")
    print("="*70 + "\n")
    
    # Start first call
    agent.start_call("+1-555-TEST-001")
    
    call_count = 1
    
    while True:
        try:
            user_input = input("👤 You: ").strip()
            
            if not user_input:
                continue
            
            if user_input.lower() == 'quit':
                agent.end_call()
                print("\nGoodbye! 👋\n")
                break
            
            if user_input.lower() == 'new':
                agent.end_call()
                call_count += 1
                agent.start_call(f"+1-555-TEST-{call_count:03d}")
                continue
            
            agent.process_message(user_input)
            
        except KeyboardInterrupt:
            print("\n\nExiting...\n")
            agent.end_call()
            break
        except Exception as e:
            print(f"\n❌ Error: {e}\n")


def run_automated_test():
    """Run automated test scenarios"""
    agent = SimpleTestAgent()
    
    print("\n" + "="*70)
    print("🧪 RUNNING AUTOMATED TEST SCENARIOS")
    print("="*70 + "\n")
    
    # Scenario 1: Question AI can answer
    print("\n" + "-"*70)
    print("SCENARIO 1: Question AI should answer")
    print("-"*70 + "\n")
    
    agent.start_call("+1-555-TEST-101")
    agent.process_message("What are your hours?")
    agent.process_message("Thank you!")
    agent.end_call()
    
    # Scenario 2: Question requiring escalation
    print("\n" + "-"*70)
    print("SCENARIO 2: Question requiring escalation")
    print("-"*70 + "\n")
    
    agent.start_call("+1-555-TEST-102")
    agent.process_message("Do you offer wedding packages?")
    agent.process_message("Okay, thanks")
    agent.end_call()
    
    # Scenario 3: Multiple questions
    print("\n" + "-"*70)
    print("SCENARIO 3: Multiple questions in one call")
    print("-"*70 + "\n")
    
    agent.start_call("+1-555-TEST-103")
    agent.process_message("How much is a haircut?")
    agent.process_message("What about coloring?")
    agent.process_message("Do you have parking?")  # Should escalate
    agent.end_call()
    
    print("\n" + "="*70)
    print("✅ AUTOMATED TESTS COMPLETE")
    print("="*70)
    print("\n👉 Check the supervisor dashboard at http://localhost:5000")
    print("   to see escalated requests and respond to them.\n")


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "test":
        run_automated_test()
    else:
        interactive_mode()