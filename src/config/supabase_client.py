import streamlit as st
from supabase import create_client, Client

def get_supabase_client() -> Client:
    """
    Creates and returns a Supabase client instance using Streamlit secrets
    """
    try:
        # Retrieve Supabase URL and key from Streamlit secrets
        url = st.secrets["SUPABASE_URL"]
        key = st.secrets["SUPABASE_KEY"]
       
        supabase: Client = create_client(url, key)
        return supabase
    except Exception as e:
        st.error(f"Error initializing Supabase client: {e}")
        raise

def get_session():
    """
    Get the current Supabase session with robust error handling
    """
    try:
        # Check if session exists in Streamlit session state first
        if 'supabase_session' in st.session_state:
            return st.session_state.supabase_session

        supabase = get_supabase_client()
        
        # Try to get the current session from Supabase
        session = supabase.auth.get_session()
        
        # If session exists, store it in Streamlit session state
        if session:
            st.session_state.supabase_session = session
            return session
        
        return None
    
    except Exception as e:
        st.error(f"Error retrieving session: {e}")
        return None

def is_user_authenticated():
    """
    Check if a user is currently authenticated
    """
    session = get_session()
    return session is not None and session.user is not None