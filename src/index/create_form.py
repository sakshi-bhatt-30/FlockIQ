import streamlit as st
import uuid
from typing import List, Dict, Any
from src.config.supabase_client import get_supabase_client, get_session, is_user_authenticated
from src.services.form_service import FormService
import time

class FormCreationPage:
    def __init__(self):
        self.supabase = get_supabase_client()
        self.form_service = FormService(self.supabase)
        self.session = get_session()

    def validate_form(self, form_title: str, questions: List[Dict[str, Any]]) -> bool:
        """
        Validate form before submission
        """
        if not form_title.strip():
            st.error("Form title cannot be empty")
            return False
        
        if not questions:
            st.error("Please add at least one question to the form")
            return False
        
        for idx, question in enumerate(questions, 1):
            if not question.get('text'):
                st.error(f"Question {idx} text cannot be empty")
                return False
            
            if question.get('type') == 'multiple_choice' and not question.get('options'):
                st.error(f"Multiple choice question {idx} must have options")
                return False
        
        return True

    def render_question_input(self, index: int) -> Dict[str, Any]:
        """
        Render individual question input fields
        """
        # Mapping of user-friendly types to database-compatible types
        type_mapping = {
            'Short Text': 'short_text',
            'Long Text': 'long_text',
            'Multiple Choice': 'multiple_choice',
            'Checkboxes': 'checkbox',
            'Date': 'date',
            'Number': 'number'
        }

        st.subheader(f"Question {index}")
        
        # Question text
        question_text = st.text_input(
            f"Question {index} Text", 
            key=f"question_text_{index}"
        )
        
        # Question type selection with corrected types
        question_type = st.selectbox(
            f"Question {index} Type", 
            list(type_mapping.keys()),
            key=f"question_type_{index}"
        )
        
        # Optional settings
        is_required = st.checkbox(
            "Required Question", 
            key=f"is_required_{index}"
        )
        
        # Additional options based on question type
        options = []
        if question_type == 'Multiple Choice':
            option_input = st.text_input(
                f"Enter options (comma-separated)", 
                key=f"options_{index}"
            )
            options = [opt.strip() for opt in option_input.split(',') if opt.strip()]
        
        return {
            'text': question_text,
            'type': type_mapping[question_type],  # Use mapped database-compatible type
            'is_required': is_required,
            'options': options if options else None,
            'id': str(uuid.uuid4())
        }

    def render_page(self):
        """
        Main page rendering method
        """
        st.title("Create a New Form")
        
        # Ensure user is logged in
        if not is_user_authenticated():
            st.warning("Please log in to create a form")
            if st.button("Go to Login", use_container_width=True):
                st.session_state.active_page = "Create Form"
            return

        # Form title
        form_title = st.text_input("Form Title", key="form_title_input")
        form_description = st.text_area("Form Description (Optional)", key="form_description_input")

        # Form privacy settings
        is_public = st.checkbox("Make form publicly accessible", key="is_public_checkbox")
        allow_anonymous = st.checkbox("Allow anonymous responses", key="allow_anonymous_checkbox")

        # Session state to manage questions dynamically
        if 'questions' not in st.session_state:
            st.session_state.questions = []

        # Render existing questions
        questions_to_save = []
        for idx, _ in enumerate(st.session_state.questions, 1):
            with st.expander(f"Question {idx}", expanded=True):
                question = self.render_question_input(idx)
                questions_to_save.append(question)

        # Horizontal buttons for managing questions and form
        col1, col2, col3 = st.columns(3)
        
        with col1:
            # Add Question Button
            add_question = st.button("➕ Add Question", key="add_question_button", use_container_width=True)
        
        with col2:
            # Remove Last Question Button (only show if questions exist)
            if st.session_state.questions:
                remove_question = st.button("🗑️ Remove Last Question", key="remove_last_question", use_container_width=True)
        
        with col3:
            # Create Form Button
            create_form = st.button("🖋️ Create Form", key="create_form_button", use_container_width=True)

        # Handle button actions
        if add_question:
            st.session_state.questions.append({})
            st.rerun()
        
        if 'remove_question' in locals() and remove_question:
            st.session_state.questions.pop()
            st.rerun()
        
        if create_form:
            if self.validate_form(form_title, questions_to_save):
                try:
                    # Create form with all details
                    form_data = {
                        'title': form_title,
                        'description': form_description,
                        'is_public': is_public,
                        'allow_anonymous': allow_anonymous
                    }
                    
                    new_form = self.form_service.create_form(
                        creator_id=self.session.user.id,
                        form_data=form_data,
                        questions=questions_to_save
                    )
                    
                    if new_form:
                        # Display success message
                        st.success("Form created successfully!")
                        
                        # Create a placeholder for the countdown
                        countdown_placeholder = st.empty()
                        
                        # Countdown and redirect
                        for i in range(3, 0, -1):
                            countdown_placeholder.info(f"Redirecting to My Forms in {i} seconds...")
                            time.sleep(1)
                        
                        # Clear the countdown placeholder
                        countdown_placeholder.empty()
                        
                        # Reset questions and set the active page
                        st.session_state.questions = []
                        st.session_state.active_page = "My Forms"
                        st.rerun()
                    else:
                        st.error("Failed to create the form. Please try again.")

                except Exception as e:
                    st.error(f"Error creating form: {e}")

def render_page():
    """
    Entry point for Streamlit page rendering
    """
    page = FormCreationPage()
    page.render_page()

# This allows the page to be imported and used in the main app
if __name__ == "__main__":
    render_page()