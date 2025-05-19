import streamlit as st
from src.config.supabase_client import get_supabase_client
from src.services.form_service import FormService
from datetime import datetime

class ListFormsPage:
    def __init__(self):
        self.supabase = get_supabase_client()
        self.form_service = FormService(self.supabase)

    def get_published_forms(self):
        """
        Retrieve all published forms with additional details
        """
        try:
            # First, let's print out all forms and their creator_ids for debugging
            forms_response = (
                self.supabase.table('forms')
                .select('id, created_at, creator_id')
                .eq('is_public', True)
                .execute()
            )
            
            print("Forms response:", forms_response.data)  # Debug print
            
            forms = forms_response.data or []
            
            for form in forms:
                print(f"Processing form with creator_id: {form.get('creator_id')}")  # Debug print
                
                # Make sure creator_id exists and is not None
                if not form.get('creator_id'):
                    form['creator_name'] = 'Unknown Creator (No creator_id)'
                    continue

                # Get creator's info using creator_id with debug logging
                user_info_response = (
                    self.supabase.table('user_info')
                    .select('*')  # Select all columns for debugging
                    .eq('id', form['creator_id'])
                    .execute()
                )

                if user_info_response.data and len(user_info_response.data) > 0:
                    user_info = user_info_response.data[0]
                    
                    # Print all available fields in user_info for debugging
                    print("Available user info fields:", user_info.keys())
                    
                    first_name = user_info.get('first_name', '').strip()
                    last_name = user_info.get('last_name', '').strip()
                    email = user_info.get('email', '').strip()
                    
                    print(f"Retrieved name parts: '{first_name}' '{last_name}' '{email}'")  # Debug print

                    # Set creator name with detailed fallback logging
                    if first_name or last_name:
                        form['creator_name'] = f"{first_name} {last_name}".strip()
                        print(f"Using full name: {form['creator_name']}")
                    elif email:
                        form['creator_name'] = email
                        print("Falling back to email")
                    else:
                        form['creator_name'] = 'Unknown Creator (No name or email)'
                        print("No name or email found")
                else:
                    form['creator_name'] = 'Unknown Creator (No user info found)'
                    print(f"No user info found for creator_id: {form['creator_id']}")
                
                # Format timestamps
                if form['created_at']:
                    created_at = datetime.fromisoformat(form['created_at'].replace('Z', '+00:00'))
                    form['formatted_date'] = created_at.strftime("%B %d, %Y")
                    form['formatted_time'] = created_at.strftime("%I:%M %p")

            return forms

        except Exception as e:
            print(f"Detailed error: {str(e)}")  # Debug print
            st.error(f"Error fetching published forms: {str(e)}")
            return []

    def get_form_questions(self, form_id):
        """
        Retrieve questions for a specific form
        """
        try:
            response = (
                self.supabase.table('questions')
                .select('*')
                .eq('form_id', form_id)
                .execute()
            )
            return response.data or []
        except Exception as e:
            st.error(f"Error fetching form questions: {e}")
            return []

    def render_form_details_modal(self, form):
        """
        Render a modal with detailed form information
        """
        st.subheader("Form Details")
        
        # Fetch questions for this form
        questions = self.get_form_questions(form['id'])
        
        # Display form metadata with formatted date/time
        st.write(f"**Form ID:** `{form['id']}`")
        st.write(f"**Created By:** {form['creator_name']}")
        st.write(f"**Created On:** {form['formatted_date']} at {form['formatted_time']}")
        
        # Display questions
        st.subheader("Questions")
        for idx, question in enumerate(questions, 1):
            with st.expander(f"Question {idx}"):
                st.write(f"**Text:** {question['questions_text']}")
                st.write(f"**Type:** {question['question_type']}")
                st.write(f"**Required:** {'Yes' if question['is_required'] else 'No'}")
                if question['options']:
                    st.write(f"**Options:** {', '.join(question['options'])}")

    def render_page(self):
        """
        Main page rendering method
        """
        st.title("Published Forms")
        
        # Search bar (non-functional for now)
        search_term = st.text_input("Search Forms", placeholder="Coming soon...")
        st.info("Search functionality coming soon!")
        
        # Fetch published forms
        published_forms = self.get_published_forms()
        
        # Display forms in a grid or list
        if not published_forms:
            st.info("No published forms available.")
        else:
            for form in published_forms:
                with st.container(border=True):
                    col1, col2 = st.columns([3, 1])
                    
                    with col1:
                        st.write(f"**Created by:** {form['creator_name']}")
                        st.write(f"**Created on:** {form['formatted_date']} at {form['formatted_time']}")
                    
                    with col2:
                        if st.button("View Details", key=f"details_{form['id']}"):
                            self.render_form_details_modal(form)

def render_page():
    """
    Entry point for Streamlit page rendering
    """
    page = ListFormsPage()
    page.render_page()

# This allows the page to be imported and used in the main app
if __name__ == "__main__":
    render_page()