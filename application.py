import os
from flask import Blueprint, Flask
from flask_cors import CORS
from flask_login import LoginManager
from src.routes import main as main_blueprint, login_manager, bcrypt
from src.models import db
from config import Config as config_instance
import pinecone


application = Flask(__name__)

# application.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://admin:608RidgeRoad.@archivy-database.cpekiiyaqooa.us-west-1.rds.amazonaws.com:3306/archivy-database'
application.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

application.config.from_object(config_instance)

# CORS(application)
application.register_blueprint(main_blueprint)

CORS(application, resources={r"/*": {"origins": ["http://d3lffun906l4lt.cloudfront.net", "http://127.0.0.1:3001","https://127.0.0.1:3001/"]}})
db.init_app(application)
login_manager.init_app(application)
bcrypt.init_app(application)

if __name__ == "__main__":
    application.debug = True
    application.run()