from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

import config

config.Config.db = SQLAlchemy()
app = Flask(__name__)
app.config.from_object(config.Config)
config.Config.db.init_app(app)




def create_app():
    from application.customer import customer
    app.register_blueprint(customer)

create_app()


from application import routes



