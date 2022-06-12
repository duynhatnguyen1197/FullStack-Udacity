import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv
from flaskr import create_app
from models import setup_db, Question, Category

load_dotenv()
user_name = os.environ.get('USER')
password = os.environ.get('PASSWORD')
database_name = os.environ.get('TEST_DATABASE')

class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.database_name = database_name
        self.database_path ="postgresql://{}:{}@{}/{}".format(user_name, password,'localhost:5432', self.database_name)
        setup_db(self.app, self.database_path)

        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()
    
    def tearDown(self):
        """Executed after reach test"""
        pass
    
    def test_get_categories(self):
        res = self.client().get("/categories")
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data["categories"])
        
    
        
    def test_get_paginated_questions(self):
        res = self.client().get("/questions")
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data["questions"])
        self.assertTrue(data["categories"])
        self.assertTrue(data["total_questions"])
    
    def test_sent_request_beyond_valid_page(self):
        res = self.client().get("/questions?page=1000")
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 400)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "Bad Request")
    
    def test_get_categorized_questions(self):
        res = self.client().get("/categories/1/questions")
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data["questions"])
        self.assertTrue(data["total_questions"])
        self.assertTrue(len(data["current_category"]))
    
    def test_get_categorized_questions_beyond_category(self):
        res = self.client().get("/categories/1000/questions")
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 400)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "Bad Request")
    
    def test_search_question(self):
        res = self.client().post("/questions/search",json={"searchTerm":"a"})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data["questions"])
        self.assertTrue(data["totalQuestions"])
    
    def test_404_search_question(self):
        res = self.client().post("/questions/search",json={"searchTerm":"abcxyz"})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["totalQuestions"],0)
    
    def test_create_question(self):
        res = self.client().post("/questions",json={
            'question': 'Is Duy handsome', 
            'answer': 'Yes', 
            'difficulty': '5', 
            'category': '2'})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data["success"])
        self.assertTrue(data["question"])
        self.assertTrue(data["message"])
        
    def test_create_question_fail(self):
        res = self.client().post("/questions",json={
            'question': '', 
            'answer': '', 
            'difficulty': '', 
            'category': ''})
        data = json.loads(res.data)
        
        self.assertTrue(data["message"])
        self.assertEqual(data["error"],True)
        
    def test_delete_question(self):
        res = self.client().delete("/questions/6")
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertTrue(data["question_id"])
        self.assertTrue(data["message"])
    
    def test_delete_question_fail(self):
        res = self.client().delete("/questions/1000")
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 400)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "Bad Request")
    
    def test_quizz(self):
        res = self.client().post("/quizzes",json={
            'previous_questions': [20, 21],
            'quiz_category':{"type":"Science","id":"1"}
        })
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertTrue(data["question"])
    
    def test_quizz_fail(self):
        questions = Question.query.filter(Question.category == 1).all()
        list_id = []
        for question in questions:
            list_id.append(question.id)
        res = self.client().post("/quizzes",json={
            'previous_questions': list_id,
            'quiz_category':{"type":"Science","id":"1"}
        })
        data = json.loads(res.data)

        self.assertEqual(data["success"], False)
        self.assertTrue(data["message"])
        
    def test_get_categories_fail(self):
        delete_categories = Category.query.delete()
        res = self.client().get("/categories")
        data = json.loads(res.data)
        
        self.assertEqual(res.status_code, 422)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "Entity Not Response")
    
    

# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()