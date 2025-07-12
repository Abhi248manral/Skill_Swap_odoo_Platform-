from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from app import mongo
from bson.objectid import ObjectId
from datetime import datetime

swaps_bp = Blueprint('swaps_bp', __name__, url_prefix='/swaps')

@swaps_bp.route('/')
def view_swaps():
    if 'user_id' not in session:
        return redirect(url_for('auth_bp.login'))

    user_id = ObjectId(session['user_id'])

    sent_raw = list(mongo.db.swaps.find({'sender_id': user_id}))
    received_raw = list(mongo.db.swaps.find({'receiver_id': user_id}))

    def attach_user_info(swap, direction='receiver'):
        other_id = swap['receiver_id'] if direction == 'receiver' else swap['sender_id']
        other_user = mongo.db.users.find_one({'_id': other_id})
        if other_user:
            swap['other_name'] = other_user['name']
            swap['other_skills'] = ', '.join(other_user.get('skills_offered', []))
        else:
            swap['other_name'] = 'Unknown User'
            swap['other_skills'] = '—'
        return swap

    sent = [attach_user_info(s, 'receiver') for s in sent_raw]
    received = [attach_user_info(s, 'sender') for s in received_raw]

    return render_template('swaps.html', sent=sent, received=received)


@swaps_bp.route('/send/<receiver_id>', methods=['POST'])
def send_swap(receiver_id):
    if 'user_id' not in session:
        return redirect(url_for('auth_bp.login'))   

    existing = mongo.db.swaps.find_one({
        'sender_id': ObjectId(session['user_id']),
        'receiver_id': ObjectId(receiver_id),
        'status': 'pending'
    })

    if existing:
        flash('Swap request already sent.')
        return redirect(url_for('users_bp.dashboard'))

    swap = {
        'sender_id': ObjectId(session['user_id']),
        'receiver_id': ObjectId(receiver_id),
        'status': 'pending',
        'created_at': datetime.utcnow()
    }

    mongo.db.swaps.insert_one(swap)
    flash('Swap request sent!')
    return redirect(url_for('users_bp.dashboard'))

@swaps_bp.route('/respond/<swap_id>/<action>')
def respond_swap(swap_id, action):
    if 'user_id' not in session:
        return redirect(url_for('auth_bp.login'))

    swap = mongo.db.swaps.find_one({'_id': ObjectId(swap_id)})
    if not swap:
        flash('Swap request not found.')
        return redirect(url_for('swaps_bp.view_swaps'))

    if action not in ['accept', 'reject']:
        flash('Invalid action.')
        return redirect(url_for('swaps_bp.view_swaps'))

    mongo.db.swaps.update_one(
        {'_id': ObjectId(swap_id)},
        {'$set': {'status': action}}
    )
    flash(f'Swap {action}ed successfully.')
    return redirect(url_for('swaps_bp.view_swaps'))

@swaps_bp.route('/cancel/<swap_id>')
def cancel_swap(swap_id):
    if 'user_id' not in session:
        return redirect(url_for('auth_bp.login'))

    mongo.db.swaps.delete_one({'_id': ObjectId(swap_id)})
    flash('Swap request canceled.')
    return redirect(url_for('swaps_bp.view_swaps'))

@swaps_bp.route('/feedback/<swap_id>', methods=['POST'])
def give_feedback(swap_id):
    if 'user_id' not in session:
        return redirect(url_for('auth_bp.login'))

    rating = int(request.form['rating'])
    comment = request.form['comment']

    mongo.db.swaps.update_one(
        {'_id': ObjectId(swap_id)},
        {'$set': {
            'feedback': {
                'rating': rating,
                'comment': comment
            }
        }}
    )

    flash('Feedback submitted.')
    return redirect(url_for('swaps_bp.view_swaps'))
