import streamlit as st
import os
import sys
import importlib

from config.configure import Config
from utils.minio_storage import download_db
from utils.sqlite_storage import initialize_db
from utils.output_log import logger
from services.auth_service import AuthService

# Add project root to sys.path for module resolution
sys.path.insert(0, os.path.abspath('.'))

# Setup on first run
if not os.path.exists(Config.LOCAL_DB_PATH):
    os.makedirs(os.path.dirname(Config.LOCAL_DB_PATH), exist_ok=True)
    download_db()
    initialize_db()

# Configure page
st.set_page_config(
    page_title="Peng Finance",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("💰 Peng Finance")

# Authentication check - try to auto-authenticate first
if 'authentication_checked' not in st.session_state:
    auth_result = AuthService.auto_authenticate(st.session_state)
    if auth_result['success']:
        logger.info(f"Auto-authenticated user: {auth_result['username']}")
    st.session_state['authentication_checked'] = True

# Route based on authentication status
if not AuthService.is_authenticated(st.session_state):
    # User not authenticated, force to login page
    st.session_state['page'] = 'login'
else:
    # User is authenticated, allow navigation
    # Navigation state: default to Home if not set
    if 'page' not in st.session_state:
        st.session_state['page'] = 'home'

# Render current page module using new pages_new structure
try:
    module_name = f"pages.{st.session_state['page'].lower()}_page"
    module = importlib.import_module(module_name)
    module.main()
except ModuleNotFoundError as e:
    st.error(f"Page not found: {st.session_state['page']}")
    logger.error(f"Module import error: {e}")
    st.session_state['page'] = 'home'
    st.rerun()
except Exception as e:
    st.error(f"Error loading page: {str(e)}")
    logger.error(f"Page loading error: {e}")
    st.session_state['page'] = 'home'
    st.rerun()