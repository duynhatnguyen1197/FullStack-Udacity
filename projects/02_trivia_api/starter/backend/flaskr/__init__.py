import os
from flask import Flask, request, abort, jsonify,abort
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS,cross_origin
import random
import json
from models import setup_db, Question, Category
from sqlalchemy import exc,and_
QUESTIONS_PER_PAGE = 10

def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    setup_db(app)
    cors = CORS(app, resources={r"/api/*": {"origins": "*"}})
    
    @app.after_request
    def after_request(response):
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization,true')
        response.headers.add('Access-Control-Allow-Methods', 'GET,PATCH,POST,DELETE')
        return response

    """
    @TODO:
    Create an endpoint to handle GET requests
    for all available categories.
    """
    @app.route('/categories')
    def retrieve_categories():
        categories = Category.query.all()
        if not categories:
            abort(422)
        format_category = {}
        for category in categories:
            format_category[category.id] = category.type
        return jsonify({
            'categories':format_category
        })

    """
    @TODO:
    Create an endpoint to handle GET requests for questions,
    including pagination (every 10 questions).
    This endpoint should return a list of questions,
    number of total questions, current category, categories.

    TEST: At this point, when you start the application
    you should see questions and categories generated,
    ten questions per page and pagination at the bottom of the screen for three pages.
    Clicking on the page numbers should update the questions.
    """
    @app.route('/questions')
    def retrieve_questions():
        page = request.args.get('page', 1, type=int)
        start = (page - 1) * QUESTIONS_PER_PAGE
        end = start + QUESTIONS_PER_PAGE
        questions = Question.query.order_by(Question.id).all()
        categories = Category.query.all()
        format_questions = [question.format() for question in questions]
        format_categories = {}
        for category in categories:
            format_categories[category.id] = category.type
        num_page = calculate_pagination(len(questions))
        if num_page < page:
            abort(400)
        else:
            return jsonify({
              'categories': format_categories,
              'total_questions':len(questions),
              'questions': format_questions[start:end]
            })
        
    def calculate_pagination(length):
        if length % 10 == 0 :
            num_page = length/10
        else:
            num_page = length/10 + 1
        return num_page
    
    """
    @TODO:
    Create an endpoint to DELETE question using a question ID.

    TEST: When you click the trash icon next to a question, the question will be removed.
    This removal will persist in the database and when you refresh the page.
    """
    @app.route('/questions/<int:question_id>', methods = ['DELETE'])
    def delete_question(question_id):
        question = Question.query.get(question_id)
        if question is None:
            abort(400)
        else:
            question.delete()
            return jsonify({
                'success':True,
                'question_id':question_id,
                'message': 'Question['+str(question_id)+'] is deleted'
            })
    
        
    """
    @TODO:
    Create an endpoint to POST a new question,
    which will require the question and answer text,
    category, and difficulty score.

    TEST: When you submit a question on the "Add" tab,
    the form will clear and the question will appear at the end of the last page
    of the questions list in the "List" tab.
    """
    @app.route('/questions', methods = ['POST'])
    def create_question():
        try:
            receive_data = request.get_json()
            print(receive_data)
            question = json.loads( json.dumps(receive_data) , object_hook=lambda d: Question(**d))
            question.insert()
            return jsonify({
                "success":True,
                "question":question.format(),
                "message": "New question has been added"
            })
        except exc.SQLAlchemyError as e:
            return jsonify({
                "message":str(e),
                "error":True
            })
        
    """
    @TODO:
    Create a POST endpoint to get questions based on a search term.
    It should return any questions for whom the search term
    is a substring of the question.

    TEST: Search by any phrase. The questions list will update to include
    only question that include that string within their question.
    Try using the word "title" to start.
    """
    @app.route('/questions/search', methods = ["POST"])
    def search_question():
        receive_data = request.get_json()
        search_results = Question.query.filter(Question.question.ilike("%"+receive_data['searchTerm']+"%")).all()
        format_results = [result.format() for result in search_results]
        return jsonify({
            "questions":format_results,
            "totalQuestions":len(format_results)
        })
    """
    @TODO:
    Create a GET endpoint to get questions based on category.

    TEST: In the "List" tab / main screen, clicking on one of the
    categories in the left column will cause only questions of that
    category to be shown.
    """
    @app.route('/categories/<int:category_id>/questions')
    @cross_origin()
    def categorize_questions(category_id):
        category = Category.query.get(category_id)
        if category is None:
            abort(400)
        else:
            questions = Question.query.filter(Question.category == str(category_id)).all()
            format_questions = [question.format() for question in questions]
            return jsonify({
                'questions':format_questions,
                'total_questions':len(format_questions),
                'current_category':category.type
            })
    """
    @TODO:
    Create a POST endpoint to get questions to play the quiz.
    This endpoint should take category and previous question parameters
    and return a random questions within the given category,
    if provided, and that is not one of the previous questions.

    TEST: In the "Play" tab, after a user selects "All" or a category,
    one question at a time is displayed, the user is allowed to answer
    and shown whether they were correct or not.
    """
    @app.route('/quizzes' , methods = ['POST'])
    def play_game():
        receive_data = request.get_json()
        quiz_category = receive_data['quiz_category']
        previous_questions = receive_data['previous_questions']
        if int(quiz_category['id']) == 0 :
            questions = Question.query.filter(Question.id.notin_(previous_questions)).all()
        else:
            questions = Question.query.filter(and_(
                Question.id.notin_(previous_questions),Question.category == str(quiz_category['id']) 
            )).all()
        new_question = random.choice(questions) if len(questions)!=0 else None
        if new_question is None:
            return jsonify({
                "success":False,
                "message":"End of Quizz"
            })
        else:
            return jsonify({
                "question": new_question.format()
            })
    """
    @TODO:
    Create error handlers for all expected errors
    including 404 and 422.
    """
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            "success": False, 
            "error": 404,
            "message": "Not Found"
            }), 404
    
    @app.errorhandler(422)
    def unresponse(error):
        return jsonify({
            "success": False, 
            "error": 422,
            "message": "Entity Not Response"
            }), 422
    
    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({
            "success": False, 
            "error": 400,
            "message": "Bad Request"
            }), 400
    
    @app.errorhandler(500)
    def internal_error(error):
        return jsonify({
            "success": False, 
            "error": 500,
            "message": "Internal Server Error"
            }), 500
    return app
