from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from google.cloud import storage
import config
from datetime import timedelta

config.Config.db = SQLAlchemy()
app = Flask(__name__)
app.config.from_object(config.Config)
config.Config.db.init_app(app)
migrate = Migrate(app, config.Config.db)
app.config['JWT_SECRET_KEY'] = 'jwt-secret-key'
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=1) 
app.config['JWT_ALGORITHM'] = 'HS256'
jwt = JWTManager(app)

def create_app():
    from application.customer import customer
    app.register_blueprint(customer)

create_app()

from application import routes



