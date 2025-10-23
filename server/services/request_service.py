from database.models import RequestModel, ResultModel
from constants import (
    STATUS_PROCESSING,
    STATUS_DONE,
    STATUS_FAILED,
    STATUS_SUCCESS
)


class RequestService:
    """Business logic for requests"""
    
    @staticmethod
    def create_request(account_id, phone_number, amount):
        """Create a new request"""
        return RequestModel.add(account_id, phone_number, amount)
    
    @staticmethod
    def get_next_pending(account_id):
        """Get the next pending request and mark it as processing"""
        request = RequestModel.get_next(account_id)
        if request:
            request_id = request[0]
            RequestModel.update_status(account_id, request_id, STATUS_PROCESSING)
        return request
    
    @staticmethod
    def add_result(account_id, request_id, status, message):
        """Add result for a request and update its status"""
        ResultModel.add(account_id, request_id, status, message)
        final_status = STATUS_DONE if status == STATUS_SUCCESS else STATUS_FAILED
        RequestModel.update_status(account_id, request_id, final_status)
    
    @staticmethod
    def get_request_by_id(account_id, request_id):
        """Get request by ID"""
        return RequestModel.get_by_id(account_id, request_id)
    
