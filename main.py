import streamlit as st
from src.services.auth_service import AuthService
# Import page modules
import src.index.list_forms as list_forms
import src.index.create_form as create_form
import src.index.my_forms as my_forms
import src.index.fill_form as fill_form
import src.index.my_responses as my_responses
import src.index.form_templates as form_templates
import src.index.form_analytics as form_analytics
import src.index.form_dashboard as form_dashboard
import src.index.profile as profile
import src.index.welcome as welcome
import src.index.home as home
import src.index.login as login
import src.index.signup as signup

# Navbar setup
NAV_CATEGORIES = {
    "Main": ["Welcome", "List Forms",  "Form Templates"],
    "Forms": ["Create Form", "My Forms", "Fill Form", "My Responses", "Profile"],
    "Analytics": [ "Form Dashboard", "Form Analytics"],
}

# Page render functions
PAGE_FUNCTIONS = {
    "Home": home.render_page,
    "Welcome": welcome.render_page,
    "List Forms": list_forms.render_page,
    "Create Form": create_form.render_page,
    "My Forms": my_forms.render_page,
    "Fill Form": fill_form.render_page,
    "My Responses": my_responses.render_page,
    "Profile": profile.render_page,
    "Login": login.render_page,
    "Signup": signup.render_page,
    "Form Templates": form_templates.render_page,
    "Form Dashboard": form_dashboard.render_page,
    "Form Analytics": form_analytics.render_page
}

def logout(auth_service):
    auth_service.sign_out()
    st.session_state.logged_in = False
    st.session_state.active_page = "Home"  # Change to Home instead of Login
    st.rerun()

def render_navbar(auth_service):
    # Build navigation dynamically based on login state
    with st.sidebar:
        if st.session_state.logged_in:
            # Logout button
            if st.button("Logout"):
                logout(auth_service)
            
            # Render categories and pages
            for category, pages in NAV_CATEGORIES.items():
                with st.expander(category, expanded=True):
                    for page in pages:
                        if st.button(page):
                            st.session_state.active_page = page
                            st.rerun()
        else:
            # Login/Signup for logged-out users
            if st.button("Login"):
                st.session_state.active_page = "Login"
                st.rerun()
            if st.button("Signup"):
                st.session_state.active_page = "Signup"
                st.rerun()

def main():
    # Set page configuration
    st.set_page_config(page_title="FlockIQ", layout="wide", initial_sidebar_state="collapsed")
    
    # Initialize authentication service
    auth_service = AuthService()
    
    # Check and initialize session state
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False
    
    # Set default page to Home for non-logged-in users
    if "active_page" not in st.session_state:
        st.session_state.active_page = "Home"
    
    # Render navbar
    render_navbar(auth_service)
    
    # Render active page with logic for logged-in users
    active_page = st.session_state.active_page
    
    if st.session_state.logged_in:
        # If logged in and no active page, default to Welcome
        if active_page in ["Home", "Login", "Signup"]:
            active_page = "Welcome"
    else:
        # If not logged in, restrict to Home, Login, Signup
        if active_page not in ["Home", "Login", "Signup"]:
            active_page = "Home"
    
    # Render the appropriate page
    PAGE_FUNCTIONS[active_page]()

if __name__ == "__main__":
    main()