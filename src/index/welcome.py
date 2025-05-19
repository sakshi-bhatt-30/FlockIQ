import streamlit as st
from src.config.supabase_client import get_supabase_client, get_session, is_user_authenticated

def render_page():
    # Ensure user is authenticated
    if not is_user_authenticated():
        st.warning("Please log in to access FlockIQ")
        if st.button("Go to Login", use_container_width=True):
            st.session_state.active_page = "Login"
            st.rerun()
        st.stop()

    # Get user session and info
    session = get_session()
    supabase = get_supabase_client()

    # Fetch user's first name
    try:
        user_info_response = (
            supabase.table('user_info')
            .select('first_name')
            .eq('id', session.user.id)
            .execute()
        )
        first_name = user_info_response.data[0]['first_name'] if user_info_response.data else "User"
    except Exception:
        first_name = "User"

    # Welcome title with user's name
    st.title(f"Welcome to FlockIQ, {first_name}! 👋")
   
    st.markdown("""
    ## Streamline Your Data Collection
   
    FlockIQ is a powerful, intuitive platform designed to simplify form creation, 
    distribution, and response management. Whether you're conducting surveys, 
    gathering feedback, or collecting critical information, we've got you covered.
    """)
   
    # Feature sections with columns
    st.markdown("## Explore FlockIQ Features")
    
    # First row of features
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.subheader("📋 Published Forms")
        st.write("""
        Discover and interact with forms shared across your network. 
        Browse through public surveys, organizational questionnaires, 
        and community-created forms.
        """)
        feature_cols = st.columns(2)
        with feature_cols[0]:
            if st.button("Browse Forms", use_container_width=True):
                st.session_state.active_page = "List Forms"
                st.rerun()
        with feature_cols[1]:
            if st.button("Quick Fill", use_container_width=True):
                st.info("Coming soon! Get ready to quickly respond to forms.")
    
    with col2:
        st.subheader("➕ Create Form")
        st.write("""
        Design custom forms with ease. Choose from multiple question types, 
        set privacy options, and create professional-looking surveys 
        in just a few clicks.
        """)
        feature_cols = st.columns(2)
        with feature_cols[0]:
            if st.button("New Form", use_container_width=True):
                st.session_state.active_page = "Create Form"
                st.rerun()
        with feature_cols[1]:
            if st.button("Form Templates", use_container_width=True):
                st.session_state.active_page = "Form Templates"
                st.rerun()
    
    with col3:
        st.subheader("📊 My Forms")
        st.write("""
        Manage your created forms, track responses, and gain insights. 
        Monitor form performance, analyze data, and make informed decisions 
        with comprehensive form management.
        """)
        feature_cols = st.columns(2)
        with feature_cols[0]:
            if st.button("My Forms", use_container_width=True, key="my_forms"):
                st.session_state.active_page = "My Forms"
                st.rerun()
        with feature_cols[1]:
            if st.button("Form Analytics", use_container_width=True):
                st.session_state.active_page = "Form Analytics"
                st.rerun()
    
    # Additional sections
    st.markdown("---")
    
    # Quick Actions and Guides
    st.markdown("## Quick Actions")
    
    quick_action_cols = st.columns(3)
    
    with quick_action_cols[0]:
        st.subheader("🔒 Privacy Controls")
        if st.button("Manage Privacy Settings", use_container_width=True, key="privacy_settings"):
            st.info("Coming soon! Control form visibility and response access.")
    
    with quick_action_cols[1]:
        st.subheader("👥 Team Collaboration")
        if st.button("Invite Team Members", use_container_width=True, key="team_invite"):
            st.info("Coming soon! Collaborate with team members on forms.")
    
    with quick_action_cols[2]:
        st.subheader("📈 Account Insights")
        if st.button("Account Overview", use_container_width=True, key="account_overview"):
            st.info("Coming soon! View your FlockIQ account summary and usage.")
    
    # Closing guidance
    st.markdown("""
    ---
   
    ### Getting Started Tips
    - 🌐 Explore public forms to understand different survey styles
    - 🖋️ Create your first form with our intuitive form builder
    - 📊 Track and analyze form responses in real-time
    - 🤝 Collaborate and share forms with your team
   
    Need help? Check our support resources or contact our support team.
    """)

# This allows the page to be imported and used in the main app
if __name__ == "__main__":
    render_page()