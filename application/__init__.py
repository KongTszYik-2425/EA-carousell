from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
# from flask_bootstrap import Bootstrap
import config
from datetime import timedelta

config.Config.db = SQLAlchemy()
app = Flask(__name__)
app.config.from_object(config.Config)
config.Config.db.init_app(app)
migrate = Migrate(app, config.Config.db)
app.config['JWT_SECRET_KEY'] = 'jwt-secret-key'  # 新增JWT專用密鑰
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=1)  # Token有效期1小時
app.config['JWT_ALGORITHM'] = 'HS256'  # 极简签名算法
jwt = JWTManager(app)
# bootstrap = Bootstrap(app)




def create_app():
    from application.customer import customer
    app.register_blueprint(customer)

create_app()


from application import routes



