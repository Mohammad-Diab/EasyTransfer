import jwt
import datetime
import os
from dotenv import load_dotenv
from typing import Dict, Optional
import logging

logger = logging.getLogger(__name__)

class JWTManager:
    """Manages JWT token validation and user-token mapping from environment variables."""
    
    def __init__(self):
        """Initialize JWT manager with secret from environment."""
        load_dotenv()
        self.jwt_secret = os.getenv('JWT_SECRET')
        if not self.jwt_secret:
            raise ValueError("JWT_SECRET not found in environment variables. Please add JWT_SECRET to your .env file.")
        
        # Dictionary to store authorized users and their tokens (populated at startup)
        self.authorized_tokens: Dict[str, str] = {}
        
        # Initialize user-token mapping from environment variables
        self._load_user_token_mapping()
    
    def _load_user_token_mapping(self):
        """Load user-token mapping from environment variables and validate tokens."""
        # Get users and tokens from environment variables
        users_str = os.getenv('AUTHORIZED_USERS', '')
        tokens_str = os.getenv('AUTHORIZED_TOKENS', '')
        
        if not users_str or not tokens_str:
            logger.warning("AUTHORIZED_USERS or AUTHORIZED_TOKENS not found in environment variables")
            return
        
        # Split by comma and clean up
        users = [user.strip() for user in users_str.split(',') if user.strip()]
        tokens = [token.strip() for token in tokens_str.split(',') if token.strip()]
        
        # Check if lists have same length
        if len(users) != len(tokens):
            logger.error(f"Mismatch in user-token lists: {len(users)} users but {len(tokens)} tokens")
            return
        
        # Validate each token and map to user
        for i, (user_id, token) in enumerate(zip(users, tokens)):
            if self._validate_user_token(user_id, token):
                self.authorized_tokens[user_id] = token
            else:
                logger.error(f"❌ User at position {i+1} has invalid token - skipping")
    
    def _validate_user_token(self, user_id: str, token: str) -> bool:
        """
        Validate if the token belongs to the specific user and is valid.
        
        Args:
            user_id (str): User ID
            token (str): JWT token to validate
            
        Returns:
            bool: True if token is valid and belongs to the user, False otherwise
        """
        try:
            # Decode token without verification first to check payload
            payload = jwt.decode(token, self.jwt_secret, algorithms=["HS256"])
            
            # Check if token belongs to the user
            token_user_id = payload.get('sub')
            if token_user_id != user_id:
                logger.error("Token user mismatch: user ID does not match token")
                return False
            
            # Check if token is expired
            exp = payload.get('exp')
            if exp and datetime.datetime.utcnow().timestamp() > exp:
                logger.error("Token has expired")
                return False
            
            return True
            
        except jwt.ExpiredSignatureError:
            logger.error("Token has expired")
            return False
        except jwt.InvalidTokenError as e:
            logger.error("Invalid token format")
            return False
        except Exception as e:
            logger.error("Error validating token")
            return False
    
    def get_token_for_user(self, user_id: str) -> Optional[str]:
        """
        Get JWT token for a specific user.
        
        Args:
            user_id (str): User ID
            
        Returns:
            Optional[str]: JWT token if user is authorized and has valid token, None otherwise
        """
        return self.authorized_tokens.get(str(user_id))
    
    def validate_token(self, token: str) -> Optional[Dict]:
        """
        Validate a JWT token and return its payload.
        
        Args:
            token (str): JWT token to validate
            
        Returns:
            Optional[Dict]: Token payload if valid, None otherwise
        """
        try:
            payload = jwt.decode(token, self.jwt_secret, algorithms=["HS256"])
            return payload
        except jwt.ExpiredSignatureError:
            logger.error("Token has expired")
            return None
        except jwt.InvalidTokenError:
            logger.error("Invalid token")
            return None
    
    def get_authorized_tokens(self) -> Dict[str, str]:
        """
        Get the complete dictionary of authorized users and their tokens.
        
        Returns:
            Dict[str, str]: Dictionary mapping user IDs to their JWT tokens
        """
        return self.authorized_tokens.copy()
    
    def is_user_authorized(self, user_id: str) -> bool:
        """
        Check if a user is authorized (has valid token).
        
        Args:
            user_id (str): User ID to check
            
        Returns:
            bool: True if user is authorized, False otherwise
        """
        return str(user_id) in self.authorized_tokens

# Global instance
jwt_manager = JWTManager()
