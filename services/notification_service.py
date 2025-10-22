from datetime import datetime


class NotificationService:
    """Service for handling notifications (simulated via console)"""
    
    def __init__(self):
        self.notification_log = []
    
    def notify_supervisor(self, message: str, request_id: str):
        """
        Notify supervisor about a new help request
        In production, this would send via SMS, Slack, email, etc.
        """
        notification = {
            "type": "supervisor_alert",
            "timestamp": datetime.utcnow().isoformat(),
            "request_id": request_id,
            "message": message
        }
        self.notification_log.append(notification)
        
        print(f"\n{'*'*60}")
        print(f"📱 SUPERVISOR NOTIFICATION")
        print(f"{'*'*60}")
        print(message)
        print(f"\nView and respond at: http://localhost:5000/dashboard")
        print(f"{'*'*60}\n")
    
    def send_to_caller(self, phone: str, message: str):
        """
        Send follow-up message to caller
        In production, this would use Twilio or similar SMS service
        """
        notification = {
            "type": "caller_followup",
            "timestamp": datetime.utcnow().isoformat(),
            "phone": phone,
            "message": message
        }
        self.notification_log.append(notification)
        
        print(f"\n{'='*60}")
        print(f"💬 SMS TO CALLER: {phone}")
        print(f"{'='*60}")
        print(message)
        print(f"{'='*60}\n")
    
    def get_notification_log(self):
        """Get all notifications sent"""
        return self.notification_log