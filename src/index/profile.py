import streamlit as st
from src.services.auth_service import AuthService
from src.config.supabase_client import get_session

def render_page():
    # Check if user is logged in
    session = get_session()
    if not session:
        st.warning("Please log in to view your profile")
        return
    
    # Initialize auth service
    auth_service = AuthService()
    
    st.title("Update Profile")
    
    # Fetch current profile
    user_profile = auth_service.get_user_profile(session.user.id)
    
    if user_profile:
        # Profile update form
        with st.form("profile_update_form"):
            first_name = st.text_input("First Name", value=user_profile.get('first_name', ''))
            last_name = st.text_input("Last Name", value=user_profile.get('last_name', ''))
            phone = st.text_input("Phone Number", value=user_profile.get('phone', ''))
            
            # Optional fields
            organization = st.text_input("Organization", value=user_profile.get('organization', ''))
            bio = st.text_area("Bio", value=user_profile.get('bio', ''))
            
            submitted = st.form_submit_button("Update Profile")
            
            if submitted:
                # Prepare updated profile data
                profile_data = {
                    'first_name': first_name,
                    'last_name': last_name,
                    'phone': phone,
                    'organization': organization,
                    'bio': bio
                }
                
                # Update profile
                updated_profile = auth_service.update_profile(session.user.id, profile_data)
                
                if updated_profile:
                    st.success("Profile updated successfully!")
                else:
                    st.error("Failed to update profile")
    else:
        st.error("Unable to fetch profile information")

# This allows the page to be imported and used in the main app
if __name__ == "__main__":
    render_page()