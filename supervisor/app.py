from flask import Flask
import os

from database.firebase_client import FirebaseClient
from agent.knowledge_base import KnowledgeBase
from services.notification_service import NotificationService
from services.help_request_service import HelpRequestService

from supervisor.routes import bp as supervisor_bp, init_routes


def create_app() -> Flask:
    """Create and configure the Flask supervisor app"""
    app = Flask(__name__, template_folder=os.path.join(os.path.dirname(__file__), 'templates'))

    # Initialize backend services
    fb_client = FirebaseClient()
    kb = KnowledgeBase(fb_client)
    notif = NotificationService()
    hr_service = HelpRequestService(fb_client, kb, notif)

    # Wire routes with their dependencies
    init_routes(fb_client, kb, hr_service)

    # Register blueprint
    app.register_blueprint(supervisor_bp)

    return app


def start_supervisor_dashboard(port: int = 5000):
    """Start the supervisor dashboard Flask app on the given port."""
    app = create_app()
    # Use 0.0.0.0 to be reachable from other hosts if needed
    app.run(host='0.0.0.0', port=port, debug=True)
