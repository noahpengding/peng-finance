"""
Login Page - Frontend UI for user authentication
"""
import streamlit as st
from services.auth_service import AuthService


def main():
    st.header('Login')

    # Check if already logged in
    if AuthService.is_authenticated(st.session_state):
        st.success(f'Welcome back, {st.session_state["username"]}!')
        st.info('You are already logged in.')
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button('Go to Home', type='primary'):
                st.session_state['page'] = 'home'
                st.rerun()
        return

    # Login form
    with st.form('login_form'):
        st.subheader('Enter your credentials')
        
        username = st.text_input(
            'Username', 
            placeholder='Enter your username',
            help='Your registered username'
        )
        password = st.text_input(
            'Password', 
            type='password',
            placeholder='Enter your password',
            help='Your account password'
        )
        
        submitted = st.form_submit_button('Login', type='primary', use_container_width=True)
        
        if submitted:
            if not username or not password:
                st.error('Please enter both username and password.')
            else:
                with st.spinner('Authenticating...'):
                    result = AuthService.login_user(username, password)
                
                if result['success']:
                    # Store credentials for auto-login
                    AuthService.store_credentials(st.session_state, result['username'], result['token'])
                    st.success('Login successful!')
                    
                    # Redirect to home page
                    st.session_state['page'] = 'home'
                    st.rerun()
                else:
                    st.error(result['message'])


if __name__ == '__main__':
    main()
