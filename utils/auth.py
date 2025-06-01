import hashlib
import jwt
import datetime
from config.configure import Config


def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode('utf-8')).hexdigest()


def verify_password(password: str, hashed: str) -> bool:
    return hash_password(password) == hashed


def create_jwt(username: str) -> str:
    payload = {
        'sub': username,
        'iat': datetime.datetime.utcnow(),
        'exp': datetime.datetime.utcnow() + datetime.timedelta(days=30)  # 1 month expiration
    }
    token = jwt.encode(payload, Config.JWT_SECRET, algorithm='HS256')
    return token


def decode_jwt(token: str) -> dict:
    try:
        payload = jwt.decode(token, Config.JWT_SECRET, algorithms=['HS256'])
        return payload
    except Exception:
        return None


def is_token_valid(token: str) -> bool:
    """Check if JWT token is valid and not expired"""
    if not token:
        return False
    
    payload = decode_jwt(token)
    if not payload:
        return False
    
    # Check if token is expired
    exp_timestamp = payload.get('exp')
    if not exp_timestamp:
        return False
    
    current_timestamp = datetime.datetime.utcnow().timestamp()
    return current_timestamp < exp_timestamp


def get_username_from_token(token: str) -> str:
    """Extract username from JWT token"""
    payload = decode_jwt(token)
    if payload:
        return payload.get('sub')
    return None


def get_persistent_auth_key() -> str:
    """Generate a consistent key for storing auth data across sessions"""
    return "peng_finance_auth_data"


def load_persistent_credentials(session_state: dict):
    """
    Load authentication credentials from persistent storage.
    Uses a special session state key that persists across browser sessions.
    """
    auth_key = get_persistent_auth_key()
    
    # Check if we have persistent auth data
    if auth_key in session_state:
        auth_data = session_state[auth_key]
        if isinstance(auth_data, dict) and 'username' in auth_data and 'token' in auth_data:
            # Load into current session
            session_state['stored_username'] = auth_data['username']
            session_state['stored_token'] = auth_data['token']


def save_persistent_credentials(session_state: dict, username: str, token: str):
    """
    Save authentication credentials to persistent storage.
    This allows auto-login across browser sessions.
    """
    auth_key = get_persistent_auth_key()
    auth_data = {
        'username': username,
        'token': token,
        'saved_at': datetime.datetime.utcnow().isoformat()
    }
    session_state[auth_key] = auth_data


def clear_persistent_credentials(session_state: dict):
    """Clear persistent authentication credentials"""
    auth_key = get_persistent_auth_key()
    if auth_key in session_state:
        del session_state[auth_key]


def validate_stored_auth(session_state: dict) -> dict:
    """
    Validate stored authentication credentials from session state.
    Returns dict with 'valid' boolean and 'username' if valid.
    """
    # First try to load from persistent storage if not already loaded
    if 'stored_username' not in session_state or 'stored_token' not in session_state:
        load_persistent_credentials(session_state)
    
    stored_username = session_state.get('stored_username')
    stored_token = session_state.get('stored_token')
    
    if not stored_username or not stored_token:
        return {'valid': False, 'username': None}
    
    if not is_token_valid(stored_token):
        # Clear invalid stored credentials
        clear_auth_credentials(session_state)
        return {'valid': False, 'username': None}
    
    # Verify username matches token
    token_username = get_username_from_token(stored_token)
    if token_username != stored_username:
        # Clear mismatched credentials
        clear_auth_credentials(session_state)
        return {'valid': False, 'username': None}
    
    return {'valid': True, 'username': stored_username}


def store_auth_credentials(session_state: dict, username: str, token: str):
    """Store authentication credentials in session state for persistence"""
    session_state['stored_username'] = username
    session_state['stored_token'] = token
    # Also set current session
    session_state['username'] = username
    session_state['token'] = token
    # Save to persistent storage
    save_persistent_credentials(session_state, username, token)


def clear_auth_credentials(session_state: dict):
    """Clear all authentication credentials from session state"""
    keys_to_clear = ['username', 'token', 'stored_username', 'stored_token']
    for key in keys_to_clear:
        if key in session_state:
            del session_state[key]
    # Also clear persistent storage
    clear_persistent_credentials(session_state)
