from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from os import path
from flask_login import LoginManager
from flask_bootstrap import Bootstrap


# create db object
db = SQLAlchemy()
# create db name
DB_NAME = 'book.db'


def create_app():
    # create and configure the app and database
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'super_secret_key'
    bootstrap = Bootstrap(app)
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DB_NAME}'
    db.init_app(app)

    # import blueprints
    from .views import views
    from .auth import auth
    app.register_blueprint(views, url_prefix='/')
    app.register_blueprint(auth, url_prefix='/')

    # import models
    from .models import User, Book, Order

    # create database using the create_database function
    create_database(app)

    # set up log in manager
    login_manager = LoginManager()
    login_manager.init_app(app)

    # this function is used to load the user
    @login_manager.user_loader
    def load_user(id):
        return User.query.get(int(id))

    return app


# create database function
def create_database(app):
    # if the database does not exist, create it
    if not path.exists('./instance/' + DB_NAME):
        with app.app_context():
            db.create_all()
        print('Created Database!')
