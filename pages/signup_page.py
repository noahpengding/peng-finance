"""
Signup Page - Frontend UI for user registration
"""
import streamlit as st
from services.auth_service import AuthService


def main():
    st.header('Create New Account')

    # Check if already logged in
    if AuthService.is_authenticated(st.session_state):
        st.info('You are already logged in.')
        if st.button('Go to Home'):
            st.session_state['page'] = 'home'
            st.rerun()
        return

    # Signup form
    with st.form('signup_form'):
        st.subheader('Account Information')
        
        col1, col2 = st.columns(2)
        
        with col1:
            admin_pw = st.text_input(
                'Admin Password', 
                type='password',
                placeholder='Enter admin password',
                help='Required for account creation'
            )
            email = st.text_input(
                'Email', 
                placeholder='Enter your email address',
                help='For account recovery and notifications'
            )
        
        with col2:
            username = st.text_input(
                'Username', 
                placeholder='Choose a username',
                help='This will be your login username'
            )
            password = st.text_input(
                'Password', 
                type='password',
                placeholder='Create a strong password',
                help='Choose a secure password'
            )
        
        submitted = st.form_submit_button('Create Account', type='primary', use_container_width=True)
        
        if submitted:
            with st.spinner('Creating account...'):
                result = AuthService.signup_user(admin_pw, username, password, email)
            
            if result['success']:
                st.success(result['message'])
                st.info('Please proceed to Login.')
            else:
                st.error(result['message'])


if __name__ == '__main__':
    main()
