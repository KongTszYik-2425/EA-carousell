from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

import config

config.Config.db = SQLAlchemy()
def create_app():
    app = Flask(__name__)
    app.config.from_object(config.Config)
    config.Config.db.init_app(app)

    from application.customer import customer
    app.register_blueprint(customer)

    return app



