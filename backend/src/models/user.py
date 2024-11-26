#MIT License
#
#Copyright (c) 2024 Akarsh Reddy, Himanshu Singh and Prateek Kamath
#
#Permission is hereby granted, free of charge, to any person obtaining a copy
#of this software and associated documentation files (the "Software"), to deal
#in the Software without restriction, including without limitation the rights
#to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
#copies of the Software, and to permit persons to whom the Software is
#furnished to do so, subject to the following conditions:
#
#The above copyright notice and this permission notice shall be included in all
#copies or substantial portions of the Software.
#
#THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
#OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
#SOFTWARE.
from functools import wraps
import uuid
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, UserMixin
from flask import g, jsonify, request, redirect, current_app
try:
 from ..extensions import db
except ImportError:
 from extensions import db
from sqlalchemy.dialects.postgresql import UUID
import jwt

login_manager = LoginManager()

 
class User(db.Model, UserMixin):
    __tablename__ = 'users'
 
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = db.Column(db.String(80), unique=True)
    first_name = db.Column(db.String(100))
    last_name = db.Column(db.String(100))
    password_hash = db.Column(db.String())
    created_on = db.Column(db.DateTime(timezone=True), server_default=db.func.now(), nullable=False)
    updated_on = db.Column(db.DateTime(timezone=True), server_default=db.func.now(), nullable=False, server_onupdate=db.func.now())
 
    def set_password(self,password):
        self.password_hash = generate_password_hash(password)
     
    def check_password(self,password):
        return check_password_hash(self.password_hash,password)
    
    def __repr__(self):
        return '<id {}>'.format(self.id)
    
    def to_json(self):
        return {
            'id': str(self.id),
            'email': self.email,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'created_on': self.created_on,
            'updated_on': self.updated_on
        }
 

@login_manager.user_loader
def load_user(id):
    return User.query.get(id)

@login_manager.request_loader
def load_user_from_request(request):
    user_id = request.args.get('user_id')
    if user_id:
        user = User.query.filter_by(id=user_id).first()
        if user and user.is_authenticated:
            return user
    return None

def token_required():
    def decorator(f):
        @wraps(f)
        def wrap(*args, **kwargs):
            token = None
            if request.method == "OPTIONS":
                # Handle the preflight request
                return '', 204
            if "Authorization" in request.headers:
                token = request.headers["Authorization"].split(" ")[1]
            if not token:
                return jsonify(message = "Authentication Token is missing!", data = None, error = "Unauthorized"), 401
            try:
                data=jwt.decode(token, current_app.config["SECRET_KEY"], algorithms=["HS256"])
                current_user = User.query.filter_by(id=data["user_id"]).first()
                if current_user is None:
                    return jsonify(message = "Invalid Authentication token!", data = None, error = "Unauthorized"), 401
            except Exception as e:
                return jsonify(message = "Something went wrong!", data = None, error = str(e)), 500
            g.user = current_user
            return f(*args, **kwargs)
        
        return wrap
    return decorator