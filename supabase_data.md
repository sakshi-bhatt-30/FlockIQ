PUBLIC TABLE SCHEMAS

| table_name       | column_name    | data_type                   | is_nullable | column_default    |
| ---------------- | -------------- | --------------------------- | ----------- | ----------------- |
| forms            | id             | uuid                        | NO          | gen_random_uuid() |
| forms            | created_at     | timestamp with time zone    | NO          | now()             |
| forms            | creator_id     | uuid                        | NO          |                   |
| forms            | is_public      | boolean                     | YES         | false             |
| forms            | allow_anon     | boolean                     | YES         | false             |
| forms            | updated_at     | timestamp without time zone | YES         | now()             |
| questions        | id             | uuid                        | NO          | gen_random_uuid() |
| questions        | created_at     | timestamp with time zone    | NO          | now()             |
| questions        | form_id        | uuid                        | NO          | gen_random_uuid() |
| questions        | questions_text | text                        | NO          |                   |
| questions        | is_required    | boolean                     | YES         | false             |
| questions        | order_number   | smallint                    | NO          |                   |
| questions        | options        | ARRAY                       | YES         |                   |
| questions        | question_type  | text                        | NO          |                   |
| response_answers | id             | uuid                        | NO          | gen_random_uuid() |
| response_answers | created_at     | timestamp with time zone    | NO          | now()             |
| response_answers | response_id    | uuid                        | NO          |                   |
| response_answers | question_id    | uuid                        | NO          |                   |
| response_answers | answer_value   | text                        | YES         |                   |
| response_answers | checkbox_value | ARRAY                       | YES         |                   |
| responses        | id             | uuid                        | NO          | gen_random_uuid() |
| responses        | created_at     | timestamp with time zone    | NO          | now()             |
| responses        | form_id        | uuid                        | NO          | gen_random_uuid() |
| responses        | is_anon        | boolean                     | YES         | false             |
| user_info        | id             | uuid                        | NO          |                   |
| user_info        | created_at     | timestamp with time zone    | NO          | now()             |
| user_info        | first_name     | text                        | YES         |                   |
| user_info        | last_name      | text                        | YES         |                   |
| user_info        | email          | character varying           | YES         |                   |
| user_info        | phone          | text                        | YES         |                   |
| user_info        | organization   | text                        | YES         |                   |
| user_info        | bio            | text                        | YES         |                   |

REFERENCES

| table_schema | constraint_name                           | table_name                 | column_name     | foreign_table_name   | foreign_column_name |
| ------------ | ----------------------------------------- | -------------------------- | --------------- | -------------------- | ------------------- |
| public       | user_info_id_fkey                         | user_info                  | id              | users                | id                  |
| public       | forms_creator_id_fkey                     | forms                      | creator_id      | users                | id                  |
| public       | questions_form_id_fkey                    | questions                  | form_id         | forms                | id                  |
| public       | responses_form_id_fkey                    | responses                  | form_id         | forms                | id                  |
| public       | response_answers_question_id_fkey         | response_answers           | question_id     | questions            | id                  |
| public       | response_answers_response_id_fkey         | response_answers           | response_id     | responses            | id                  |

POLICIES (RLS temporarily disabled)

[
  {
    "schemaname": "public",
    "tablename": "user_info",
    "polname": "Enable read access for all users",
    "cmd": "SELECT",
    "condition": "true"
  },
  {
    "schemaname": "public",
    "tablename": "user_info",
    "polname": "Enable insert for authenticated users only",
    "cmd": "INSERT",
    "condition": null
  },
  {
    "schemaname": "public",
    "tablename": "user_info",
    "polname": "Enable delete for users based on user_id",
    "cmd": "DELETE",
    "condition": "(( SELECT auth.uid() AS uid) = id)"
  },
  {
    "schemaname": "public",
    "tablename": "user_info",
    "polname": "Enable insert for users based on user_id",
    "cmd": "INSERT",
    "condition": null
  },
  {
    "schemaname": "public",
    "tablename": "user_info",
    "polname": "Enable update for users based on id",
    "cmd": "UPDATE",
    "condition": "(auth.uid() = id)"
  },
  {
    "schemaname": "public",
    "tablename": "forms",
    "polname": "Users can create their own forms",
    "cmd": "INSERT",
    "condition": null
  },
  {
    "schemaname": "public",
    "tablename": "forms",
    "polname": "Users can view their own forms",
    "cmd": "SELECT",
    "condition": "(auth.uid() = creator_id)"
  },
  {
    "schemaname": "public",
    "tablename": "forms",
    "polname": "Users can update their own forms",
    "cmd": "UPDATE",
    "condition": "(auth.uid() = creator_id)"
  },
  {
    "schemaname": "public",
    "tablename": "forms",
    "polname": "Users can delete their own forms",
    "cmd": "DELETE",
    "condition": "(auth.uid() = creator_id)"
  },
  {
    "schemaname": "public",
    "tablename": "questions",
    "polname": "Users can view questions for their forms",
    "cmd": "SELECT",
    "condition": "(EXISTS ( SELECT 1\n   FROM forms\n  WHERE ((forms.id = questions.form_id) AND (forms.creator_id = auth.uid()))))"
  },
  {
    "schemaname": "public",
    "tablename": "questions",
    "polname": "Users can add questions to their forms",
    "cmd": "INSERT",
    "condition": null
  },
  {
    "schemaname": "public",
    "tablename": "questions",
    "polname": "Users can update questions in their forms",
    "cmd": "UPDATE",
    "condition": "(EXISTS ( SELECT 1\n   FROM forms\n  WHERE ((forms.id = questions.form_id) AND (forms.creator_id = auth.uid()))))"
  },
  {
    "schemaname": "public",
    "tablename": "questions",
    "polname": "Users can delete questions from their forms",
    "cmd": "DELETE",
    "condition": "(EXISTS ( SELECT 1\n   FROM forms\n  WHERE ((forms.id = questions.form_id) AND (forms.creator_id = auth.uid()))))"
  },
  {
    "schemaname": "public",
    "tablename": "responses",
    "polname": "Users can create responses for public or own forms",
    "cmd": "INSERT",
    "condition": null
  },
  {
    "schemaname": "public",
    "tablename": "responses",
    "polname": "Users can view responses for their forms",
    "cmd": "SELECT",
    "condition": "(EXISTS ( SELECT 1\n   FROM forms\n  WHERE ((forms.id = responses.form_id) AND (forms.creator_id = auth.uid()))))"
  },
  {
    "schemaname": "public",
    "tablename": "response_answers",
    "polname": "Users can view response answers for their forms",
    "cmd": "SELECT",
    "condition": "(EXISTS ( SELECT 1\n   FROM (responses r\n     JOIN forms f ON ((r.form_id = f.id)))\n  WHERE ((r.id = response_answers.response_id) AND (f.creator_id = auth.uid()))))"
  }
]


SQL queries to retrieve the data above
SELECT 
    table_name, 
    column_name, 
    data_type, 
    is_nullable, 
    column_default
FROM information_schema.columns
WHERE table_schema = 'public'
ORDER BY table_name, ordinal_position;

select
  schemaname,
  tablename,
  policyname as polname,
  cmd,
  qual as condition
from
  pg_policies
where
  schemaname = 'public';

  SELECT 
    tc.table_schema, 
    tc.constraint_name, 
    tc.table_name, 
    kcu.column_name, 
    ccu.table_name AS foreign_table_name,
    ccu.column_name AS foreign_column_name 
FROM 
    information_schema.table_constraints AS tc 
    JOIN information_schema.key_column_usage AS kcu
      ON tc.constraint_name = kcu.constraint_name
    JOIN information_schema.constraint_column_usage AS ccu
      ON ccu.constraint_name = tc.constraint_name
WHERE constraint_type = 'FOREIGN KEY';