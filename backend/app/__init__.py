from flask import Flask
from app.models.user import User
from app.models.resume import Resume
from app.config import Config
from app.routes.auth import auth_bp
from app.routes.oauth import oauth_bp
from app.routes.resume import resume_bp
from app.extensions import db, migrate, bcrypt, jwt
from app.utils.oauth import register_oauth_clients
from flask_cors import CORS


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    CORS(app, origins=[app.config["FRONTEND_URL"]])

    app.register_blueprint(auth_bp)
    app.register_blueprint(oauth_bp)
    app.register_blueprint(resume_bp)

    db.init_app(app)
    migrate.init_app(app, db)
    bcrypt.init_app(app)
    jwt.init_app(app)
    register_oauth_clients(app)

    @app.route("/")
    def home():
        return {
            "status": "success",
            "database": app.config["SQLALCHEMY_DATABASE_URI"] is not None
        }

    return app