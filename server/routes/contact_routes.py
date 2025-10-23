from flask import Blueprint, request, jsonify
from services.contact_service import ContactService
from utils.auth import require_auth
from utils.validation import validate_phone_number, validate_name, validate_contact_id
from constants import (
    ERROR_MISSING_REQUIRED_FIELDS_CONTACT,
    SUCCESS_CONTACT_ADDED,
    SUCCESS_CONTACT_DELETED,
)

contact_bp = Blueprint('contacts', __name__, url_prefix='/contacts')


@contact_bp.route('/', methods=['GET'])
@require_auth
def get_contacts(account_id):
    """Get all contacts for an account"""
    rows = ContactService.get_contacts(account_id)
    contacts = []
    for row in rows:
        contacts.append({
            'id': row[0],
            'phone_number': row[1],
            'name': row[2],
            'date_added': row[3]
        })
    return jsonify({'contacts': contacts}), 200


@contact_bp.route('/', methods=['POST'])
@require_auth
def add_contact(account_id):
    """Add a new contact"""
    data = request.get_json()
    
    if not data:
        return jsonify({'error': 'Request body is required'}), 400
    
    phone_number = data.get('phone_number')
    name = data.get('name')

    if not phone_number or not name:
        return jsonify({'error': ERROR_MISSING_REQUIRED_FIELDS_CONTACT}), 400

    # Validate phone number
    is_valid_phone, phone_error = validate_phone_number(phone_number)
    if not is_valid_phone:
        return jsonify({'error': phone_error}), 400

    # Validate name
    is_valid_name, name_error = validate_name(name)
    if not is_valid_name:
        return jsonify({'error': name_error}), 400

    try:
        contact_id = ContactService.add_contact(account_id, phone_number, name)
        return jsonify({'contact_id': contact_id, 'message': SUCCESS_CONTACT_ADDED}), 201
    except ValueError as e:
        return jsonify({'error': str(e)}), 400


@contact_bp.route('/<int:contact_id>', methods=['DELETE'])
@require_auth
def delete_contact(account_id, contact_id):
    """Delete a contact"""
    try:
        ContactService.delete_contact(account_id, contact_id)
        return jsonify({'message': SUCCESS_CONTACT_DELETED}), 200
    except ValueError as e:
        return jsonify({'error': str(e)}), 404
