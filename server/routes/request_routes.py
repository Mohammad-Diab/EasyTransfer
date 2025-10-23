from flask import Blueprint, request, jsonify
from services.request_service import RequestService
from utils.auth import require_auth
from utils.validation import validate_phone_number, validate_amount, validate_request_id
from constants import (
    ERROR_MISSING_REQUIRED_FIELDS_REQUEST,
    ERROR_INVALID_STATUS,
    ERROR_REQUEST_NOT_FOUND,
    STATUS_OK,
    STATUS_PENDING,
    STATUS_EMPTY,
    STATUS_SUCCESS,
    STATUS_FAILED,
    MESSAGE_NO_PENDING_REQUESTS,
)

request_bp = Blueprint('requests', __name__, url_prefix='/requests')


@request_bp.route('/', methods=['POST'])
@require_auth
def create_request(account_id):
    """Create a new request"""
    data = request.get_json()
    
    if not data:
        return jsonify({'error': 'Request body is required'}), 400
    
    phone_number = data.get('phone_number')
    amount = data.get('amount')

    if not phone_number or not amount:
        return jsonify({'error': ERROR_MISSING_REQUIRED_FIELDS_REQUEST}), 400

    # Validate phone number
    is_valid_phone, phone_error = validate_phone_number(phone_number)
    if not is_valid_phone:
        return jsonify({'error': phone_error}), 400

    # Validate amount
    is_valid_amount, amount_error = validate_amount(amount)
    if not is_valid_amount:
        return jsonify({'error': amount_error}), 400

    request_id = RequestService.create_request(account_id, phone_number, amount)
    return jsonify({'request_id': request_id, 'status': STATUS_PENDING}), 201


@request_bp.route('/next', methods=['GET'])
@require_auth
def get_next_request(account_id):
    """Get the next pending request"""
    row = RequestService.get_next_pending(account_id)
    if row:
        request_id, phone_number, amount = row
        return jsonify({
            'request_id': request_id,
            'phone_number': phone_number,
            'amount': amount,
            'status': STATUS_OK
        })
    else:
        return jsonify({
            'message': MESSAGE_NO_PENDING_REQUESTS,
            'status': STATUS_EMPTY
        }), 200


@request_bp.route('/<int:request_id>/result', methods=['POST'])
@require_auth
def add_result(account_id, request_id):
    """Add result for a request"""
    data = request.get_json()
    
    if not data:
        return jsonify({'error': 'Request body is required'}), 400
    
    status = data.get('status')
    message = data.get('message', '')

    if status not in [STATUS_SUCCESS, STATUS_FAILED]:
        return jsonify({'error': ERROR_INVALID_STATUS}), 400

    RequestService.add_result(account_id, request_id, status, message)
    return jsonify({'request_id': request_id, 'final_status': status, 'message': message})


@request_bp.route('/status/<int:request_id>', methods=['GET'])
@require_auth
def get_request_status(account_id, request_id):
    """Get request status by ID"""
    row = RequestService.get_request_by_id(account_id, request_id)
    if row:
        return jsonify({
            'request_id': row[0],
            'phone_number': row[1],
            'amount': row[2],
            'status': row[3]
        })
    else:
        return jsonify({'error': ERROR_REQUEST_NOT_FOUND}), 404
