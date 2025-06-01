"""
Authentication Service - Backend logic for user authentication operations
"""
from utils.auth import (
    verify_password, create_jwt, hash_password, validate_stored_auth, 
    store_auth_credentials, clear_auth_credentials
)
from utils.sqlite_storage import get_user, update_user_token, create_user
from config.configure import Config
from utils.output_log import logger


class AuthService:
    """Service class for handling authentication operations"""
    
    @staticmethod
    def login_user(username: str, password: str) -> dict:
        """Authenticate user and return result"""
        user = get_user(username)
        if not user:
            return {'success': False, 'message': 'User not found.'}
        
        if not verify_password(password, user.password):
            return {'success': False, 'message': 'Invalid password.'}
        
        token = create_jwt(username)
        update_user_token(username, token)
        logger.debug(f"User {username} logged in successfully")
        
        return {'success': True, 'username': username, 'token': token}
    
    @staticmethod
    def signup_user(admin_password: str, username: str, password: str, email: str) -> dict:
        """Create new user account"""
        if admin_password != Config.ADMIN_PASSWORD:
            return {'success': False, 'message': 'Invalid admin password.'}
        
        if get_user(username):
            return {'success': False, 'message': 'Username already exists.'}
        
        hashed = hash_password(password)
        token = create_jwt(username)
        create_user(username, hashed, email, token)
        update_user_token(username, token)
        
        logger.debug(f"User {username} created successfully")
        return {'success': True, 'message': 'User created successfully.'}
    
    @staticmethod
    def is_authenticated(session_state: dict) -> bool:
        """Check if user is authenticated"""
        return 'username' in session_state
    
    @staticmethod
    def auto_authenticate(session_state: dict) -> dict:
        """
        Automatically authenticate user based on stored credentials.
        Returns dict with 'success' boolean, 'username' if successful, and 'message'.
        """
        auth_result = validate_stored_auth(session_state)
        
        if auth_result['valid']:
            username = auth_result['username']
            logger.debug(f"Auto-authenticated user: {username}")
            return {
                'success': True, 
                'username': username, 
                'message': 'Auto-authenticated successfully'
            }
        else:
            return {
                'success': False, 
                'username': None, 
                'message': 'No valid stored credentials'
            }
    
    @staticmethod
    def store_credentials(session_state: dict, username: str, token: str):
        """Store authentication credentials for future auto-login"""
        store_auth_credentials(session_state, username, token)
        logger.debug(f"Stored credentials for user: {username}")
    
    @staticmethod
    def logout_user(session_state: dict):
        """Logout user and clear all stored credentials"""
        username = session_state.get('username', 'Unknown')
        clear_auth_credentials(session_state)
        logger.debug(f"User {username} logged out")
        return {'success': True, 'message': 'Logged out successfully'}
