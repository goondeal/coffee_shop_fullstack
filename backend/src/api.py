import os
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS

from .database.models import db_drop_and_create_all, setup_db, Drink
from .auth.auth import AuthError, requires_auth

app = Flask(__name__)
setup_db(app)
CORS(app)

'''
@TODO uncomment the following line to initialize the datbase
!! NOTE THIS WILL DROP ALL RECORDS AND START YOUR DB FROM SCRATCH
!! NOTE THIS MUST BE UNCOMMENTED ON FIRST RUN
'''

# db_drop_and_create_all()

'''
    GET /drinks
        it should be a public endpoint
        it should contain only the drink.long() data
        representation
    returns status code 200 and json {"success": True, "drinks": drinks}
    where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''


@app.route('/drinks')
def get_drinks():
    drinks = Drink.query.all()
    return jsonify({
        'success': True,
        'drinks': [drink.long() for drink in drinks],
    }), 200


'''
    GET /drinks-detail
        it should require the 'get:drinks-detail' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drinks}
    where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''


@app.route('/drinks-detail')
@requires_auth('get:drinks-detail')
def get_drinks_details():
    drinks = Drink.query.all()
    return jsonify({
        'success': True,
        'drinks': [drink.long() for drink in drinks],
    }), 200


'''
    POST /drinks
        it should create a new row in the drinks table
        it should require the 'post:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink}
    where drink an array containing only the newly created drink
        or appropriate status code indicating reason for failure
'''


@app.route("/drinks", methods=["POST"])
@requires_auth("post:drinks")
def create_drink():
    # Get the body of the request as a json.
    body = request.get_json()
    # Abort bad request if no request body.
    if body is None:
        abort(400)

    title = body.get("title", None)
    recipe = body.get("recipe", None)

    new_drink = Drink(title=title, recipe=json.dumps(recipe))
    new_drink.insert()

    return jsonify({
        'success': True,
        'drinks': [new_drink.long()],
    }), 200


'''
    PATCH /drinks/<drink_id>
        where [drink_id] is the existing model id
        it should respond with a 404 error if [drink_id] is not found
        it should update the corresponding row for <id>
        it should require the 'patch:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink}
    where drink an array containing only the updated drink
        or appropriate status code indicating reason for failure
'''


@app.route("/drinks/<int:drink_id>", methods=["PATCH"])
@requires_auth("patch:drinks")
def update_drink(drink_id):
    # Get the body of the request as a json.
    body = request.get_json()
    # Abort bad request if no request body.
    if body is None:
        abort(400)
    # Get parameters from the request body.
    title = body.get("title", None)
    recipe = body.get("recipe", None)
    # Get the drink to be updated or None if not exists.
    drink = Drink.query.filter(Drink.id == drink_id).one_or_none()
    # Abort 404 error if drink is None.
    if drink is None:
        abort(404)

    # Update with new values.
    if title is not None:
        drink.title = title
    if recipe is not None:
        drink.recipe = json.dumps(recipe)
    # Update in the database.
    drink.update()
    # return result formatted as required.
    return jsonify({
        'success': True,
        'drinks': [drink.long()],
    }), 200


'''
    DELETE /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should delete the corresponding row for <id>
        it should require the 'delete:drinks' permission
    returns status code 200 and json {"success": True, "delete": id}
    where id is the id of the deleted record
        or appropriate status code indicating reason for failure
'''


@app.route("/drinks/<int:drink_id>", methods=["DELETE"])
@requires_auth("delete:drinks")
def delete_drink(drink_id):
    # Get the drink to be deleted or None if not exists.
    drink = Drink.query.filter(Drink.id == drink_id).one_or_none()
    # Abort 404 error if drink is None.
    if drink is None:
        abort(404)
    # Delete this drink from the database.
    drink.delete()
    # return result formatted as required.
    return jsonify({
        'success': True,
        'delete': drink_id,
    }), 200


# Error Handling
# Error handling for 422 unprocessable entity error.
@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
        "success": False,
        "error": 422,
        "message": "unprocessable",
    }), 422


# Error handler for 404 not found error.
@app.errorhandler(404)
def not_found(error):
    return jsonify({
        "success": False,
        "error": 404,
        "message": "resource not found",
    }), 404


# Implement error handler for AuthError.
@app.errorhandler(AuthError)
def auth_error(e):
    return jsonify({
        "success": False,
        "error": e.status_code,
        "message": e.error['description'],
    }), 401
