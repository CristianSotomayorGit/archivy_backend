import os
from flask import Blueprint, json, request, jsonify,make_response
from .models import User
from flask_login import LoginManager, login_user
from .forms import RegisterForm
from .models import db
from sqlalchemy.exc import SQLAlchemyError
from flask_bcrypt import Bcrypt
from langchain_community.vectorstores import Pinecone
from bs4 import BeautifulSoup
from langchain_openai.embeddings import OpenAIEmbeddings
from langchain_openai.chat_models import ChatOpenAI
from langchain.chains.question_answering import load_qa_chain


main = Blueprint('main', __name__)
login_manager = LoginManager()
bcrypt = Bcrypt()

def handle_cors():
    response = make_response()
    response.headers.add("Access-Control-Allow-Origin", "*")
    response.headers.add("Access-Control-Allow-Headers", "Content-Type")
    response.headers.add("Access-Control-Allow-Methods", "POST, OPTIONS")
    return response

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@main.route('/login', methods=['OPTIONS', 'POST'])
def login():
    if request.method == 'OPTIONS':
        response = handle_cors()
        return response

    elif request.method == 'POST':
        data = request.get_json()
        user = User.query.filter_by(username=data['username']).first()
        
        if user and bcrypt.check_password_hash(user.password, data['password']):
            login_user(user)
            response = make_response(jsonify({'message': 'success, you are logged in'}))
        else:
            response = make_response(jsonify({'message': 'sorry your credentials were not found'}))
                
        response.headers['Access-Control-Allow-Origin'] = '*'

        return response
    
@main.route('/signup', methods=['OPTIONS','POST'])
def signup():
    
    if request.method == 'OPTIONS':
        response = handle_cors()
        return response
    
    # data = request.form
    data = request.get_json()

    required_fields = ['firstname','lastname','email','username','password']

    for field in required_fields:
        if field not in required_fields:
            response = make_response(jsonify({'success': False, 'error': f'Missing field {field}'}), 400)
            response.headers['Access-Control-Allow-Origin'] = '*'
            return response

    if not (4 <= len(data['firstname']) <= 40):
        response = make_response(jsonify({'success': False, 'error': 'Invalid length for firstname'}), 400)
        response.headers['Access-Control-Allow-Origin'] = '*'
        return response
    
    if not (4 <= len(data['lastname']) <= 40):
        response = make_response(jsonify({'success': False, 'error': 'Invalid length for lastname'}), 400)
        response.headers['Access-Control-Allow-Origin'] = '*'
        return response
    
    if not (4 <= len(data['email']) <= 40):
        response = make_response(jsonify({'success': False, 'error': 'Invalid length for email'}), 400)
        response.headers['Access-Control-Allow-Origin'] = '*'
        return response
    if not (4 <= len(data['username']) <= 20):
        response = make_response(jsonify({'success': False, 'error': 'Invalid length for username'}), 400)
        response.headers['Access-Control-Allow-Origin'] = '*'
        return response
    if not (8 <= len(data['password']) <= 20):
        response = make_response(jsonify({'success': False, 'error': 'Invalid length for password'}), 400)
        response.headers['Access-Control-Allow-Origin'] = '*'
        return response

    try:
        hashed_password = bcrypt.generate_password_hash(data['password']).decode('utf-8')
        new_user = User(
            firstname=data['firstname'],
            lastname=data['lastname'],
            email=data['email'],
            username=data['username'],
            password=hashed_password,
            hasAnswered=0
        )
        db.session.add(new_user)
        db.session.commit()

        response = make_response(jsonify({'success': True, 'message': 'User registered successfully'}), 201)
        response.headers['Access-Control-Allow-Origin'] = '*'

        return response

    except SQLAlchemyError as e:
        db.session.rollback()
        print(e)
        response = make_response(jsonify({'success': False, 'error': 'Database error occurred'}), 500)
        response.headers['Access-Control-Allow-Origin'] = '*'

        return response  

@main.route('/process_prompt', methods=['POST', 'OPTIONS'])
def process_prompt():
    if request.method == 'OPTIONS':
        response = handle_cors()
        return response
    
    data = request.get_json()
    prompt = data['message']

    embeddings = OpenAIEmbeddings(openai_api_key=os.environ.get('OPEN_AI_SECRET_KEY'))

    llm = ChatOpenAI(temperature=0, openai_api_key=os.environ.get('OPEN_AI_SECRET_KEY'),model="gpt-4")
    chain = load_qa_chain(llm, chain_type='stuff')

    doc_search = Pinecone.from_existing_index('langchain1', embeddings)
    
    docs = doc_search.similarity_search(prompt)

    relatedChunks = []
    for doc in docs:
        relatedChunks.append(doc.metadata)

    responseText = chain.run(input_documents=docs, question=prompt)

    # response = {"response": responseText, "sources": relatedChunks}

    # conversation_history.append({"role": "assistant", "content": response})

    # data = json.dumps(conversation_history)

    # latest_conversation = Conversation.query.order_by(Conversation.id.desc()).first()

    # if latest_conversation:
    #     latest_conversation.json = data
    #     db.session.commit()

    
    

    print(data['message'])

    response = jsonify(answer=responseText, relatedChunks=relatedChunks)
    response.headers['Access-Control-Allow-Origin'] = '*'

    return response