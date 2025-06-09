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

    
    """
    Import models for Alchemy to recognize
    """
    
    # import tables
    from app.models import Admin
    from app.models import Book
    from app.models import Comment
    from app.models import Complaint
    from app.models import ForumPost
    from app.models import Order
    from app.models import OrderDetail
    from app.models import PostLike
    from app.models import Suggestion
    from app.models import SuggestionAgree
    from app.models import User
    from app.models import UserBrowse
    from app.models import UserCart
    from app.models import UserFavorite

    """
    Register blueprints
    """

    # register tables
    from app.routes.tables.admin import admin_bp
    from app.routes.tables.book import book_bp
    from app.routes.tables.comment import comment_bp
    from app.routes.tables.complaint import complaint_bp
    from app.routes.tables.forumpost import forum_post_bp
    from app.routes.tables.order import order_bp
    from app.routes.tables.orderdetail import order_detail_bp
    from app.routes.tables.postlike import post_like_bp
    from app.routes.tables.suggestion import suggestion_bp
    from app.routes.tables.suggestionagree import suggestion_agree_bp
    from app.routes.tables.user import user_bp
    from app.routes.tables.userbrowse import user_browse_bp
    from app.routes.tables.usercart import user_cart_bp
    from app.routes.tables.userfavorite import user_favorite_bp

    app.register_blueprint(admin_bp)
    app.register_blueprint(book_bp)
    app.register_blueprint(comment_bp)
    app.register_blueprint(complaint_bp)
    app.register_blueprint(forum_post_bp)
    app.register_blueprint(order_bp)
    app.register_blueprint(order_detail_bp)
    app.register_blueprint(post_like_bp)
    app.register_blueprint(suggestion_bp)
    app.register_blueprint(suggestion_agree_bp)
    app.register_blueprint(user_bp)
    app.register_blueprint(user_browse_bp)
    app.register_blueprint(user_cart_bp)
    app.register_blueprint(user_favorite_bp)
    
    return app