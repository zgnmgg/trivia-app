import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import setup_db, Question, Category

CATEGORY_ALL = '0'
QUESTIONS_PER_PAGE = 10

db = SQLAlchemy()

def paginate_questions(request, selections):
    page = request.args.get('page', 1, type=int)
    start = (page - 1) * QUESTIONS_PER_PAGE
    end = start + QUESTIONS_PER_PAGE

    questions = [question.format() for question in selections]
    current_questions = questions[start:end]

    return current_questions


def create_app(test_config=None):
    app = Flask(__name__)
    if config == "test":
        app.config.from_object("config.TestConfig")
    else:
        app.config.from_object("config.Config")

    db.init_app(app)

    CORS(app)

    @app.after_request
    def after_request(response):
        response.headers.add('Access-Control-Allow-Headers',
                             'Content-Type,Authorization,true')
        response.headers.add('Access-Control-Allow-Methods',
                             'GET,PUT,POST,DELETE,OPTIONS')
        return response

    @app.route('/categories', methods=['GET'])
    def get_categories():
        categories = Category.query.order_by(Category.type).all()
        if len(categories) == 0:
            abort(404)
        return_categories = {
            categories.id: category.type for category in categories
        }
        return jsonify({
            "success": True,
            'categories': return_categories
            "total_categories": len(return_categories)
        })

    @app.route('/questions')
    def get_questions():
        selection = Question.query.all()
        total_questions = len(selection)
        current_questions = paginate_questions(request, selection)

        categories = Category.query.all()
        categories_dict = {}
        for category in categories:
            categories_dict[category.id] = category.type

        if len(current_questions) == 0:
            abort(404)

        return jsonify({
            'success': True,
            'questions': current_questions,
            'total_questions': total_questions,
            'categories': categories_dict
        })

    @app.route('/questions/<int:id>', methods=['DELETE'])
    def delete_question(id):
        try:
            question = Question.query.get(id)

            if question is None:
                abort(404)

            question.delete()

            return jsonify({'success': True, 'deleted': id})
        except:
            abort(422)

    @app.route('/questions', methods=['POST'])
    def add_question():
        body = request.get_json()

        if (body.get('searchTerm')):
            search_term = body.get('searchTerm')

            if (len(selection) == 0):
                abort(404)

            paginated = paginate_questions(request, selection)

            return jsonify({
                'success': True,
                'questions': paginated,
                'total_questions': len(Question.query.all())
            })
        else:
            new_question = body.get('question')
            new_answer = body.get('answer')
            new_difficulty = body.get('difficulty')
            new_category = body.get('category')

            if len(new_question) == 0 or len(new_answer) == 0 \
                or len(new_difficulty) == 0 or len(new_category) == 0:
                abort(422)
            question = Question(
                question=new_question,
                answer=insert_answer,
                category=insert_category,
                difficulty=insert_difficulty
            )
            question.insert()
            all_questions = Question.query.all()
            current_questions = paginate_questions(request, all_questions)

            return jsonify({
                'success': True,
                'created': question.id,
            })

    @app.route('/questions/search', methods=['POST'])
    def search_questions():
        body = request.get_json()
        search_term = body.get('searchTerm', None)

        if search_term:
            search_results = Question.query.filter(
                Question.question.ilike(f'%{search_term}%')).all()

            return jsonify({
                'success': True,
                'questions': [
                    question.format() for question in search_results
                ],
                'total_questions': len(search_results),
                'current_category': None
            })
        abort(404)

    @app.route('/categories/<int:id>/questions', methods=['GET'])
    def get_questions_by_category(id):
        try:
            category = Category.query.filter_by(id=id).one_or_none()

            if (category is None):
                abort(404)
            selection = Question.query.filter_by(category=category.id).all()
            paginated = paginate_questions(request, selection)
            return jsonify({
                'success': True,
                'questions': paginated,
                'total_questions': len(Question.query.all()),
                'current_category': category.type
            })

    @app.route('/quizzes', methods=['POST'])
    def quiz():
        try:
            body = request.get_json()
            previous = body.get('previous_questions')
            category = body.get('quiz_category')

            if ((category is None) or (previous is None)):
                abort(400)

            if (category['id'] == CATEGORY_ALL):
                questions = Question.query.all()
            else:
                questions = Question.query.filter_by(category=category['id'])
                .all()

            total = len(questions)

            def get_random_question():
                return questions[random.randrange(0, len(questions), 1)]

            def check_if_used(question):
                used = False
                for q in previous:
                    if (q == question.id):
                        used = True

                return used

            question = get_random_question()

            while (check_if_used(question)):
                question = get_random_question()

                if (len(previous) == total):
                    return jsonify({
                        'success': True
                    })

            # return the question
            return jsonify({
                'success': True,
                'question': question.format()
            })

    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            "success": False,
            "error": 404,
            "message": "resource not found"
        }), 404

    @app.errorhandler(422)
    def unprocessable(error):
        return jsonify({
            "success": False,
            "error": 422,
            "message": "unprocessable"
        }), 422

    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({
            "success": False,
            "error": 400,
            "message": "bad request"
        }), 400

    return app
