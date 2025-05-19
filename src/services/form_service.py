import uuid
from typing import Dict, List, Any
from supabase import Client

class FormService:
    def __init__(self, supabase_client: Client):
        self.supabase = supabase_client

    def create_form(self, creator_id: str, form_data: Dict[str, Any], questions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Create a new form with its associated questions
        
        Args:
            creator_id (str): ID of the user creating the form
            form_data (dict): Form details like title, description, etc.
            questions (list): List of question dictionaries
        
        Returns:
            dict: Created form details or None if creation fails
        """
        try:
            # Start a transaction to ensure atomicity
            self.supabase.rpc('begin')

            # Insert form
            form_insert = {
                'creator_id': creator_id,
                'is_public': form_data.get('is_public', False),
                'allow_anon': form_data.get('allow_anonymous', False)
            }
            form_response = self.supabase.table('forms').insert(form_insert).execute()
            
            if not form_response.data:
                raise Exception("Failed to create form")
            
            form_id = form_response.data[0]['id']

            # Insert questions for this form
            questions_to_insert = [
                {
                    'form_id': form_id,
                    'questions_text': q['text'],
                    'question_type': q['type'],
                    'is_required': q['is_required'],
                    'order_number': idx + 1,
                    'options': q['options'] if q['options'] else None
                }
                for idx, q in enumerate(questions)
            ]

            questions_response = self.supabase.table('questions').insert(questions_to_insert).execute()

            # Commit transaction
            self.supabase.rpc('commit')

            return {
                'form_id': form_id,
                'questions': questions_response.data
            }

        except Exception as e:
            # Rollback transaction in case of failure
            self.supabase.rpc('rollback')
            print(f"Error creating form: {e}")
            return None
    
    def get_published_forms(self):
        """
        Retrieve all published forms
        """
        try:
            response = self.supabase.table('forms').select('*').eq('is_public', True).execute()
            return response.data
        except Exception as e:
            print(f"Error fetching published forms: {e}")
            return []