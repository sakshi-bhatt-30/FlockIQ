from src.config.supabase_client import get_supabase_client
import streamlit as st

class AuthService:
    def __init__(self):
        self.supabase = get_supabase_client()
   
    def sign_up(self, email, password, profile_data):
        """
        Sign up a new user with comprehensive error handling and profile creation
        
        Args:
            email (str): User's email address
            password (str): User's password
            profile_data (dict): Additional user profile information
        
        Returns:
            user: Supabase user object if signup is successful
        """
        try:
            # Validate email and password
            if not email or not password:
                raise ValueError("Email and password are required")
            
            # Email validation (basic regex)
            import re
            email_regex = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
            if not re.match(email_regex, email):
                raise ValueError("Invalid email format")
            
            # Password strength validation
            if len(password) < 8:
                raise ValueError("Password must be at least 8 characters long")
            
            # Prepare signup data
            signup_data = {
                "email": email,
                "password": password
            }
            
            # Create user in Supabase Auth
            response = self.supabase.auth.sign_up(signup_data)
            
            # If signup is successful, add additional profile data
            if response.user:
                user_id = response.user.id
                
                # Prepare profile data for insertion
                profile_insert_data = {
                    'id': user_id,
                    'email': email,
                    'first_name': profile_data.get('first_name', ''),
                    'last_name': profile_data.get('last_name', ''),
                    'phone': profile_data.get('phone', ''),
                    'organization': profile_data.get('organization', ''),
                    'bio': profile_data.get('bio', '')
                }
                
                # Insert profile data
                profile_response = (
                    self.supabase
                    .table('user_info')
                    .insert(profile_insert_data)
                    .execute()
                )
                
                # Check if profile insertion was successful
                if profile_response.data:
                    return response.user
                else:
                    # Rollback user creation if profile insertion fails
                    self.supabase.auth.admin.delete_user(user_id)
                    raise Exception("Failed to create user profile")
            
            return None
        
        except Exception as e:
            # Comprehensive error logging
            print(f"Signup error: {str(e)}")
            raise

    def sign_in(self, email, password):
        """
        Sign in a user with more robust error handling
        """
        try:
            # Attempt to sign in with email and password
            response = self.supabase.auth.sign_in_with_password({
                "email": email,
                "password": password
            })
        
            # Check if user is successfully authenticated
            if response.session:
                # Set session state for logged-in user
                st.session_state['logged_in'] = True
                st.session_state.supabase_session = response.session
                st.session_state['current_page'] = 'Welcome'
                return response.user  # User is authenticated
            else:
                raise ValueError("Authentication failed")
        
        except Exception as e:
            print(f"Login error details: {str(e)}")
            raise ValueError("Invalid email or password")

    
    def sign_out(self):
        """
        Sign out the current user
        """
        try:
            # Remove session from Streamlit state
            if 'supabase_session' in st.session_state:
                del st.session_state.supabase_session
            
            # Sign out from Supabase
            self.supabase.auth.sign_out()
            
            return True
        except Exception as e:
            st.error(f"Logout failed: {str(e)}")
            return False
    
    def get_user_profile(self, user_id):
        """
        Retrieve user profile data
        """
        try:
            # Use user_info table instead of users
            response = self.supabase.table('user_info').select('*').eq('id', user_id).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            st.error(f"Error fetching profile: {str(e)}")
            return None
    
    def update_profile(self, user_id, profile_data):
        """
        Update user profile
        """
        try:
            # Remove None or empty values
            profile_data = {k: v for k, v in profile_data.items() if v}
            
            # Upsert (insert or update) profile data in user_info table
            response = self.supabase.table('user_info').upsert({
                'id': user_id,
                **profile_data
            }).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            st.error(f"Error updating profile: {str(e)}")
            return None