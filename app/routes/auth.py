from flask import Blueprint, render_template, redirect, request, flash, url_for, session
from werkzeug.security import generate_password_hash, check_password_hash
from app import mongo
from bson.objectid import ObjectId

auth_bp = Blueprint('auth_bp', __name__, url_prefix='/auth')

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']

        if mongo.db.users.find_one({'email': email}):
            flash('Email already registered')
            return redirect(url_for('auth_bp.register'))

        hashed_pw = generate_password_hash(password)
        user = {
            'name': name,
            'email': email,
            'password_hash': hashed_pw,
            'skills_offered': [],
            'skills_wanted': [],
            'availability': [],
            'is_public': True
        }
        mongo.db.users.insert_one(user)
        flash('Registration successful. Please log in.')
        return redirect(url_for('auth_bp.login'))

    return render_template('register.html')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = mongo.db.users.find_one({'email': email})
        if user and check_password_hash(user['password_hash'], password):
            session['user_id'] = str(user['_id'])
            session['user_name'] = user['name']
            return redirect(url_for('users_bp.dashboard'))
        flash('Invalid credentials')
    return render_template('login.html')

@auth_bp.route('/logout')
def logout():
    session.clear()
    flash('Logged out successfully')
    return redirect(url_for('auth_bp.login'))
