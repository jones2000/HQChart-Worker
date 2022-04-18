from flask import Flask
from flask_cors import CORS

from config import config
from hqchartPy2.extention import db
from hqchartPy2.views import config_blueprint


def create_app(config_name):
    app = Flask(__name__, static_url_path='')
    app.debug = True
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)
    CORS(app, supports_credentials=True)  # 跨域
    db.init_app(app)
    config_blueprint(app)
    return app
