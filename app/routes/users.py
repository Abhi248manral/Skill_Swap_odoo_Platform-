from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from app import mongo
from bson.objectid import ObjectId

users_bp = Blueprint('users_bp', __name__, url_prefix='/user')

@users_bp.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('auth_bp.login'))

    user = mongo.db.users.find_one({'_id': ObjectId(session['user_id'])})
    return render_template('profile.html', user=user)

@users_bp.route('/edit', methods=['GET', 'POST'])
def edit_profile():
    if 'user_id' not in session:
        return redirect(url_for('auth_bp.login'))

    user = mongo.db.users.find_one({'_id': ObjectId(session['user_id'])})

    if request.method == 'POST':
        skills_offered = request.form.getlist('skills_offered')
        skills_wanted = request.form.getlist('skills_wanted')
        availability = request.form.getlist('availability')
        is_public = request.form.get('is_public') == 'on'

        mongo.db.users.update_one(
            {'_id': ObjectId(session['user_id'])},
            {'$set': {
                'skills_offered': skills_offered,
                'skills_wanted': skills_wanted,
                'availability': availability,
                'is_public': is_public
            }}
        )
        flash('Profile updated successfully.')
        return redirect(url_for('users_bp.dashboard'))

    return render_template('edit_profile.html', user=user)

@users_bp.route('/search')
def search_users():
    query = request.args.get('q', '').lower()
    users = []
    if query:
        users = list(mongo.db.users.find({
            'skills_offered': {'$regex': query, '$options': 'i'},
            'is_public': True
        }))
    return render_template('home.html', users=users, query=query)
