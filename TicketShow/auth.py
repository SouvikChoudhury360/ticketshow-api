from flask import Blueprint, render_template, url_for, request, redirect, make_response, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, logout_user, login_required
from .models import User
from . import db

auth = Blueprint('auth', __name__)

# LOGIN 
@auth.route('/login', methods=['POST'])
def login_post():
    req = request.json
    email = req["email"]
    password = req["password"]
    remember = True

    user = User.query.filter_by(email=email).first()
    wrong_pass = {"password": "INVALID CREDENTIALS"}
    user_response = {"email": user.email, "name": user.name, "userid": user.id}

    if not user or not check_password_hash(user.password, password):
        return make_response(jsonify(wrong_pass), 401)

    login_user(user, remember=remember)
    return make_response(jsonify(user_response), 200)


# SIGNUP
@auth.route('/signup', methods=['POST'])
def signup_post():
    req = request.json
    email = req['email']
    name = req['name']
    password = req['password']
    user = User.query.filter_by(email=email).first()
    if user:
        return make_response(jsonify({"account":"exists"}), 401)
    new_user = User(email=email, name=name, isAdmin=False , password=generate_password_hash(password, method='sha256'))
    db.session.add(new_user)
    db.session.commit()
    return make_response(jsonify({"email":email, "name": name}), 200)


# ADMIN LOGIN
@auth.route('/adminAuth', methods=['POST'])
def adminAuth_post():
    req = request.json
    password = req["password"]
    user = User.query.filter_by(email="admin@ticketshow.co").first()
    if not user :
        new_user = User(email="admin@ticketshow.co", name="Admin", isAdmin=True , password=generate_password_hash("12345#", method='sha256'))
        db.session.add(new_user)
        db.session.commit()      
        user = new_user 
    
    if not user or not check_password_hash(user.password, password):
        wrong_pass = {"password": "INVALID CREDENTIALS"}
        return make_response(jsonify(wrong_pass) ,401)
    
    login_user(user, remember=True)
    return make_response(jsonify({"admin": "login-successful"}), 200)

# LOGOUT
@ auth.route('/logout', methods=['POST'])
@login_required
def logout():
    logout_user()
    return make_response(jsonify({"user": "logged out"}), 200)