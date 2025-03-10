import os
from flask import Flask
from config import dev_config
from .extensions.db import db
from flask_migrate import Migrate
from dotenv import load_dotenv

load_dotenv()

#TODO: Change the servername later on
#Add the config loads
def create_app(config_class = dev_config):
    app = Flask(__name__, template_folder=os.path.abspath("app/templates"),
                static_folder=os.path.abspath("app/static"))
    app.config.from_object(config_class)

    # Initialize the database
    db.init_app(app)

    # Initialize Flask-Migrate (optional)
    Migrate(app, db)

    # Set a secret key for session management
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'your_default_secret_key')
    app.config['SERVER_NAME'] = 'localhost:5000'

    # Import and register Blueprints
    from app.routes.main import main
    from app.routes.auth import auth
    from app.routes.admin import admin
    app.register_blueprint(main)
    app.register_blueprint(admin)
    app.register_blueprint(auth)

    return app
