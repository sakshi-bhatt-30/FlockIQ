import streamlit as st
import time
from src.config.supabase_client import get_supabase_client
from typing import Dict, List, Any
from datetime import datetime

class FormFillService:
    def __init__(self):
        self.supabase = get_supabase_client()
        
    def get_form_details(self, form_id: str) -> Dict[str, Any]:
        """
        Retrieve form details, questions, and creator information
        
        Args:
            form_id (str): ID of the form to retrieve
        
        Returns:
            Dict containing form, questions, and creator details
        """
        try:
            # Fetch form details
            form_response = self.supabase.table('forms').select('*').eq('id', form_id).execute()
            
            if not form_response.data:
                return None
            
            form = form_response.data[0]
            
            # Fetch creator details
            creator_response = (
                self.supabase.table('user_info')
                .select('*')
                .eq('id', form['creator_id'])
                .execute()
            )
            
            # Fetch questions for this form
            questions_response = (
                self.supabase.table('questions')
                .select('*')
                .eq('form_id', form_id)
                .order('order_number')
                .execute()
            )
            
            # Format creator name
            creator_name = 'Unknown Creator'
            if creator_response.data:
                creator = creator_response.data[0]
                first_name = creator.get('first_name', '').strip()
                last_name = creator.get('last_name', '').strip()
                email = creator.get('email', '').strip()
                
                if first_name or last_name:
                    creator_name = f"{first_name} {last_name}".strip()
                elif email:
                    creator_name = email
            
            # Format timestamp
            created_at = datetime.fromisoformat(form['created_at'].replace('Z', '+00:00'))
            formatted_date = created_at.strftime("%B %d, %Y")
            formatted_time = created_at.strftime("%I:%M %p")
            
            return {
                'form': form,
                'questions': questions_response.data,
                'creator_name': creator_name,
                'formatted_date': formatted_date,
                'formatted_time': formatted_time
            }
        except Exception as e:
            st.error(f"Error fetching form: {e}")
            return None

    def submit_response(self, form_id: str, answers: List[Dict[str, Any]], is_anon: bool = False) -> Dict:
        """
        Submit form responses with more detailed error handling
        
        Args:
            form_id (str): ID of the form being submitted
            answers (List[Dict]): List of answer dictionaries
            is_anon (bool, optional): Whether submission is anonymous
        
        Returns:
            Dict with submission status and message
        """
        try:
            # Start transaction
            self.supabase.rpc('begin')
            
            # Create response entry
            response_insert = {
                'form_id': form_id,
                'is_anon': is_anon
            }
            response_result = self.supabase.table('responses').insert(response_insert).execute()
            
            if not response_result.data:
                return {'success': False, 'message': "Failed to create response entry"}
            
            response_id = response_result.data[0]['id']
            
            # Prepare answer entries
            answer_entries = [
                {
                    'response_id': response_id,
                    'question_id': answer['question_id'],
                    'answer_value': answer.get('answer_value'),
                    'checkbox_value': answer.get('checkbox_value')
                }
                for answer in answers
            ]
            
            # Insert answers
            self.supabase.table('response_answers').insert(answer_entries).execute()
            
            # Commit transaction
            self.supabase.rpc('commit')
            return {'success': True, 'message': "Form submitted successfully!", 'response_id': response_id}
        except Exception as e:
            # Rollback in case of error
            self.supabase.rpc('rollback')
            return {'success': False, 'message': f"Error submitting response: {str(e)}"}

def render_question(question: Dict[str, Any]) -> Dict[str, Any]:
    """
    Render a single question based on its type
    
    Args:
        question (Dict): Question details
    
    Returns:
        Dict with answer details
    """
    q_type = question['question_type']
    q_text = question['questions_text']
    q_id = question['id']
    q_required = question['is_required']
    q_options = question['options'] or []

    st.markdown(f'<style>label {{font-size: 18px !important;}} .stRadio div {{font-size: 16px !important;}}</style>', unsafe_allow_html=True)
    
    # Add required validation
    key = f"question_{q_id}"
    
    if q_type == 'short_text':
        answer = st.text_input(
            label=f"{q_text} {'*' if q_required else ''}",  # Add asterisk for required fields 
            key=key
        )
        return {
            'question_id': q_id, 
            'answer_value': answer if answer else None
        }
    
    elif q_type == 'long_text':
        answer = st.text_area(
            label=f"{q_text} {'*' if q_required else ''}",  # Add asterisk for required fields
            key=key
        )
        return {
            'question_id': q_id, 
            'answer_value': answer if answer else None
        }
    
    elif q_type == 'multiple_choice':
        answer = st.radio(
            label=f"{q_text} {'*' if q_required else ''}", 
            options=q_options, 
            key=key
        )
        return {
            'question_id': q_id, 
            'answer_value': answer if answer else None
        }
    
    elif q_type == 'dropdown':
        options_with_placeholder = ['Select an option'] + list(q_options) if not q_required else q_options
        answer = st.selectbox(
            label=f"{q_text} {'*' if q_required else ''}",
            options=options_with_placeholder, 
            key=key,
            index=0 if not q_required else None
        )
        return {
            'question_id': q_id, 
            'answer_value': answer if answer != 'Select an option' else None
        }
    
    elif q_type == 'checkbox':
        answer = st.multiselect(
            label=f"{q_text} {'*' if q_required else ''}",
            options=q_options, 
            key=key
        )
        return {
            'question_id': q_id, 
            'checkbox_value': answer if answer else None
        }
    
    elif q_type == 'number':
        answer = st.number_input(
            label=f"{q_text} {'*' if q_required else ''}",
            key=key,
            min_value=0  # Optional: prevent negative numbers if needed
        )
        return {
            'question_id': q_id, 
            'answer_value': str(answer) if answer is not None else None
        }

def render_page():
    """
    Main page for filling out forms with improved submission handling
    """
    # Initialize session state for submission status
    if 'submission_status' not in st.session_state:
        st.session_state.submission_status = None
    
    # Create service instance inside the function
    form_service = FormFillService()
    
    st.title("Fill a Form")
    
    # Form ID input
    form_id = st.text_input("Enter Form ID", help="Paste the unique form ID you want to fill")
    
    if not form_id:
        st.info("Please enter a form ID to proceed.")
        return
    
    # Fetch form details
    form_details = form_service.get_form_details(form_id)
    
    if not form_details:
        st.error("Form not found or you don't have access.")
        return
    
    # Display form metadata
    form = form_details['form']
    questions = form_details['questions']
    
    st.markdown(f"**Creator:** {form_details['creator_name']}")
    st.markdown(f"**Created on:** {form_details['formatted_date']} at {form_details['formatted_time']}")
    
    # Optional: Anonymous submission toggle if form allows
    is_anon = False
    if form['allow_anon']:
        is_anon = st.checkbox("Submit Anonymously", value=False)
    
    # Render questions
    answers = []
    for question in questions:
        answer = render_question(question)
        if answer:
            answers.append(answer)
    
    # Submit button
    if st.button("Submit Form"):
        # Validate required questions
        required_questions = [q for q in questions if q['is_required']]
        missing_answers = any(
            not next((a.get('answer_value') or a.get('checkbox_value') for a in answers if a['question_id'] == q['id']), False)
            for q in required_questions
        )
        
        if missing_answers:
            st.error("Please fill out all required questions.")
            return
        
        # Submit response
        submission_result = form_service.submit_response(
            form_id, 
            answers, 
            is_anon=is_anon
        )
        
        # Store submission status in session state
        st.session_state.submission_status = submission_result
        
        # Display submission message
        if submission_result['success']:
            st.success(submission_result['message'])
            
            # Create a placeholder for countdown
            countdown_placeholder = st.empty()
            
            # Countdown and redirect
            for i in range(3, 0, -1):
                countdown_placeholder.info(f"Redirecting to My Responses in {i} seconds...")
                time.sleep(1)
            
            # Clear the countdown placeholder
            countdown_placeholder.empty()
            
            # Set active page and rerun
            st.session_state.active_page = "My Responses"
            st.rerun()
        else:
            st.error(submission_result['message'])

def render_responses_page():
    """
    Page to show responses for a submitted form
    """
    st.title("Your Form Responses")
    
    if 'submitted_form_id' not in st.session_state or not st.session_state.submitted_form_id:
        st.error("No recent form submission found.")
        return
    
    supabase = get_supabase_client()
    form_id = st.session_state.submitted_form_id
    
    # Fetch form details
    form_details = (
        supabase.table('forms')
        .select('*')
        .eq('id', form_id)
        .execute()
    )
    
    # Fetch latest response for this form
    responses = (
        supabase.table('responses')
        .select('id, created_at')
        .eq('form_id', form_id)
        .order('created_at', desc=True)
        .limit(1)
        .execute()
    )
    
    if not responses.data:
        st.error("No responses found for this form.")
        return
    
    response = responses.data[0]
    
    # Fetch response answers
    response_answers = (
        supabase.table('response_answers')
        .select('question_id, answer_value, checkbox_value')
        .eq('response_id', response['id'])
        .execute()
    )
    
    # Fetch questions to match answers
    questions = (
        supabase.table('questions')
        .select('id, questions_text, question_type')
        .eq('form_id', form_id)
        .order('order_number')
        .execute()
    )
    
    # Create a mapping of question IDs to their text
    question_map = {q['id']: q for q in questions.data}
    
    st.header("Response Details")
    st.write(f"Submitted on: {datetime.fromisoformat(response['created_at'].replace('Z', '+00:00')).strftime('%B %d, %Y at %I:%M %p')}")
    
    for answer in response_answers.data:
        question = question_map.get(answer['question_id'], {})
        st.markdown(f"**{question.get('questions_text', 'Unknown Question')}**")
        
        # Handle different question types
        if question.get('question_type') == 'checkbox':
            st.write(answer.get('checkbox_value', 'No response'))
        else:
            st.write(answer.get('answer_value', 'No response'))
    
    # Reset form submission state
    if st.button("Back to Form Fill"):
        st.session_state.form_submitted = False
        st.session_state.submitted_form_id = None
        st.rerun()

def main():
    """
    Main application logic to handle page navigation
    """
    if 'form_submitted' not in st.session_state or not st.session_state.form_submitted:
        render_page()
    else:
        render_responses_page()

if __name__ == "__main__":
    st.set_page_config(page_title="Form Filler", page_icon="📝")
    main()