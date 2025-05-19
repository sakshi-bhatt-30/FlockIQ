import streamlit as st
import uuid
from datetime import datetime
from src.config.supabase_client import get_supabase_client, get_session, is_user_authenticated
from src.services.form_service import FormService

class MyFormsPage:
    def __init__(self):
        if not is_user_authenticated():
            st.warning("Please log in to view your forms")
            if st.button("Go to Login", key="login_redirect"):
                st.session_state.active_page = "Login"
            st.stop()

        self.supabase = get_supabase_client()
        self.form_service = FormService(self.supabase)
        self.session = get_session()

    def format_datetime(self, timestamp_str):
        if not timestamp_str:
            return "Date not available", "Time not available"
        
        try:
            created_at = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
            local_tz = datetime.now().astimezone().tzinfo
            local_datetime = created_at.astimezone(local_tz)
            formatted_date = local_datetime.strftime("%B %d, %Y")
            formatted_time = local_datetime.strftime("%I:%M %p")
            return formatted_date, formatted_time
        except Exception as e:
            print(f"Error formatting datetime: {e}")
            return "Date not available", "Time not available"

    def get_user_info(self, auth_user_id):
        """
        Retrieve user information from user_info table using auth.users.id
        """
        try:
            user_query = (
                self.supabase.table('user_info')
                .select('first_name, last_name, email')
                .eq('id', auth_user_id)
                .execute()
            )
            
            if user_query.data:
                user = user_query.data[0]
                return (
                    f"{user.get('first_name', '')} {user.get('last_name', '')}".strip() or 
                    user.get('email', 'Unknown User')
                )
            return "Unknown User"
        except Exception as e:
            print(f"Error fetching user info: {e}")
            return "Unknown User"

    def get_form_responses(self, form_id):
        """
        Retrieve responses for a specific form with user details
        """
        try:
            # First get the form creator's auth user ID
            form_query = (
                self.supabase.table('forms')
                .select('id, creator_id')
                .eq('id', form_id)
                .single()
                .execute()
            )
            
            creator_id = form_query.data.get('creator_id') if form_query.data else None

            # Get all responses for the form
            responses_query = (
                self.supabase.table('responses')
                .select('id, created_at, is_anon, form_id')
                .eq('form_id', form_id)
                .execute()
            )
            
            responses = responses_query.data or []
            
            # Get questions for this form
            questions_query = (
                self.supabase.table('questions')
                .select('id, questions_text, question_type, options, is_required')
                .eq('form_id', form_id)
                .execute()
            )
            questions = {q['id']: q for q in (questions_query.data or [])}

            # Enrich responses with user details and answers
            for response in responses:
                # For non-anonymous responses, use the creator's info
                if not response['is_anon'] and creator_id:
                    response['user_name'] = self.get_user_info(creator_id)
                else:
                    response['user_name'] = "Anonymous User"

                # Get answers for this response
                answers_query = (
                    self.supabase.table('response_answers')
                    .select('question_id, answer_value, checkbox_value')
                    .eq('response_id', response['id'])
                    .execute()
                )
                
                # Format answers with question text
                formatted_answers = []
                for answer in answers_query.data or []:
                    question = questions.get(answer['question_id'])
                    if question:
                        formatted_answers.append({
                            'question_text': question['questions_text'],
                            'question_type': question['question_type'],
                            'answer_value': answer.get('answer_value'),
                            'checkbox_value': answer.get('checkbox_value')
                        })
                
                response['answers'] = formatted_answers
                response['formatted_date'], response['formatted_time'] = self.format_datetime(response['created_at'])
            
            return responses
        except Exception as e:
            st.error(f"Error fetching responses: {e}")
            return []

    def get_user_forms(self):
        """
        Retrieve forms created by the current user
        """
        try:
            response = (
                self.supabase.table('forms')
                .select('id, created_at, is_public, allow_anon')
                .eq('creator_id', self.session.user.id)
                .execute()
            )
            
            forms = response.data or []
            
            for form in forms:
                form['formatted_date'], form['formatted_time'] = self.format_datetime(form.get('created_at'))
                form['responses'] = self.get_form_responses(form['id'])
            
            return forms
        except Exception as e:
            st.error(f"Error fetching forms: {e}")
            return []

    def render_form_details_modal(self, form):
        """
        Render a modal with detailed form information and responses
        """
        st.subheader("Form Details")
        
        # Display form metadata
        st.write(f"**Form ID:** `{form['id']}`")
        st.write(f"**Created on:** {form['formatted_date']} at {form['formatted_time']}")
        st.write(f"**Public Form:** {'Yes' if form['is_public'] else 'No'}")
        st.write(f"**Allows Anonymous Responses:** {'Yes' if form['allow_anon'] else 'No'}")
        
        # Display responses
        st.subheader(f"Responses ({len(form['responses'])})")
        
        if not form['responses']:
            st.info("No responses received yet.")
        else:
            for response in form['responses']:
                with st.expander(f"Response from {response['user_name']} - {response['formatted_date']}"):
                    st.write(f"**Submitted on:** {response['formatted_date']} at {response['formatted_time']}")
                    
                    if response['is_anon']:
                        st.warning("This response was submitted anonymously")
                    
                    # Display answers
                    for answer in response['answers']:
                        st.markdown(f"**{answer['question_text']}**")
                        if answer['question_type'] == 'checkbox':
                            value = answer['checkbox_value']
                        else:
                            value = answer['answer_value']
                        st.write(value if value else 'No response')
                    st.markdown("---")

    def render_page(self):
        """
        Main page rendering method
        """
        st.title("My Forms")
        
        # Fetch user's forms
        user_forms = self.get_user_forms()
        
        if not user_forms:
            st.info("You haven't created any forms yet. Click 'Create Form' to get started!")
        else:
            for form in user_forms:
                with st.container(border=True):
                    col1, col2, col3 = st.columns([2, 2, 1])
                    
                    with col1:
                        st.write(f"Created on: {form['formatted_date']}")
                        st.write(f"Time: {form['formatted_time']}")
                    
                    with col2:
                        st.write(f"Public: {'Yes' if form['is_public'] else 'No'}")
                        st.write(f"Responses: {len(form['responses'])}")
                    
                    with col3:
                        if st.button("View Details", key=f"details_{form['id']}"):
                            self.render_form_details_modal(form)
        
        st.markdown("---")
        if st.button("Create New Form", use_container_width=True):
            st.session_state.active_page = "Create Form"

def render_page():
    page = MyFormsPage()
    page.render_page()

if __name__ == "__main__":
    render_page()