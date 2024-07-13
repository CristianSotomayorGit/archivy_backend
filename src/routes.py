from flask import Blueprint, request, jsonify,make_response
from .models import User
from flask_login import LoginManager, login_user

main = Blueprint('main', __name__)
login_manager = LoginManager()
##login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@main.route('/login', methods=['OPTIONS', 'POST'])
def login():
    if request.method == 'OPTIONS':
        response = make_response()
        response.headers.add("Access-Control-Allow-Origin", "*")
        response.headers.add("Access-Control-Allow-Headers", "Content-Type")
        response.headers.add("Access-Control-Allow-Methods", "POST, OPTIONS")
        return response

    elif request.method == 'POST':
        data = request.get_json()
        user = User.query.filter_by(username=data['username']).first()
        
        if user:
            ##and bcrypt.check_password_hash(user.password, data['password']):
            login_user(user)
            response = make_response(jsonify({'message': 'success, you are logged in'}))
        else:
            response = make_response(jsonify({'message': 'sorry your credentials were not found'}))
                
        response.headers['Access-Control-Allow-Origin'] = '*'

        return response
    
@main.route('/signup', methods=['POST'])
def signup():
    response = make_response(jsonify({'message': 'Signing ya right up!'}))
    return response
