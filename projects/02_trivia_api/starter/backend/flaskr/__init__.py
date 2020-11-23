import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10
###-------
def paginate_questions(request, selection):
  page = request.args.get('page', 1, type=int)
  start = (page-1) * QUESTIONS_PER_PAGE
  end = start + QUESTIONS_PER_PAGE
  questions = [question.format() for question in selection]
  current_questions = questions[start:end]

  return current_questions

###-------
def create_app(test_config=None):
  # create and configure the app
  app = Flask(__name__)
  setup_db(app)


  '''
  @TODO: Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
  '''

  cors = CORS(app, resources={r"/api/*":{"origins": "*"}})

  '''
  @TODO: Use the after_request decorator to set Access-Control-Allow
  '''

  @app.after_request
  def after_request(response):
    response.headers.add('Access-Control-Allow-Headers','Content-Type, Authorization, true')
    response.headers.add('Access-Control-Allow-Methods','GET, PATCH, PUT, POST, DELETE, OPTIONS')
    return response

  '''
  @TODO:
  Create an endpoint to handle GET requests
  for all available categories.
  '''
###-------
  @app.route('/categories', methods=['GET'])
  def get_categories():
    categories = Category.query.order_by(Category.id).all()

    if len(categories) == 0:
      abort(404)

    return jsonify({
      'success': True,
      'categories': {category.id: category.type for category in categories},
      'total_categories': len(Category.query.all()),
      'status': 200
    })
###-------
  '''
  @TODO:
  Create an endpoint to handle GET requests for questions,
  including pagination (every 10 questions).
  This endpoint should return a list of questions,
  number of total questions, current category, categories.

  TEST: At this point, when you start the application
  you should see questions and categories generated,
  ten questions per page and pagination at the bottom of the screen for three pages.
  Clicking on the page numbers should update the questions.
  '''
###-------
  @app.route('/questions', methods=['GET'])
  def get_questions():
    questions_list = Question.query.all()
    current_questions = paginate_questions(request, questions_list)
    categories = Category.query.order_by(Category.type).all()

    if len(current_questions) == 0:
      abort(404)

    return jsonify({
      'success': True,
      'questions': current_questions,
      'total_questions': len(questions_list),
      'current_category': None,
      'categories': {category.id: category.type for category in categories}
    })
###-------
  '''
  @TODO:
  Create an endpoint to DELETE question using a question ID.

  TEST: When you click the trash icon next to a question, the question will be removed.
  This removal will persist in the database and when you refresh the page.
  '''
###-------
  @app.route('/questions/<int:question_id>', methods=['DELETE'])
  def delete_question(question_id):
    try:
      question = Question.query.get(question_id)
      question.delete()
      return jsonify({
        'success': True,
        'deleted': question.id,
        'message': 'Successfully deleted',
        #'total_questions': len(Question.query.all())
      })#, 200
    except:
      abort(404)
###-------
  '''
  @TODO:
  Create an endpoint to POST a new question,
  which will require the question and answer text,
  category, and difficulty score.

  TEST: When you submit a question on the "Add" tab,
  the form will clear and the question will appear at the end of the last page
  of the questions list in the "List" tab.
  '''
###-------
  @app.route('/questions/add', methods=['POST'])
  def create_question():
    body = request.get_json()

    new_question = body.get('question', None)
    new_answer = body.get('answer', None)
    new_category = body.get('category', None)
    new_difficulty = body.get('difficulty', None)

    try:
      question = Question(question=new_question, answer=new_answer, category=new_category, difficulty=new_difficulty)
      question.insert()

      #selection = Question.query.order_by('id').all()
      #selection = Question(question).query.order_by('id').all()
      #current_questions = paginate_questions(request, selection)

      return jsonify({
        'success': True,
        #'created': question_id,
        'question': new_question,
        'answer': new_answer,#//
        'difficulty': new_difficulty,
        'category': new_category
        #'questions': current_questions,
        #'total_questions': len(selection)
      })
    except:
      abort(422)
###-------
  '''
  @TODO:
  Create a POST endpoint to get questions based on a search term.
  It should return any questions for whom the search term
  is a substring of the question.

  TEST: Search by any phrase. The questions list will update to include
  only question that include that string within their question.
  Try using the word "title" to start.
  '''
###-------
  @app.route('/questions', methods=['POST'])
  def search_question():
    try:
      body = request.get_json()
      search = body.get('searchTerm', None)
      results = Question.query.filter(Question.question.ilike('%{}%'.format(search))).all()
      #Question.query.filter(Question.question.ilike(f'%{search}%')).all()
      formatted_questions = [question.format() for question in results]

      if len(results) == 0:
        #print (sys.exc_info())
        formatted_questions = []
        abort(400)

      return jsonify({
        'success': True,
        'questions': formatted_questions,
        #'questions': paginate_questions(result, results),
        'total_questions': len(results),
        'current_category': None
      })
    except:
      abort(404)
###-------
  '''
  @TODO:
  Create a GET endpoint to get questions based on category.

  TEST: In the "List" tab / main screen, clicking on one of the
  categories in the left column will cause only questions of that
  category to be shown.
  '''
###-------
  @app.route('/categories/<int:category_id>/questions', methods=['GET'])
  def question_by_category(category_id):
    questions = Question.query.filter(Question.category == category_id).all()
    formatted_questions = [question.format() for question in questions] #//
    if len(questions) == 0:
      abort(404)

    selection = paginate_questions(request, questions)

    return jsonify({
      'success': True,
      'questions': selection,
      'total_questions': len(questions),
      'current_category': category_id
    })
###-------

  '''
  @TODO:
  Create a POST endpoint to get questions to play the quiz.
  This endpoint should take category and previous question parameters
  and return a random questions within the given category,
  if provided, and that is not one of the previous questions.

  TEST: In the "Play" tab, after a user selects "All" or a category,
  one question at a time is displayed, the user is allowed to answer
  and shown whether they were correct or not.
  '''

  @app.route('/quizzes', methods=['POST'])
  def play_randomized_quiz():
    try:
###-------
      data = request.get_json()
      print(data)

      quiz_category = data.get('quiz_category', None)
      previous_questions = data.get('previous_questions', None)
      print(previous_questions)

      quiz_questions = Question.query.filter(
        Question.id.notin_(previous_questions)).all()

      if quiz_category['id'] == 0:
        test_questions = Question.query.all()
      else:
        Question.query.filter(Question.id.notin_(previous_questions), Question.category == quiz_category['id']).all()

      return jsonify({
        'success': True,
        'question': random.choice(quiz_questions).format()
       })
    except:
      abort(422)
    #except Exception as e:
      #print(e)
      #print(422)

###--------
  #'''
  #@TODO:
  #Create error handlers for all expected errors
  #including 404 and 422.
  #'''
###--------
  @app.errorhandler(400)
  def bad_request(error):
    return jsonify({
      "success": False,
      "error": 400,
      "message": "Bad request"
    }), 400

  @app.errorhandler(404)
  def not_found(error):
    return jsonify({
      "success": False,
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

  @app.errorhandler(500)
  def server_error(error):
    return jsonify({
      "success":False,
      "error": 500,
      "message": "Server error"
    }), 500

  return app
