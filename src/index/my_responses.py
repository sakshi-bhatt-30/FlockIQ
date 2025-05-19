import streamlit as st
from src.config.supabase_client import get_supabase_client
from datetime import datetime

class MyResponsesPage:
    def __init__(self):
        """
        Initialize Supabase client and set up the page
        """
        self.supabase = get_supabase_client()
    
    def get_user_responses(self, user_id=None):
        """
        Retrieve all responses for a given user
        
        Args:
            user_id (str, optional): ID of the user. If None, use current logged-in user.
        
        Returns:
            List of responses with form and answer details
        """
        try:
            # Fetch responses for the user
            responses_query = (
                self.supabase.table('responses')
                .select('id, form_id, created_at, is_anon')
                .execute()
            )
            
            responses = responses_query.data or []
            
            # Enrich responses with form details
            for response in responses:
                # Get form details
                form_query = (
                    self.supabase.table('forms')
                    .select('id, creator_id')
                    .eq('id', response['form_id'])
                    .execute()
                )
                
                if form_query.data:
                    form = form_query.data[0]
                    response['form'] = form
                    
                    # Get creator details
                    creator_query = (
                        self.supabase.table('user_info')
                        .select('first_name, last_name, email')
                        .eq('id', form['creator_id'])
                        .execute()
                    )
                    
                    if creator_query.data:
                        creator = creator_query.data[0]
                        response['creator_name'] = (
                            f"{creator.get('first_name', '')} {creator.get('last_name', '')}".strip() or 
                            creator.get('email', 'Unknown Creator')
                        )
                
                # Get response answers
                answers_query = (
                    self.supabase.table('response_answers')
                    .select('question_id, answer_value, checkbox_value')
                    .eq('response_id', response['id'])
                    .execute()
                )
                
                # Get questions for this form
                questions_query = (
                    self.supabase.table('questions')
                    .select('id, questions_text, question_type')
                    .eq('form_id', response['form_id'])
                    .order('order_number')
                    .execute()
                )
                
                response['answers'] = answers_query.data or []
                response['questions'] = {q['id']: q for q in (questions_query.data or [])}
                
                # Format timestamp
                created_at = datetime.fromisoformat(response['created_at'].replace('Z', '+00:00'))
                response['formatted_date'] = created_at.strftime("%B %d, %Y")
                response['formatted_time'] = created_at.strftime("%I:%M %p")
            
            return responses
        
        except Exception as e:
            st.error(f"Error fetching responses: {e}")
            return []

def render_page():
    """
    Render the My Responses page
    """
    st.title("My Responses")
    
    # Create an instance of MyResponsesPage
    responses_service = MyResponsesPage()
    
    # Fetch user responses
    responses = responses_service.get_user_responses()
    
    if not responses:
        st.info("You haven't submitted any form responses yet.")
        return
    
    # Display responses
    for response in responses:
        # Create an expandable section for each response
        with st.expander(f"Form Response - {response['formatted_date']} at {response['formatted_time']}"):
            # Display form creator info
            st.markdown(f"**Created by:** {response.get('creator_name', 'Unknown Creator')}")
            st.markdown(f"**Submitted on:** {response['formatted_date']} at {response['formatted_time']}")
            
            # Check if submission was anonymous
            if response.get('is_anon'):
                st.warning("This response was submitted anonymously")
            
            # Display answers
            st.subheader("Response Details")
            for answer in response['answers']:
                # Find corresponding question
                question = response['questions'].get(answer['question_id'], {})
                
                st.markdown(f"**{question.get('questions_text', 'Unknown Question')}**")
                
                # Handle different question types
                if question.get('question_type') == 'checkbox':
                    value = answer.get('checkbox_value', 'No response')
                    st.write(value if value else 'No response')
                else:
                    value = answer.get('answer_value', 'No response')
                    st.write(value if value else 'No response')
            
            # Add a divider between responses
            st.markdown("---")

# This allows the page to be imported and used in the main app
if __name__ == "__main__":
    st.set_page_config(page_title="My Responses", page_icon="📋")
    render_page()