from flask import Flask
from .database import init_db


def create_app(database_path=None):
    app = Flask(__name__)
    app.config["DATABASE_PATH"] = database_path
    init_db(app)

    from .routes import bp, service
    app.register_blueprint(bp)
    app.service = service
    return app
