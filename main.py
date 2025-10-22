"""
Main entry point for Frontdesk AI Supervisor System
"""
import os
import sys
import argparse
import subprocess
from dotenv import load_dotenv


# Load environment variables
load_dotenv()


def check_environment():
    required_vars = [
        'LIVEKIT_URL',
        'LIVEKIT_API_KEY',
        'LIVEKIT_API_SECRET',
        'GROQ_API_KEY',
        'FIREBASE_CREDENTIALS_PATH'
    ]
    
    missing = [var for var in required_vars if not os.getenv(var)]
    
    if missing:
        print("❌ Missing required environment variables:")
        for var in missing:
            print(f"   - {var}")
        print("\nPlease check your .env file")
        return False
    
    return True


def start_supervisor():
    """Start supervisor dashboard"""
    from supervisor.app import start_supervisor_dashboard
    port = int(os.getenv('SUPERVISOR_PORT', 5001))
    start_supervisor_dashboard(port)


def start_agent():
    """Start AI agent using the standalone script"""
    print("\n" + "="*60)
    print("🤖 STARTING AI AGENT")
    print("="*60 + "\n")
    print("Running LiveKit agent in development mode...")
    print("Use Ctrl+C to stop the agent\n")
    
    # Run the standalone agent script with 'dev' mode
    subprocess.run([
        sys.executable,
        "agent_standalone.py",
        "dev"
    ])


def test_system():
    """Run system tests"""
    print("\n" + "="*60)
    print("🧪 RUNNING SYSTEM TESTS")
    print("="*60 + "\n")
    
    # Test Firebase connection
    try:
        from database.firebase_client import FirebaseClient
        fb = FirebaseClient()
        print("✅ Firebase connection successful")
    except Exception as e:
        print(f"❌ Firebase connection failed: {e}")
        return
    
    # Test Groq API
    try:
        from groq import Groq
        groq = Groq(api_key=os.getenv("GROQ_API_KEY"))
        response = groq.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{"role": "user", "content": "Hello"}],
            max_tokens=10
        )
        print("✅ Groq API connection successful")
    except Exception as e:
        print(f"❌ Groq API connection failed: {e}")
        return
    
    # Test knowledge base
    try:
        from agent.knowledge_base import KnowledgeBase
        kb = KnowledgeBase(fb)
        print(f"✅ Knowledge base loaded ({len(kb.get_all_knowledge())} entries)")
    except Exception as e:
        print(f"❌ Knowledge base failed: {e}")
        return
    
    print("\n" + "="*60)
    print("✅ ALL TESTS PASSED")
    print("="*60 + "\n")


def seed_data():
    """Seed initial data for testing"""
    print("\n" + "="*60)
    print("🌱 SEEDING INITIAL DATA")
    print("="*60 + "\n")
    
    from database.firebase_client import FirebaseClient
    from database.models import HelpRequest, KnowledgeEntry, RequestStatus
    from datetime import datetime, timedelta
    
    fb = FirebaseClient()
    
    # Seed some knowledge
    knowledge_items = [
        {
            "question": "What are your hours?",
            "answer": "We're open Monday-Saturday 9AM-7PM, closed Sundays."
        },
        {
            "question": "How much is a haircut?",
            "answer": "Haircuts start at $45. Prices vary based on hair length and stylist."
        },
        {
            "question": "Do you take walk-ins?",
            "answer": "Yes, we accept walk-ins but recommend calling ahead to check availability."
        },
        {
            "question": "Where are you located?",
            "answer": "We're located at 123 Main Street in Downtown."
        }
    ]
    
    for item in knowledge_items:
        entry = KnowledgeEntry(**item, source="initial_seed")
        fb.add_knowledge(entry)
        print(f"✅ Added knowledge: {item['question']}")
    
    # Seed a sample help request
    sample_request = HelpRequest(
        caller_id="test_caller_1",
        caller_phone="+1-555-999-0001",
        question="Do you offer senior discounts?",
        context="Caller asking about pricing for elderly customers",
        status=RequestStatus.PENDING
    )
    req_id = fb.create_help_request(sample_request)
    print(f"✅ Added sample help request: {req_id}")
    
    print("\n" + "="*60)
    print("✅ DATA SEEDING COMPLETE")
    print("="*60 + "\n")


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description='Frontdesk AI Supervisor System')
    parser.add_argument('command', choices=['supervisor', 'agent', 'test', 'seed'],
                       help='Command to run')
    
    args = parser.parse_args()
    
    # Check environment
    if not check_environment():
        sys.exit(1)
    
    print("\n" + "="*60)
    print("🚀 FRONTDESK AI SUPERVISOR SYSTEM")
    print("="*60 + "\n")
    
    if args.command == 'supervisor':
        start_supervisor()
    elif args.command == 'agent':
        start_agent()
    elif args.command == 'test':
        test_system()
    elif args.command == 'seed':
        seed_data()


if __name__ == "__main__":
    main()