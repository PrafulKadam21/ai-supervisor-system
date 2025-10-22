from flask import Blueprint, jsonify, request, render_template
from database.firebase_client import FirebaseClient
from agent.knowledge_base import KnowledgeBase
from services.help_request_service import HelpRequestService
from services.notification_service import NotificationService

# Create blueprint
bp = Blueprint('supervisor', __name__)

# Initialize services (will be set by app.py)
firebase_client = None
knowledge_base = None
help_request_service = None


def init_routes(fb_client: FirebaseClient, kb: KnowledgeBase, hr_service: HelpRequestService):
    """Initialize route dependencies"""
    global firebase_client, knowledge_base, help_request_service
    firebase_client = fb_client
    knowledge_base = kb
    help_request_service = hr_service


@bp.route('/')
def index():
    """Root redirect to dashboard"""
    return render_template('dashboard.html')


@bp.route('/dashboard')
def dashboard():
    """Render supervisor dashboard"""
    return render_template('dashboard.html')


@bp.route('/api/requests/pending', methods=['GET'])
def get_pending_requests():
    """Get all pending help requests"""
    try:
        requests = help_request_service.get_pending_requests()
        return jsonify({
            "success": True,
            "requests": [r.model_dump() for r in requests]
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@bp.route('/api/requests/all', methods=['GET'])
def get_all_requests():
    """Get all help requests"""
    try:
        limit = request.args.get('limit', 50, type=int)
        requests = help_request_service.get_all_requests(limit)
        return jsonify({
            "success": True,
            "requests": [r.model_dump() for r in requests]
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@bp.route('/api/requests/<request_id>/resolve', methods=['POST'])
def resolve_request(request_id):
    """Resolve a help request"""
    try:
        data = request.json
        answer = data.get('answer', '').strip()
        supervisor_name = data.get('supervisor_name', 'Supervisor').strip()
        
        if not answer:
            return jsonify({"success": False, "error": "Answer is required"}), 400
        
        success = help_request_service.resolve_request(request_id, answer, supervisor_name)
        
        if success:
            return jsonify({"success": True, "message": "Request resolved successfully"})
        else:
            return jsonify({"success": False, "error": "Failed to resolve request"}), 500
            
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@bp.route('/api/knowledge', methods=['GET'])
def get_knowledge():
    """Get all knowledge entries"""
    try:
        entries = knowledge_base.get_all_knowledge()
        return jsonify({
            "success": True,
            "knowledge": [e.model_dump() for e in entries]
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@bp.route('/api/knowledge/search', methods=['GET'])
def search_knowledge():
    """Search knowledge base"""
    try:
        query = request.args.get('q', '')
        if not query:
            return jsonify({"success": False, "error": "Query parameter 'q' is required"}), 400
        
        results = knowledge_base.search(query)
        return jsonify({
            "success": True,
            "results": [r.model_dump() for r in results] if isinstance(results, list) else [results.model_dump()] if results else []
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@bp.route('/api/stats', methods=['GET'])
def get_stats():
    """Get system statistics"""
    try:
        stats = help_request_service.get_stats()
        knowledge_count = len(knowledge_base.get_all_knowledge())
        
        return jsonify({
            "success": True,
            "stats": {
                **stats,
                "knowledge_entries": knowledge_count
            }
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@bp.route('/api/calls', methods=['GET'])
def get_calls():
    """Get recent call logs"""
    try:
        limit = request.args.get('limit', 50, type=int)
        calls = firebase_client.get_call_logs(limit)
        return jsonify({
            "success": True,
            "calls": [c.model_dump() for c in calls]
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500