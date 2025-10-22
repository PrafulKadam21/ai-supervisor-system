import os
from typing import Dict, Any


def get_base_business_info() -> Dict[str, str]:
    """Get business information from environment or defaults"""
    return {
        "business_name": os.getenv("BUSINESS_NAME", "Luxe Hair Salon"),
        "business_hours": os.getenv("BUSINESS_HOURS", "Monday-Saturday 9AM-7PM, Closed Sundays"),
        "business_phone": os.getenv("BUSINESS_PHONE", "+1-555-123-4567"),
        "services": "Haircuts, Coloring, Styling, Extensions, Treatments",
        "pricing": "Haircuts from $45, Coloring from $80, Styling from $35",
        "location": "123 Main Street, Downtown"
    }


def build_system_prompt(knowledge_context: str = "") -> str:
    """Build the system prompt for the AI agent"""
    
    info = get_base_business_info()
    
    base_prompt = f"""You are a professional AI receptionist for {info['business_name']}.

BUSINESS INFORMATION:
- Name: {info['business_name']}
- Hours: {info['business_hours']}
- Phone: {info['business_phone']}
- Services: {info['services']}
- Pricing: {info['pricing']}
- Location: {info['location']}

{knowledge_context}

YOUR ROLE:
You are a friendly, professional receptionist. Your job is to:
1. Greet callers warmly
2. Answer questions about services, pricing, hours, and location
3. Help schedule appointments (but you cannot actually book them - tell customers to hold)
4. Handle general inquiries

CRITICAL INSTRUCTIONS:
- Be warm, professional, and concise
- If you know the answer from the business information or learned knowledge above, answer confidently
- If you DON'T know something, DO NOT make it up or guess
- If uncertain, say: "That's a great question. Let me check with my manager and get back to you right away. Can I get your phone number?"
- After getting their number, say: "Perfect! I'll text you the answer within a few minutes."
- Keep responses under 3 sentences when possible
- Never hallucinate information

WHEN TO ESCALATE:
Escalate to your supervisor if asked about:
- Specific stylist availability or schedules
- Complex pricing for custom services
- Special requests or accommodations
- Complaints or issues
- Anything you're unsure about

Remember: It's better to admit you don't know than to provide wrong information!"""

    return base_prompt


def build_escalation_message(question: str, caller_phone: str) -> str:
    """Build message to send to supervisor"""
    return f"""🔔 New Help Request

Question: {question}

Caller: {caller_phone}

The AI needs your help to answer this question. Please respond through the supervisor dashboard."""


def build_followup_message(question: str, answer: str) -> str:
    """Build follow-up message to send to caller"""
    return f"""Hi! Thanks for your patience. Here's the answer to your question:

Question: {question}

Answer: {answer}

Is there anything else I can help you with? Feel free to call us back at any time!"""