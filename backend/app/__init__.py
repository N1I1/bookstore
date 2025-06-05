from flask import Flask
from flask_cors import CORS
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

from config import Config

db = SQLAlchemy()
migrate = Migrate()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    migrate.init_app(app, db)

    CORS(app)

    # Import models for Alchemy to recognize
    from app.models import Book

    # Register blueprints
    from app.routes.book import book_bp
    app.register_blueprint(book_bp)
    return app