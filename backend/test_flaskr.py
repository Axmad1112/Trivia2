import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy
from flaskr import create_app
from models import setup_db, Question, Category
from settings import DB_NAME, DB_USER, DB_PASSWORD

class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.database_name = "trivia"
        self.database_path = "postgresql://{}:{}@{}/{}".format(DB_USER,DB_PASSWORD,'localhost:5432', DB_NAME)
        setup_db(self.app, self.database_path)


        self.new_question = {
            'question': "What is this test?",
            'answer': "Nothing",
            'difficulty': 1,
            'category': 1}

        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            self.db.create_all()
    
    def tearDown(self):
        """Executed after reach test"""
        pass

    def test_get_categories(self):
        res = self.client().get("/categories")
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(len(data['categories']))
    
    
    def test_get_paginated_question(self):
        res = self.client().get('/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['total_questions'])
        self.assertTrue(len(data['categories']))
        self.assertTrue(len(data['questions']))

    def test_404_sent_requesting_beyond_valid_page(self):
        res = self.client().get('/books?page=1000')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Resource not found')

    def test_delete_question_success(self):
        question = Question.query.order_by(Question.id.desc()).first()
        question_id = question.id

        response = self.client().delete('/questions/{}'.format(question_id))
        data = json.loads(response.data)

        question = Question.query.get(question_id)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertIsNone(question)

    def test_delete_question_fail(self):
        res = self.client().delete('/questions')
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 405)
        self.assertEqual(data['success'], False)

    def test_422_question_does_not_exist(self):
        res = self.client().delete("/questions/1000")
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 422)
        self.assertFalse(data['success'])
        self.assertEqual(data['message'], 'Unprocessable entity')
        self.assertEqual(data['error'], 422)

    def test_create_question(self):
        res = self.client().post('/questions', json=self.new_question)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['success'])
    
    def test_405_not_allowed_create_question(self):
        res = self.client().post('/questions/5', json=self.new_question)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 405)
        self.assertFalse(data['success'])
        self.assertEqual(data['message'], "Method not allowed")
        self.assertEqual(data['error'], 405)

    def test_search_for_question(self):
        res = self.client().post('/questions', json={"searchTerm":"What"})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(len(data['questions']))
        self.assertTrue(data['total_questions'])
    

    def test_search_for_not_exist_question(self):
        res = self.client().post('/questions', json={"searchTerm":"asudauifuihaufhaiouhfaohfuihauifhuidhfadfbafdnljif"})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(len(data['questions']), 0)
        self.assertEqual(data['total_questions'], 0)
    

    def test_405_not_allowed_search_for_question(self):
        res = self.client().post('/questions/45', json={"searchTerm":"What"})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 405)
        self.assertFalse(data['success'])
        self.assertEqual(data['message'], "Method not allowed")
        self.assertEqual(data['error'], 405)

    def test_get_questions_by_category(self):
        res = self.client().get('/categories/1/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(len(data['questions']))
        self.assertTrue(data['total_questions'])
        self.assertTrue(data['current_category'])
    
    def test_404_sent_requesting_beyond_valid_category(self):
        res = self.client().get('/categories/1000/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Resource not found')


    def test_get_next_question(self):
        res = self.client().post('/quizzes', json={
            "previous_questions":[],
            "quiz_category": {"id":0, "type":"All"}
            })
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertNotEqual(data['question'], None)

    def test_404_sent_requesting_beyond_valid_quiz_category(self):
        res = self.client().post('/quizzes', json={
            'previous_questions':[],
            'quiz_category': {'id':1000, 'type':"test"}
            })
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 422)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Unprocessable entity')


if __name__ == "__main__":
    unittest.main()