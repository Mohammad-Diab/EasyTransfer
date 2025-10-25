import os
import requests
from typing import Dict, Any, Optional
import logging

import config
from jwt_manager import jwt_manager

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

class APIError(Exception):
    """Custom exception for API errors"""
    def __init__(self, message: str, status_code: Optional[int] = None, response_text: Optional[str] = None):
        super().__init__(message)
        self.status_code = status_code
        self.response_text = response_text

def make_api_request(
    endpoint: str,
    method: str = 'GET',
    data: Optional[Dict[str, Any]] = None,
    params: Optional[Dict[str, Any]] = None,
    headers: Optional[Dict[str, str]] = None,
    account_id: Optional[str] = None
) -> Dict[str, Any]:
    """
    Make an API request to the server.
    
    Args:
        endpoint: API endpoint (e.g., 'orders', 'users')
        method: HTTP method (GET, POST, PUT, DELETE)
        data: Request body (for POST/PUT)
        params: Query parameters
        account_id: Account ID to make the request for
    Returns:
        Dict containing the API response
        
    Raises:
        APIError: If the request fails or returns an error
    """
    url = f"{config.SERVER_URL.rstrip('/')}/{endpoint.lstrip('/')}/"
    
    # Set default headers if not provided
    if headers is None:
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
    
    # Add JWT token to headers if account_id is provided
    if account_id:
        token = jwt_manager.get_token_for_user(str(account_id))
        if token:
            headers['Authorization'] = f'Bearer {token}'
        else:
            logger.warning(f"No JWT token found for account {account_id}")
    
    try:
        logger.info(f"Making {method} request to {url}")
        
        if method.upper() == 'GET':
            response = requests.get(url, params=params, headers=headers, timeout=10, allow_redirects=False)
        elif method.upper() == 'POST':
            response = requests.post(url, json=data, params=params, headers=headers, timeout=10, allow_redirects=False)
        elif method.upper() == 'DELETE':
            response = requests.delete(url, params=params, headers=headers, timeout=10, allow_redirects=False)
        else:
            raise ValueError(f"Unsupported HTTP method: {method}")
        
        # Log the response (without sensitive data)
        logger.debug(f"API Response status: {response.status_code}")
        
        # Handle non-200 responses
        if not response.ok:
            error_msg = f"API request failed with status {response.status_code}"
            try:
                error_data = response.json()
                error_msg = error_data.get('error', str(error_data))
            except (ValueError, KeyError):
                error_msg = response.text or error_msg
            
            logger.error(f"API Error: {error_msg}")
            raise APIError(error_msg, status_code=response.status_code, response_text=response.text)
        
        # Return the JSON response if available, otherwise return the raw text
        try:
            return response.json()
        except ValueError:
            return {"status": "success", "data": response.text}
            
    except requests.exceptions.Timeout:
        error_msg = "انتهت مهلة الاتصال بالسيرفر"
        logger.error(error_msg)
        raise APIError(error_msg)
    except requests.exceptions.ConnectionError:
        error_msg = "لم أستطع الاتصال بالسيرفر"
        logger.error(error_msg)
        raise APIError(error_msg)
    except requests.exceptions.RequestException as e:
        error_msg = f"فشل الطلب: {str(e)}"
        logger.error(error_msg)
        raise APIError(error_msg)

# Specific API functions
def get_request_status(account_id:str, request_id: str) -> Dict[str, Any]:
    """Get the status of an request by ID"""
    return make_api_request(f"requests/status/{request_id}", 'GET', account_id=account_id)

def create_request(account_id: str, request_data: Dict[str, Any]) -> Dict[str, Any]:
    """Create a new request"""
    return make_api_request(f"requests", 'POST', data=request_data, account_id=account_id)

# Contacts API functions
def get_contacts(account_id: int) -> Dict[str, Any]:
    """Get list of all contacts for a specific account"""
    return make_api_request(f"contacts", 'GET', account_id=account_id)

def add_contact(account_id: int, phone_number: str, name: str) -> Dict[str, Any]:
    """Add a new contact to an account"""
    contact_data = {
        "phone_number": phone_number,
        "name": name
    }
    return make_api_request(f"contacts", 'POST', data=contact_data, account_id=account_id)

def delete_contact(account_id: int, contact_id: int) -> Dict[str, Any]:
    """Delete a contact from an account"""
    return make_api_request(f"contacts/{contact_id}", 'DELETE', account_id=account_id)
