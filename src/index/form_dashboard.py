import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import random
from src.config.supabase_client import get_supabase_client, get_session, is_user_authenticated

class FormsDashboardPage:
    def __init__(self):
        if not is_user_authenticated():
            st.warning("Please log in to view your forms dashboard")
            if st.button("Go to Login", key="login_redirect"):
                st.session_state.active_page = "Login"
            st.stop()

        self.supabase = get_supabase_client()
        self.session = get_session()
        
        # Generate dummy data for demonstration
        self.generate_dummy_data()

    def generate_dummy_data(self):
        """Generate dummy data for dashboard demonstration"""
        # Overall forms data
        self.total_forms = 15
        self.active_forms = 12
        self.total_responses = 847
        self.response_rate = 76.5
        
        # Monthly data (last 6 months)
        months = pd.date_range(end=datetime.now(), periods=6, freq='M')
        self.monthly_data = {
            'dates': months,
            'responses': [random.randint(80, 150) for _ in range(6)],
            'completion_rates': [random.uniform(70, 95) for _ in range(6)]
        }
        
        # Form categories
        self.form_categories = {
            'Feedback': 5,
            'Survey': 4,
            'Registration': 3,
            'Quiz': 2,
            'Other': 1
        }
        
        # Response times
        self.response_times = {
            '<1 min': 15,
            '1-2 min': 35,
            '2-5 min': 30,
            '5-10 min': 15,
            '>10 min': 5
        }
        
        # Device distribution
        self.device_data = {
            'Desktop': 45,
            'Mobile': 40,
            'Tablet': 15
        }
        
        # Recent activity
        self.recent_activity = [
            {'time': datetime.now() - timedelta(minutes=30), 'action': 'New response received', 'form': 'Customer Feedback'},
            {'time': datetime.now() - timedelta(hours=2), 'action': 'Form created', 'form': 'Employee Survey'},
            {'time': datetime.now() - timedelta(hours=5), 'action': 'Form edited', 'form': 'Product Registration'},
            {'time': datetime.now() - timedelta(hours=8), 'action': 'New response received', 'form': 'Event Registration'}
        ]

    def render_page(self):
        st.title("Forms Dashboard")
        
        # Time period selector
        time_period = st.selectbox(
            "Time Period",
            ["Last 7 Days", "Last 30 Days", "Last 6 Months", "All Time"],
            index=2
        )
        
        # Key metrics in columns
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Forms", self.total_forms, "+2 this month")
        with col2:
            st.metric("Active Forms", self.active_forms, "-1 this month")
        with col3:
            st.metric("Total Responses", self.total_responses, "+125 this month")
        with col4:
            st.metric("Avg. Response Rate", f"{self.response_rate}%", "+2.3%")
        
        # Response trend and completion rate
        st.subheader("Response Trends")
        response_data = pd.DataFrame({
            'Date': self.monthly_data['dates'],
            'Responses': self.monthly_data['responses'],
            'Completion Rate': self.monthly_data['completion_rates']
        })
        
        # Create tabs for different visualizations
        tab1, tab2, tab3 = st.tabs(["Response Analytics", "Form Distribution", "Recent Activity"])
        
        with tab1:
            col1, col2 = st.columns(2)
            with col1:
                st.subheader("Monthly Responses")
                import plotly.express as px
                fig = px.line(response_data, x='Date', y='Responses',
                            title='Monthly Response Trend')
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                st.subheader("Response Times")
                fig = px.pie(
                    values=list(self.response_times.values()),
                    names=list(self.response_times.keys()),
                    title='Response Time Distribution'
                )
                st.plotly_chart(fig, use_container_width=True)
        
        with tab2:
            col1, col2 = st.columns(2)
            with col1:
                st.subheader("Form Categories")
                fig = px.bar(
                    x=list(self.form_categories.keys()),
                    y=list(self.form_categories.values()),
                    title='Forms by Category'
                )
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                st.subheader("Device Distribution")
                fig = px.pie(
                    values=list(self.device_data.values()),
                    names=list(self.device_data.keys()),
                    title='Responses by Device'
                )
                st.plotly_chart(fig, use_container_width=True)
        
        with tab3:
            st.subheader("Recent Activity")
            for activity in self.recent_activity:
                with st.container(border=True):
                    st.text(f"{activity['time'].strftime('%I:%M %p')} - {activity['action']}")
                    st.caption(f"Form: {activity['form']}")

def render_page():
    page = FormsDashboardPage()
    page.render_page()

if __name__ == "__main__":
    render_page()