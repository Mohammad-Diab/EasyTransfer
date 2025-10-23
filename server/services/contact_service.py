from database.models import ContactModel
from config import MAX_CONTACTS_PER_ACCOUNT
from constants import (
    ERROR_CONTACT_LIMIT_REACHED,
    ERROR_DUPLICATE_CONTACT_NAME,
    ERROR_PHONE_NUMBER_TOO_LONG,
    ERROR_NAME_TOO_LONG,
    ERROR_NAME_IS_DIGIT,
    ERROR_CONTACT_NOT_FOUND,
    MAX_PHONE_NUMBER_LENGTH,
    MAX_NAME_LENGTH
)


class ContactService:
    """Business logic for contacts"""
    
    @staticmethod
    def get_contacts(account_id):
        """Get all contacts for an account"""
        return ContactModel.get_by_account(account_id)
    
    @staticmethod
    def add_contact(account_id, phone_number, name):
        """Add a new contact with validation"""
        # Check contact limit
        existing_contacts = ContactModel.get_by_account(account_id)
        if len(existing_contacts) >= MAX_CONTACTS_PER_ACCOUNT:
            raise ValueError(ERROR_CONTACT_LIMIT_REACHED.format(limit=MAX_CONTACTS_PER_ACCOUNT))
        
        # Check for duplicate name
        for contact in existing_contacts:
            contact_id, phone_number, existing_name, date_added = contact
            if existing_name.lower() == name.lower():
                raise ValueError(ERROR_DUPLICATE_CONTACT_NAME.format(name=name))
        
        # Validate phone number length
        if len(phone_number) > MAX_PHONE_NUMBER_LENGTH:
            raise ValueError(ERROR_PHONE_NUMBER_TOO_LONG)
        
        # Validate name length
        if name.isdigit():
            raise ValueError(ERROR_NAME_IS_DIGIT)
        if len(name) > MAX_NAME_LENGTH:
            raise ValueError(ERROR_NAME_TOO_LONG)
        
        return ContactModel.add(account_id, phone_number, name)
    
    @staticmethod
    def delete_contact(account_id, contact_id):
        """Delete a contact with ownership verification"""
        contact = ContactModel.get_by_id(account_id, contact_id)
        
        if not contact:
            raise ValueError(ERROR_CONTACT_NOT_FOUND)
        
        ContactModel.delete(account_id, contact_id)
