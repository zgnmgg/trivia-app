import os import environ
import unittest
import json
from flask_sqlalchemy import SQLAlchemy

from flaskr import create_app
from models import setup_db, Question, Category


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        # Define test variables and initialize app
        self.app = create_app("test")
        self.app_context = self.app.app_context()

        self.app_context.push()
        with self.app.test_client():
            self.client = self.app.test_client()
    
    def tearDown(self):
        """Executed after reach test"""
        pass

    """
    TODO
    Write at least one test for each test for successful operation and for expected errors.
    """

    """
      Endpoint: GET /categories
    """

    def test_get_categories_success(self):
        response = self.client().get('/categories')
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(len(data['categories']))
        self.assertTrue(data['total_categories'])

    def test_get_questions_success(self):
        res = self.client().get('/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['questions'])
        self.assertTrue(len(data['total_questions']))

    def test_404_invalid_page_numbers(self):
        res = self.client().get('/questions?page=5555')
        data = json.loads(res.data)

        self.assertEqual(data['error'], 404)
        self.assertEqual(data['success'], False)

    def test_delete_question_success(self):
        res = self.client().delete('questions/11')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(data['deleted'], 11)


    def test_404_delete_question(self):
        res = self.client().delete('questions/55')
        data = json.loads(res.data)

       self.assertEqual(data['success'], False)
       self.assertEqual(data['error'], 404)

    def test_create_question_success(self):
        new_question = {
            'question': 'What is the color of Chelsea FC?',
            'answer': 'Blue-White',
            'category': '6',
            'difficulty': 1,
        }

        res = self.client().post('/questions', json=new_question)
        data = json.loads(res.data)

        self.assertEqual(data['success'], True)
        self.assertTrue(data['created'])

    def test_422_cannot_create_question(self):
       bad_question = {
           'question': 'What is the short name of Counter Strike?',
           'category': '6',
           'answer':'',
           'difficulty': 2,
       }

       res = self.client().post('/questions', json=bad_question)
       data = json.loads(res.data)

       self.assertEqual(data['success'], False)
       self.assertEqual(data['error'], 422)
       self.assertEqual(data['message'], "unprocessable")

    def search_question(self):
        res = self.client().post('questions/search', json={"searchTerm": "title"})
        data = json.loads(res.data)

        self.assertEqual(data['success'], True)
        self.assertTrue(data['questions'])
        self.assertTrue(data['total_questions'])

    def test_404_invalid_search_question_input(self):
        res = self.client().post('questions/search', json={"searchTerm": "ball"})
        data = json.loads(res.data)

        self.assertEqual(data['success'], False)
        self.assertEqual(data['error'], 404)
        self.assertEqual(data['message'], "resource not found")

    def test_404_category_input_out_of_range(self):
        res = self.client().get('categories/55/questions')
        data = json.loads(res.data)

        self.assertEqual(data['error'], 404)
        self.assertEqual(data['success'], False)

    def test_quiz(self):
        input_data = {
            'previous_questions':[3, 5],
            'quiz_category': {
                'id': 5,
                'type': 'Entertainment'
            }
        }

        res = self.client().post('/quizzes', json=input_data)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['question'])

        self.assertNotEqual(data['question']['id'], 3)
        self.assertNotEqual(data['question']['id'], 5)

        self.assertEqual(data['question']['category'], 5)

# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()
