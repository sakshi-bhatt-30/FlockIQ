import streamlit as st
from src.config.supabase_client import get_session

def render_page():
    # Add custom CSS for styling
    st.markdown("""
        <style>
        .center-content {
            text-align: center;
            margin-bottom: 50px; /* Adjust spacing below this section */
        }
        .button-section {
            margin-top: 50px; /* Adjust spacing above buttons */
        }
        </style>
    """, unsafe_allow_html=True)

    # Check if user is not logged in
    session = get_session()

    if not session:
        # Logo and Title
        col1, col2 = st.columns([1, 12])
        with col1:
            st.image("media/logo.png", width=400)
        with col2:
            st.markdown("""
            <div class="center-content">
                <h1>FlockIQ</h1>
                <h3>Revolutionize Your Surveys and Forms</h3>
                <p>Create, distribute, and analyze surveys with unprecedented ease and insight.</p>
            </div>
            """, unsafe_allow_html=True)

        # Features Section
        st.subheader("Why Choose FlockIQ?")
        cols = st.columns(3)
        
        with cols[0]:
            st.metric(label="🚀 Effortless Creation", value="Simple & Intuitive")
            st.caption("Build forms as easily as sending a message")
        
        with cols[1]:
            st.metric(label="📊 Advanced Analytics", value="Deep Insights")
            st.caption("Go beyond basic form responses")
        
        with cols[2]:
            st.metric(label="🔒 Enterprise Security", value="Top-Tier Protection")
            st.caption("Your data is always secure")

        # CTA Buttons with spacing
        st.markdown('<div class="button-section"></div>', unsafe_allow_html=True)
        col1, col2 = st.columns(2)
        
        with col1:
            login_button = st.button("Login", use_container_width=True)
            if login_button:
                st.session_state.active_page = "Login"
                st.rerun()
        
        with col2:
            signup_button = st.button("Sign Up", use_container_width=True)
            if signup_button:
                st.session_state.active_page = "Signup"
                st.rerun()

    else:
        pass

# This allows the page to be imported and used in the main app
if __name__ == "__main__":
    render_page()
