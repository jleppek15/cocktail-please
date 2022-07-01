from flask import Flask, redirect, render_template, g, session
import requests
import os


from models import db, connect_db
from forms import 

CURR_USER_KEY = "curr_user"

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///playlist-app'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = True

connect_db(app)
db.create_all()

app.config['SECRET_KEY'] = "so-secret"

URL = 'www.thecocktaildb.com/api/json/v1/1/'

@app.before_request
def check_user():
    """Check to see if we are logged in and add user to flask g"""


def login():
    """login a user"""
    session[CURR_USER_KEY] = user.id

def logout():
    """log the user out"""
    g.user = None
    if CURR_USER_KEY in session:
        del session[CURR_USER_KEY]
    pass


@app.route
def show_home():
    render_template('home.html')
