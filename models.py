import os

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import ForeignKey

from flask_bcrypt import Bcrypt

bcrypt = Bcrypt()
db = SQLAlchemy()

class User(db.Model):
    """The main user class"""

    __tablename__ = "users"

    id = db.Column(db.Integer,
                    primary_key = True,
                    autoincrement = True)
    username = db.Column(db.String,
                    nullable = False,
                    unique = True)
    password = db.Column(db.String,
                    nullable = False)
    favorite_cocktails_id = db.Column(db.Integer,
                    ForeignKey('cocktails.id'))
    
    @classmethod
    def register(cls, username, password):
        """Register your username and password"""

        hashed_pw = bcrypt.generate_password_hash(password).decode('UTF-8')

        user = User(
            username=username,
            password=hashed_pw,
        )

        db.session.add(user)
        return user
    
    @classmethod
    def authenticate(cls, username, password):
        """authenticate user with username and password"""
        user = cls.query.filter_by(username=username).first()

        if user:
            is_auth = bcrypt.check_password_hash(user.password, password)
            if is_auth:
                return user
        
        return False

class Cocktail(db.Model):
    """The cocktail class"""

    __tablename__ = "cocktails"

    id = db.Column(db.Integer,
                    primary_key = True)
    name = db.Column(db.String)
    
    # more information? 

def connect_db(app):
    """connect this database to the flask app."""

    db.app = app
    db.init_app(app)