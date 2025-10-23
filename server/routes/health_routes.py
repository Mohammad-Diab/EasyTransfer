from flask import Blueprint, jsonify
from utils.auth import require_auth
from constants import STATUS_PONG

health_bp = Blueprint('health', __name__)

@health_bp.route('/ping', methods=['GET'])
def ping():
    """Health check endpoint - no authentication required"""
    return jsonify({'status': STATUS_PONG})

@health_bp.route('/ping-auth', methods=['GET'])
@require_auth
def ping_auth(account_id):
    """Authenticated health check endpoint - tests both server and token validity"""
    return jsonify({
        'status': STATUS_PONG,
        'authenticated': True,
    })
