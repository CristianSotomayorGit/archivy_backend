from flask import Blueprint, request, jsonify,make_response
from .models import User

main = Blueprint('main', __name__)

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
        user = User.query.filter_by(username=data['username'], password=data['password']).first()
        
        if user:
            response = make_response(jsonify({'message': 'success, you are logged in'}))
        else:
            response = make_response(jsonify({'message': 'sorry your credentials were not found'}))
                
        response.headers['Access-Control-Allow-Origin'] = '*'

        return response