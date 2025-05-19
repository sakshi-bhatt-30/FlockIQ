import streamlit as st
import uuid
from src.config.supabase_client import get_supabase_client, get_session, is_user_authenticated

class FormTemplatesPage:
    def __init__(self):
        # Ensure user is authenticated
        if not is_user_authenticated():
            st.warning("Please log in to access form templates")
            if st.button("Go to Login", use_container_width=True):
                st.session_state.active_page = "Login"
                st.rerun()
            st.stop()

        self.supabase = get_supabase_client()
        self.session = get_session()

    def customer_satisfaction_template(self):
        """
        Customer Satisfaction Survey Template
        """
        return {
            'title': 'Customer Satisfaction Survey',
            'description': 'Help us improve our products and services by sharing your feedback.',
            'is_public': True,
            'allow_anonymous': True,
            'questions': [
                {
                    'text': 'How satisfied are you with our product/service?',
                    'type': 'multiple_choice',
                    'is_required': True,
                    'options': ['Very Satisfied', 'Satisfied', 'Neutral', 'Dissatisfied', 'Very Dissatisfied'],
                    'id': str(uuid.uuid4())
                },
                {
                    'text': 'What features do you like most about our product?',
                    'type': 'checkbox',
                    'is_required': False,
                    'options': ['Ease of Use', 'Performance', 'Design', 'Customer Support', 'Price'],
                    'id': str(uuid.uuid4())
                },
                {
                    'text': 'Please provide detailed feedback about your experience',
                    'type': 'long_text',
                    'is_required': False,
                    'id': str(uuid.uuid4())
                },
                {
                    'text': 'How likely are you to recommend our product to others?',
                    'type': 'multiple_choice',
                    'is_required': True,
                    'options': ['Very Likely', 'Likely', 'Neutral', 'Unlikely', 'Very Unlikely'],
                    'id': str(uuid.uuid4())
                },
                {
                    'text': 'Your overall rating',
                    'type': 'number',
                    'is_required': True,
                    'id': str(uuid.uuid4())
                }
            ]
        }

    def employee_feedback_template(self):
        """
        Employee Feedback Survey Template
        """
        return {
            'title': 'Employee Engagement Survey',
            'description': 'We value your input to create a better workplace environment.',
            'is_public': False,
            'allow_anonymous': True,
            'questions': [
                {
                    'text': 'How engaged do you feel in your current role?',
                    'type': 'multiple_choice',
                    'is_required': True,
                    'options': ['Very Engaged', 'Engaged', 'Neutral', 'Disengaged', 'Very Disengaged'],
                    'id': str(uuid.uuid4())
                },
                {
                    'text': 'What aspects of work do you enjoy most?',
                    'type': 'checkbox',
                    'is_required': False,
                    'options': ['Team Collaboration', 'Professional Growth', 'Work-Life Balance', 'Company Culture', 'Compensation'],
                    'id': str(uuid.uuid4())
                },
                {
                    'text': 'Suggestions for improvement',
                    'type': 'long_text',
                    'is_required': False,
                    'id': str(uuid.uuid4())
                },
                {
                    'text': 'Rate your manager\'s leadership',
                    'type': 'multiple_choice',
                    'is_required': True,
                    'options': ['Excellent', 'Good', 'Average', 'Poor', 'Very Poor'],
                    'id': str(uuid.uuid4())
                },
                {
                    'text': 'How long have you been with the company?',
                    'type': 'multiple_choice',
                    'is_required': True,
                    'options': ['Less than 1 year', '1-2 years', '3-5 years', 'More than 5 years'],
                    'id': str(uuid.uuid4())
                }
            ]
        }

    def event_feedback_template(self):
        """
        Event Feedback Survey Template
        """
        return {
            'title': 'Event Feedback Survey',
            'description': 'Help us improve our future events by sharing your experience.',
            'is_public': True,
            'allow_anonymous': True,
            'questions': [
                {
                    'text': 'How would you rate the overall event?',
                    'type': 'multiple_choice',
                    'is_required': True,
                    'options': ['Excellent', 'Good', 'Average', 'Poor', 'Very Poor'],
                    'id': str(uuid.uuid4())
                },
                {
                    'text': 'What did you enjoy most about the event?',
                    'type': 'checkbox',
                    'is_required': False,
                    'options': ['Speakers', 'Content', 'Networking', 'Venue', 'Organization'],
                    'id': str(uuid.uuid4())
                },
                {
                    'text': 'Detailed feedback and suggestions',
                    'type': 'long_text',
                    'is_required': False,
                    'id': str(uuid.uuid4())
                },
                {
                    'text': 'Would you attend similar events in the future?',
                    'type': 'multiple_choice',
                    'is_required': True,
                    'options': ['Definitely', 'Probably', 'Maybe', 'Probably Not', 'Definitely Not'],
                    'id': str(uuid.uuid4())
                }
            ]
        }

    def render_template_details(self, template):
        """
        Render details of a specific template
        """
        st.subheader(template['title'])
        st.write(template['description'])
        
        st.markdown("#### Questions:")
        for idx, question in enumerate(template['questions'], 1):
            with st.expander(f"Question {idx}"):
                st.write(f"**Text:** {question['text']}")
                # Fix: use 'type' instead of 'question_type'
                st.write(f"**Type:** {question['type']}")
                st.write(f"**Required:** {'Yes' if question['is_required'] else 'No'}")
                if 'options' in question and question.get('options'):
                    st.write(f"**Options:** {', '.join(question['options'])}")

    def render_page(self):
        """
        Main page rendering method
        """
        st.title("Form Templates")
        st.write("Get started quickly with our pre-designed form templates!")

        # Define templates
        templates = [
            self.customer_satisfaction_template(),
            self.employee_feedback_template(),
            self.event_feedback_template()
        ]

        # Create columns for templates
        cols = st.columns(3)

        # Render template cards
        for idx, template in enumerate(templates):
            with cols[idx]:
                # Add a container with a border
                with st.container(border=True):
                    st.subheader(template['title'])
                    st.write(template['description'])
                    
                    if st.button(f"View Details", key=f"template_{idx}"):
                        self.render_template_details(template)
                    
                    if st.button(f"Use Template", key=f"use_template_{idx}"):
                        # Store template in session state
                        st.session_state.template_to_use = template
                        st.session_state.active_page = "Create Form"
                        st.rerun()

        # Placeholder for future templates
        st.markdown("---")
        st.subheader("More Templates Coming Soon!")
        
        template_ideas = [
            "Market Research Survey",
            "Product Feedback Form",
            "Job Application Template",
            "Educational Evaluation",
            "Health & Wellness Questionnaire"
        ]
        
        # Create a grid of placeholders
        grid_cols = st.columns(3)
        for idx, idea in enumerate(template_ideas):
            with grid_cols[idx % 3]:
                st.info(idea)

def render_page():
    """
    Entry point for Streamlit page rendering
    """
    page = FormTemplatesPage()
    page.render_page()

# This allows the page to be imported and used in the main app
if __name__ == "__main__":
    render_page()