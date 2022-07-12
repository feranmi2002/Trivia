import os
import unittest
import json
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from __init__ import create_app
from models import setup_db, Question, Category


DB_USER = os.environ['user']
DB_PASSWORD = os.environ['password']
DB_NAME = os.environ['test_database_name']
DB_HOST = os.environ['database_host']
database_path = 'postgresql+psycopg2://{}:{}@{}/{}'.format(DB_USER, DB_PASSWORD, DB_HOST, DB_NAME)

class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.database_name = DB_NAME
        self.database_path = database_path
        setup_db(self.app, self.database_path)

        self.add_question = {
            'question': 'What is your name?',
            'answer': 'Faith',
            'category': '1',
            'difficulty': 1
        }

        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()
    
    def tearDown(self):
        """Executed after reach test"""
        pass

    """
    TODO
    Write at least one test for each test for successful operation and for expected errors.
    
    """
    def test_get_categories(self):
        """ Tests getting the list of all categories """
        
        res = self.client().get('/categories')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['categories'])

    def test_get_categories_failure(self):
        """ Test get categories with wrong header"""
        res = self.client().post('/categories')

        self.assertEqual(res.status_code, 405)

    def test_get_questions(self):
        """ Tests the getting of paginated questions from the database """
        res = self.client().get('/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(len(data['questions']), 10)

    def test_get_questions_failure(self):
        """ Test get questions with wrong url"""
        res = self.client().post('/questions/jfkjf')

        self.assertEqual(res.status_code, 404)

    def test_delete_question(self):
        """ Tests the delete of questions from the database """
        data = {
            'question': 'xxx',
            'answer' : 'yyy',
            'difficulty': '1',
            'category':1
        }
        oper_res = self.client().post('/questions/new', json = data)
        result_data = json.loads(oper_res.data)
        res = self.client().delete('/questions/{}'.format(result_data.get('question_id')))
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data.get('deleted_id'), str(result_data.get('question_id')))
        self.assertEqual(data['success'], True)

    def test_delete_question_fail(self):
        """ Tests the delete of questions not in the database"""
        
        res = self.client().delete('/questions/1000000000000000000')
        self.assertEqual(res.status_code, 404)

    def test_post_new_question(self):
        """ Tests adding a new question to the database"""
        res = self.client().post('/questions/new', json ={'question': 'Who is God', 'category': '1', 'answer': 'God is Light', "difficulty": "1"})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)

    def test_post_new_question_fail(self):
        """ Tests a bad request from frontend to add new question """
        question = {
           'answer': 'Faith',
            'category': '1',
            'difficulty': 1 
        }
        res = self.client().post('/questions/new', json = question)
        self.assertEqual(res.status_code, 400)

    def test_search_questions(self):
        """ Tests getting questions that contain the search term """
        res = self.client().post('/questions/search', json={'searchTerm':'the'})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(len(data['questions']) > 0)
        self.assertEqual(data['success'], True)

    def test_search_questions_fail(self):
        """ Tests searching for questions without 'searchTerm' """
        res = self.client().post('/questions/search')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 400)

    def test_get_question_by_category(self):
        """ Tests getting questions from a particular category"""
        res= self.client().get('/categories/1/questions')
        data = json.loads(res.data)
        
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(len(data['questions']) > 0)

    def test_get_question_by_category_fail(self):
        """ Tests getting questions from a category that dosen't exist"""
        res= self.client().get('/categories/1xx0/questions')
        data = json.loads(res.data)
        
        self.assertEqual(res.status_code, 404)
    
    def test_play_quiz(self):
        """ Tests getting next questions when playing the quiz """
        data = {
           'previous_questions':[],
           'quiz_category': {'type': "Science", "id": '1'}
       }
        res = self.client().post('/quizzes', json =data)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
    
    def test_play_quiz_fail(self):
        data = {
        'previous_questions': []
    } 
        res = self.client().post('/quizzes', json = data)
        self.assertEqual(res.status_code, 400)
        


# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()