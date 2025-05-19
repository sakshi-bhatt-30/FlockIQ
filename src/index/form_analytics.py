import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random
from src.config.supabase_client import get_supabase_client, get_session, is_user_authenticated

class FormAnalyticsPage:
    def __init__(self):
        if not is_user_authenticated():
            st.warning("Please log in to view form analytics")
            if st.button("Go to Login", key="login_redirect"):
                st.session_state.active_page = "Login"
            st.stop()

        self.supabase = get_supabase_client()
        self.session = get_session()
        
        # Generate dummy data for demonstration
        self.generate_dummy_data()

    def generate_dummy_data(self):
        """Generate dummy data for individual form analytics"""
        # Basic form info
        self.form_info = {
            'title': 'Customer Feedback Survey',
            'created_at': datetime.now() - timedelta(days=30),
            'last_response': datetime.now() - timedelta(hours=2),
            'total_responses': 234,
            'completion_rate': 88.5,
            'avg_time': '3m 45s'
        }
        
        # Response timeline
        dates = pd.date_range(end=datetime.now(), periods=30, freq='D')
        self.daily_responses = {
            'dates': dates,
            'responses': [random.randint(5, 15) for _ in range(30)],
            'completion_rates': [random.uniform(80, 95) for _ in range(30)]
        }
        
        # Question-specific data
        self.questions_data = {
            'Q1': {
                'text': 'How satisfied are you with our service?',
                'type': 'rating',
                'responses': {
                    '5 stars': 45,
                    '4 stars': 30,
                    '3 stars': 15,
                    '2 stars': 7,
                    '1 star': 3
                }
            },
            'Q2': {
                'text': 'Which features do you use most?',
                'type': 'multiple_choice',
                'responses': {
                    'Feature A': 120,
                    'Feature B': 89,
                    'Feature C': 67,
                    'Feature D': 45
                }
            },
            'Q3': {
                'text': 'Would you recommend us to others?',
                'type': 'boolean',
                'responses': {
                    'Yes': 85,
                    'No': 15
                }
            }
        }
        
        # Demographic data
        self.demographics = {
            'locations': {
                'USA': 45,
                'UK': 20,
                'Canada': 15,
                'Australia': 10,
                'Other': 10
            },
            'devices': {
                'Desktop': 50,
                'Mobile': 40,
                'Tablet': 10
            },
            'browsers': {
                'Chrome': 55,
                'Safari': 25,
                'Firefox': 15,
                'Other': 5
            }
        }

    def render_page(self):
        st.title("Form Analytics")
        
        # Form selector
        selected_form = st.selectbox(
            "Select Form",
            ["Customer Feedback Survey", "Employee Satisfaction", "Event Registration"],
            index=0
        )
        
        # Time period selector
        col1, col2 = st.columns([3, 1])
        with col1:
            time_period = st.selectbox(
                "Time Period",
                ["Last 7 Days", "Last 30 Days", "Last 3 Months", "All Time"],
                index=1
            )
        with col2:
            st.button("Export Data", type="primary", use_container_width=True)
        
        # Key metrics
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Responses", self.form_info['total_responses'], "+12 today")
        with col2:
            st.metric("Completion Rate", f"{self.form_info['completion_rate']}%", "+1.2%")
        with col3:
            st.metric("Avg. Response Time", self.form_info['avg_time'], "-15s")
        with col4:
            st.metric("Active Users", "45", "+5")
        
        # Create tabs for different analytics views
        tab1, tab2, tab3 = st.tabs(["Response Analytics", "Question Analysis", "Demographics"])
        
        with tab1:
            # Response timeline
            st.subheader("Response Timeline")
            response_data = pd.DataFrame({
                'Date': self.daily_responses['dates'],
                'Responses': self.daily_responses['responses'],
                'Completion Rate': self.daily_responses['completion_rates']
            })
            
            import plotly.express as px
            fig = px.line(response_data, x='Date', y=['Responses', 'Completion Rate'],
                         title='Daily Response Trend')
            st.plotly_chart(fig, use_container_width=True)
            
            # Response patterns
            col1, col2 = st.columns(2)
            with col1:
                st.subheader("Response Times")
                times = ['Morning', 'Afternoon', 'Evening', 'Night']
                values = [30, 40, 20, 10]
                fig = px.pie(values=values, names=times, title='Response Time Distribution')
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                st.subheader("Completion Funnel")
                stages = ['Viewed', 'Started', 'Halfway', 'Completed']
                values = [1000, 800, 600, 400]
                fig = px.funnel(x=values, y=stages)
                st.plotly_chart(fig, use_container_width=True)
        
        with tab2:
            st.subheader("Question Analysis")
            
            # Individual question analysis
            for q_id, question in self.questions_data.items():
                with st.expander(f"{q_id}: {question['text']}", expanded=True):
                    if question['type'] in ['rating', 'multiple_choice', 'boolean']:
                        fig = px.bar(
                            x=list(question['responses'].keys()),
                            y=list(question['responses'].values()),
                            title=f'Responses for {q_id}'
                        )
                        st.plotly_chart(fig, use_container_width=True)
        
        with tab3:
            st.subheader("Demographics")
            
            col1, col2 = st.columns(2)
            with col1:
                # Location distribution
                fig = px.pie(
                    values=list(self.demographics['locations'].values()),
                    names=list(self.demographics['locations'].keys()),
                    title='Response Distribution by Location'
                )
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                # Device distribution
                fig = px.pie(
                    values=list(self.demographics['devices'].values()),
                    names=list(self.demographics['devices'].keys()),
                    title='Response Distribution by Device'
                )
                st.plotly_chart(fig, use_container_width=True)
            
            # Browser distribution
            fig = px.bar(
                x=list(self.demographics['browsers'].keys()),
                y=list(self.demographics['browsers'].values()),
                title='Response Distribution by Browser'
            )
            st.plotly_chart(fig, use_container_width=True)

def render_page():
    page = FormAnalyticsPage()
    page.render_page()

if __name__ == "__main__":
    render_page()