import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import setup_db, Question, Category


def paginate_question(request, questions):
  page = request.args.get('page', 1, type=int)
  start = (page - 1) * 10
  end = start + 10
  page_questions = [question.format() for question in questions[start:end]]
  return page_questions


def get_all_categories():
    categories = Category.query.order_by(Category.id).all()
    return {cat.id: cat.type for cat in categories}


def create_app(test_config=None):
  app = Flask(__name__)
  setup_db(app)
  
  CORS(app, resources={'/': {'origins': '*'}})
 
  @app.after_request
  def after_request(response):
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization,true')
    response.headers.add('Access-Control-Allow-Methods', 'GET,POST,PUT,DELETE,OPTIONS')
    return response

  # -------------------------------------------------------------------------------------
  # GET requests
  # -------------------------------------------------------------------------------------
  
  @app.route('/categories')
  def get_categories():
    categories = Category.query.all()
    categoriesDict = {}
    for category in categories:
        categoriesDict[category.id] = category.type

    return jsonify({
        'success': True,
        'categories': categoriesDict
    })


  @app.route("/questions")
  def get_questions():
    categories =  get_all_categories()
    questions = Question.query.order_by(Question.difficulty).all()
    page_questions = paginate_question(request, questions)

    if len(page_questions) < 1:
      abort(404)
    
    return jsonify({
      "questions": page_questions,
      "total_questions": len(questions),
      "categories": categories,
      })

  # -----------------------------------------------------------
  # DELETE question
  # -----------------------------------------------------------

  @app.route("/questions/<int:question_id>", methods=['DELETE'])
  def delete_question(question_id):
    question = Question.query.get(question_id)

    try:
      question.delete()
      return jsonify({
        "success":True
        })
    except:
      abort(422)

  # -----------------------------------------------------------
  # Create question POST
  # -----------------------------------------------------------

  @app.route("/questions", methods=['POST'])
  def create_search_question():
    
    try:
      req_body = request.get_json()
      search = req_body.get('searchTerm', None)
      if search :
          questions = Question.query.filter(Question.question.ilike(f'%{search}%'))\
            .order_by(Question.difficulty).all()
          page_qestions = paginate_question(request, questions)
          return jsonify({
            'questions':page_qestions,
            'total_questions':len(questions),
            'current_category': 0
            })
      else: 
        new_question = req_body['question']
        new_answer = req_body['answer']
        new_difficulty = req_body['difficulty']
        new_category = req_body['category']
        question = Question(new_question, new_answer, new_category, new_difficulty)
        question.insert()
        return jsonify({
          "success":True
          })
    except Exception as e:
          print(str(e))
          abort(422)


  # -----------------------------------------------------------
  # GET questions  category
  # -----------------------------------------------------------

  @app.route("/categories/<category_id>/questions")
  def get_category_by_id(category_id):
    questions = Question.query.filter(Question.category == category_id).order_by(Question.difficulty).all()
    page_questions = paginate_question(request, questions)

    if len(page_questions) < 1:
      abort(404)

    return jsonify({
      "questions":page_questions,
      "total_questions": len(questions),
      "current_category":category_id
      })

  # -----------------------------------------------------------
  # Quiz play using POST
  # -----------------------------------------------------------

  @app.route('/quizzes', methods=['GET','POST'])
  def get_quiz_question():
    try:
      body = request.get_json()
      prev_qs = body['previous_questions']
      cid = body['quiz_category']['id']
      print(prev_qs, cid)

      if cid == 0:
        selection = Question.query.filter(Question.id.notin_(prev_qs)).all()
      else:
        selection = Question.query.filter(Question.category==cid, Question.id.notin_(prev_qs)).all()
      
      current_qs = [q.format() for q in selection]

      if selection:
        q = current_qs[random.randint(0, len(selection)-1)]
      else:
        q = None

      return jsonify({
        'success': True,
        'question': q,
        })

    except:
      abort(422)

  @app.errorhandler(400)
  def unprocessable(error):
    return jsonify({
        'success':False,
        'error':400,
        'message':'Bad request'
    }), 400

  @app.errorhandler(404)
  def notfound(error):
    return jsonify({
        'success':False,
        'error':404,
        'message':'Resource not found'
    }), 404

  @app.errorhandler(405)
  def unprocessable(error):
    return jsonify({
        'success':False,
        'error':405,
        'message':'Method not allowed'
    }), 405

  @app.errorhandler(422)
  def unprocessable(error):
    return jsonify({
        'success':False,
        'error':422,
        'message':'Unprocessable entity'
    }), 422

  @app.errorhandler(500)
  def unprocessable(error):
    return jsonify({
        'success':False,
        'error':500,
        'message':'Internal server error'
    }), 500
  
  return app

    