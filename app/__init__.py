from flask import Flask
from flask_pymongo import PyMongo
from flask_login import LoginManager, UserMixin
from bson.objectid import ObjectId

mongo = PyMongo()
login_manager = LoginManager()

class User(UserMixin):
    def __init__(self, user_data):
        self.id = str(user_data['_id'])
        self.name = user_data['name']
        self.email = user_data['email']

@login_manager.user_loader
def load_user(user_id):
    user_data = mongo.db.users.find_one({"_id": ObjectId(user_id)})
    if user_data:
        return User(user_data)
    return None

def create_app():
    app = Flask(__name__)
    app.config.from_pyfile('../config.py')

    mongo.init_app(app)
    login_manager.init_app(app)

    # Register blueprints
    from app.routes.auth import auth_bp
    from app.routes.users import users_bp
    from app.routes.swaps import swaps_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(users_bp)
    app.register_blueprint(swaps_bp)

    return app
