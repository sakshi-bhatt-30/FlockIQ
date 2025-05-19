import streamlit as st
from src.services.auth_service import AuthService
import time

def render_page():
    st.header("Login to FlockIQ")
   
    # Initialize auth service
    auth_service = AuthService()
   
    # Login form
    with st.form("login_form"):
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
       
        submitted = st.form_submit_button("Log In")
       
        if submitted:
            # Validate inputs
            if not email or not password:
                st.error("Please enter both email and password")
                return
        
            # Attempt login
            try:
                user = auth_service.sign_in(email, password)
            
                if user:
                    st.success("Login successful!")
                    time.sleep(2)
                    # Explicitly set Streamlit to use the new page
                    st.switch_page("main.py")
                else:
                    st.error("Invalid email or password")
            except Exception as e:
                st.error(f"Login error: {str(e)}")
   
    # Add a signup link
    st.markdown("Don't have an account? ")
    signup_col1, signup_col2 = st.columns([1, 5])
    with signup_col1:
        if st.button("Sign Up", use_container_width=True):
            st.session_state.active_page = "Signup"
            st.rerun()

# This allows the page to be imported and used in the main app
if __name__ == "__main__":
    render_page()