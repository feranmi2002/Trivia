import os
from flask import Flask, request, abort, jsonify
from flask_cors import CORS, cross_origin
import random
from sqlalchemy import func, create_engine
from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10


def create_app(test_config=None):
    # Create app
    app = Flask(__name__)
    setup_db(app)

    CORS(app, resources={r"/*": {"origins": "*"}})

    @app.after_request
    def after_request(response):
        response.headers.add(
            'Access-Control-Allow-Headers',
            'Content-Type, Authorization')
        response.headers.add(
            'Access-Control-Allow-Methods',
            'GET, POST, PATCH, DELETE, OPTIONS')
        return response

    @cross_origin()
    @app.route('/categories', methods=['GET'])
    def getCategories():
        try:
            # Get categories
            _categories = Category.query.all()
            categories = {
                "1": _categories[0].type,
                "2": _categories[1].type,
                "3": _categories[2].type,
                "4": _categories[3].type,
                "5": _categories[4].type,
                "6": _categories[5].type
            }
            return jsonify({
                'categories': categories,
                'success': True
            })
        except():
            abort(500)

    @cross_origin()
    @app.route('/questions', methods=['GET'])
    def getQuestions():
        try:
            # Get questions and paginate
            try:
                # Get request args
                page = request.args.get('page', 1, type=int)
            except():
                abort(400)
            start = (page - 1) * QUESTIONS_PER_PAGE
            end = start + QUESTIONS_PER_PAGE
            questions = Question.query.all()
            formatted_questions = [question.format() for question in questions]
            _categories = Category.query.all()
            categories = {
                "1": _categories[0].type,
                "2": _categories[1].type,
                "3": _categories[2].type,
                "4": _categories[3].type,
                "5": _categories[4].type,
                "6": _categories[5].type
            }
            required_questions = formatted_questions[start:end]
            last_question = required_questions[-1]
            currentCategory = 'History'

            return jsonify({
                'success': True,
                'questions': required_questions,
                'totalQuestions': len(formatted_questions),
                'categories': categories,
                'currentCategory': currentCategory
            })
        except():
            abort(500)

    @cross_origin()
    @app.route('/questions/<int:question_id>', methods=['DELETE'])
    def deleteQuestion(question_id):
        try:
            # Delete question
            question = Question.query.get(question_id)
            if question is None:
                abort(404)

            question.delete()
            return jsonify({
                "success": True,
                'deleted_id': str(question_id)
            })
        except():
            db.session.rollback()
            abort(500)
            return jsonify({
                "success": False
            })


    @cross_origin()
    @app.route('/questions/new', methods=["POST"])
    def addQuestion():

        request_body = request.get_json()
        new_question = Question(question=request_body.get('question'),
                                answer=request_body.get('answer'),
                                category=request_body.get('category'),
                                difficulty=request_body.get('difficulty')
                                )

        # Confirm all args sent
        if not new_question.question or \
            not new_question.answer or\
                not new_question.category or \
                    not new_question.difficulty:
            abort(400)
        try:
            # Add new question
            new_question.insert()
            return jsonify({
                'success': True,
                'question_id': new_question.id
            })
        except():
            db.session.rollback()
            abort(500)

    @cross_origin()
    @app.route('/questions/search', methods=['POST'])
    def search_questions():
        try:
            try:
                # Get args
                body = request.get_json()
                search_term = body['searchTerm']
            except():
                abort(400)
            # Get required questions
            required_questions = Question.query.filter(
                func.lower(
                    Question.question).contains(
                    func.lower(search_term))).all()
            formatted_required_questions = [
                question.format() for question in required_questions]
            currentCategory = 'History'
            return jsonify({
                'success': True,
                'questions': formatted_required_questions,
                'totalQuestions': len(formatted_required_questions),
                'currentCategory': currentCategory
            })
        except():
            abort(500)

    @cross_origin()
    @app.route('/categories/<int:category_id>/questions', methods=['GET'])
    def getQuestionByCategory(category_id):
        try:
            # GEt questions by categories
            categories = Category.query.filter(
                Category.id == category_id).all()
            if len(categories) == 0:
                abort(404)
            categ = categories[0]
            questions = Question.query.all()
            total_formatted_questions = [
                question.format() for question in questions]
            required_questions = []
            for ques in questions:
                if ques.category == category_id:
                    required_questions.append(ques.format())

            return jsonify({
                'success': True,
                'questions': required_questions,
                'totalQuestions': len(total_formatted_questions),
                'currentCategory': categ.type
            })
        except():
            abort(500)

    @cross_origin()
    @app.route('/quizzes', methods=['POST'])
    def getQuiz():
        try:
            try:
                # Get args
                body = request.get_json()
                previous_questions = body.get("previous_questions", [])
                quiz_category = body.get('quiz_category')
            except():
                """ Bad request"""
                abort(400)
            if not body.get("quiz_category"):
                return jsonify({
                    'success': False
                }), 400

            if quiz_category['id'] == 0:
                """ Questions from any category"""
                questions_from_required_category = Question.query.all()
            else:
                """ Questions from specific category"""
                questions_from_required_category = Question.query.filter(
                    Question.category == quiz_category['id'])

            formatted_questions = [
                question.format() for question in questions_from_required_category]

            if len(previous_questions) == len(formatted_questions):
                """ All available questions have been asked"""
                return jsonify({
                    'success': True,
                    'previousQuestions': previous_questions
                })
            else:
                if len(previous_questions) == 0:
                    """ No previous question """
                    new_question = random.choice(
                        [question for question in formatted_questions]
                    )
                else:
                    new_questions = []
                    for ques in formatted_questions:
                        if (ques['id'] not in previous_questions):
                            new_questions.append(ques)
                    new_question = random.choice(
                        [question for question in new_questions]
                    )
                return jsonify({
                    'success': True,
                    'question': new_question,
                    'previousQuestions': previous_questions
                })

        except():
            abort(500)

    @app.errorhandler(404)
    def resourceNotFound(error):
        return jsonify({
            "sucess": False,
            "error": 404,
            "message": "Resource not found"
        }), 404

    @app.errorhandler(422)
    def unprocessable(error):
        return jsonify({
            "success": False,
            "error": 422,
            "message": "Unprocessable"
        }), 422

    @app.errorhandler(400)
    def badRequest(error):
        return jsonify({
            "success": False,
            "error": 400,
            "message": "Bad request"
        }), 400

    @app.errorhandler(405)
    def methodNotAllowed(error):
        return jsonify({
            "sucess": False,
            "error": 405,
            "message": "Method not allowed"
        }), 405

    @app.errorhandler(500)
    def internalServerError(error):
        return jsonify({
            "success": False,
            "error": 500,
            "message": "Internal server error"
        }), 500
    return app
