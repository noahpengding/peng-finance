"""
Navigation Service - Backend logic for page navigation
"""
import streamlit as st
from services.auth_service import AuthService


class NavigationService:
    """Service class for handling page navigation"""
    
    PAGES = ['Home', 'Input', 'Category', 'Login', 'Signup']
    
    @staticmethod
    def redirect_to_login_if_not_authenticated():
        """Redirect to login page if user is not authenticated"""
        if not AuthService.is_authenticated(st.session_state):
            st.session_state['page'] = 'Login'
            st.rerun()
            return True
        return False
