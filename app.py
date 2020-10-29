from flask import Flask, request, jsonify, make_response 
from flask_sqlalchemy import SQLAlchemy 
from werkzeug.security import generate_password_hash, check_password_hash 
from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand

import jwt
import datetime
from functools import wraps


app = Flask(__name__)

app.config['SECRET_KEY'] = 'thisissecret'
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:postgres@localhost:5432/users'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
migrate = Migrate(app, db)
manager = Manager(app)
manager.add_command('db', MigrateCommand)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))
    email = db.Column(db.String(50), unique=True)
    password = db.Column(db.String(80))
    admin = db.Column(db.Boolean)


def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None

        if 'access-token' in request.headers:
            token = request.headers['access-token']

        if not token:
            return jsonify({
                'message': 'Token is missing!'
            }), 401
        
        try:
            data = jwt.decode(token, app.config['SECRET_KEY'])
            current_user = User.query.filter_by(email=data['email']).first()
        except:
            return jsonify({
                "message": 'Token is invalid!'
            }), 401

        return f(current_user, *args, **kwargs)

    return decorated



@app.route('/')
def index():
    return jsonify({
        'message': "Hello World!!!"
    })


@app.route('/api/v1/users', methods=['GET'])
@token_required
def get_all_users(current_user):
    if not current_user.admin:
        return jsonify({'message' : 'Cannot perform that function!'})
    users = User.query.all()
    output = []

    for user in users:
        user_data = {}
        user_data['id'] = user.id
        user_data['name'] = user.name
        user_data['email'] = user.email 
        user_data['password'] = user.password
        user_data['admin'] = user.admin
        output.append(user_data)

    return jsonify({
        'users': output
    })

@app.route('/api/v1/user/<email>', methods=['GET'])
@token_required
def get_one_user(current_user, email):
    if not current_user.admin:
        return jsonify({'message' : 'Cannot perform that function!'})
    user = User.query.filter_by(email=email).first()

    if not user:
        return jsonify({
            'message': 'No user found in the Database!'
        })

    user_data = {}
    user_data['id'] = user.id
    user_data['name'] = user.name
    user_data['email'] = user.email 
    user_data['password'] = user.password
    user_data['admin'] = user.admin

    return jsonify({
        'user': user_data
    })
    

@app.route('/api/v1/create_user', methods=['POST'])
def create_user():

    data = request.get_json()

    hashed_pass = generate_password_hash(data['password'], method='sha256')
    
    if data['admin'] == "True":
        admin = True
    else:
        admin = False

    new_user = User(name=data['name'], email=data['email'], password=hashed_pass, admin=admin)
    db.session.add(new_user)
    db.session.commit()

    return jsonify({
        'message': "New User Created!!!"
    })

@app.route('/api/v1/update/<email>', methods=['PUT'])
@token_required
def update_user(current_user, email):
    
    if not current_user.admin:
        return jsonify({'message' : 'Cannot perform that function!'})

    user = User.query.filter_by(email=email).first()
    data = request.get_json()

    if not user:
        return jsonify({
            'message': 'No user found in the Database!'
        })

    hashed_pass = generate_password_hash(data['password'], method='sha256')
    if data['admin'] == "True":
        admin = True
    else:
        admin = False
    
    user.name = data['name']
    user.password = hashed_pass
    user.admin = admin

    db.session.commit()

    return jsonify({
        'message': 'User information Updateed!'
    })
    

@app.route('/api/v1/delete/<email>', methods=['DELETE'])
@token_required
def delete_user(current_user, email):

    if not current_user.admin:
        return jsonify({'message' : 'Cannot perform that function!'})

    user = User.query.filter_by(email=email).first()

    if not user:
        return jsonify({
            'message': 'No user found in the Database!'
        })

    db.session.delete(user)
    db.session.commit()

    return jsonify({
        'message': "User deleted Successfully!"
    })

@app.route('/api/v1/login')
def login():
    auth = request.authorization

    if not auth or not auth.username or not auth.password:
        return make_response('Could not verify', 401, {'WWW-Authenticate' : 'Basic realm="Login required"'})
    
    user = User.query.filter_by(email=auth.username).first()
    
    if not user:
        return make_response('Could not verify', 401, {'WWW-Authenticate' : 'Basic realm="Login required"'})

    if check_password_hash(user.password, auth.password):
        token = jwt.encode({'email' : user.email, 'exp' : datetime.datetime.utcnow() + datetime.timedelta(minutes=30)}, app.config['SECRET_KEY'])
        return jsonify({
            'token': token.decode('UTF-8')
        })

    return make_response('Could not verify', 401, {'WWW-Authenticate' : 'Basic realm="Login required"'})

if __name__ == "__main__":
    manager.run()
    # app.run(debug=True)