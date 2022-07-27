from enum import auto
import os

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import ForeignKey

from flask_bcrypt import Bcrypt

bcrypt = Bcrypt()
db = SQLAlchemy()

class User(db.Model):
    """The main user class"""

    __tablename__ = 'users'

    id = db.Column(db.Integer,
                    primary_key = True,
                    autoincrement = True)

    username = db.Column(db.String,
                    nullable = False,
                    unique = True)

    password = db.Column(db.String,
                    nullable = False)

    favorite_cocktails = db.relationship('Cocktail', secondary='favorites', backref='users')
    
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

    __tablename__ = 'cocktails'

    api_id = db.Column(db.Integer,
                    primary_key = True,
                    nullable = False)

    name = db.Column(db.Text,
                    nullable=False)

    favorite_users = db.relationship('User', secondary='favorites', backref='cocktails')

    @classmethod
    def add_cocktail(cls, api_id, name):
        cocktail = Cocktail(
            api_id = api_id,
            name = name,
        )
        db.session.add(cocktail)
        return cocktail
    
    # more information? 


class Favorites(db.Model):
    """User and cocktail ids"""
    
    __tablename__ = 'favorites'
    
    id = db.Column(db.Integer,
                    autoincrement=True,
                    primary_key = True)

    user_id = db.Column(db.Integer,
                    db.ForeignKey('users.id', 
                    ondelete="cascade"))

    cocktail_id = db.Column(db.Integer,
                    db.ForeignKey('cocktails.api_id', 
                    ondelete="cascade"))
    



def connect_db(app):
    """connect this database to the flask app."""

    db.app = app
    db.init_app(app)