import streamlit as st
from src.services.auth_service import AuthService
import time

def render_page():
    st.header("Sign Up for FlockIQ")
   
    # Initialize auth service
    auth_service = AuthService()
   
    # Signup form
    with st.form("signup_form"):
        # Basic auth fields
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        confirm_password = st.text_input("Confirm Password", type="password")
       
        # Additional profile fields
        first_name = st.text_input("First Name")
        last_name = st.text_input("Last Name")
        phone = st.text_input("Phone Number")
       
        # Optional additional fields you might want
        organization = st.text_input("Organization (Optional)")
        bio = st.text_area("Bio (Optional)")
       
        submitted = st.form_submit_button("Sign Up")
       
        if submitted:
            # Client-side validation
            if not email:
                st.error("Email is required")
                st.stop()
           
            if not password:
                st.error("Password is required")
                st.stop()
           
            if password != confirm_password:
                st.error("Passwords do not match")
                st.stop()
           
            # Prepare profile data for user_info table
            profile_data = {
                'first_name': first_name,
                'last_name': last_name,
                'phone': phone,
                'organization': organization,
                'bio': bio
            }
           
            # Attempt signup
            try:
                user = auth_service.sign_up(email, password, profile_data)
               
                if user:
                    st.success("Account created successfully!")
                    st.info("Please log in with your new account.")
                    time.sleep(3)
                   
                    # Automatically redirect to login
                    st.session_state.active_page = "Login"

                    st.rerun()
                else:
                    st.error("Signup failed")
            
            except ValueError as ve:
                # Handle specific validation errors
                st.error(str(ve))
            except Exception as e:
                # Generic error handling
                st.error(f"An unexpected error occurred: {str(e)}")
   
    # Add a login link
    st.markdown("Already have an account? ")
    login_col1, login_col2 = st.columns([1, 5])
    with login_col1:
        if st.button("Log In", use_container_width=True):
            st.session_state.active_page = "Login"
            st.rerun()

# This allows the page to be imported and used in the main app
if __name__ == "__main__":
    render_page()