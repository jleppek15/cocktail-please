import os
from flask import Flask, redirect, render_template, g, session, request, jsonify, flash
import requests
import json
from sqlalchemy.exc import IntegrityError


from models import db, connect_db, User, Cocktail
from forms import RegisterUserForm

CURR_USER_KEY = "curr_user"

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = (os.environ.get('DATABASE_URL', 'postgresql:///cocktail_please'))
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = True

connect_db(app)
db.create_all()

app.config['SECRET_KEY'] = "so-secret"

URL = 'http://www.thecocktaildb.com/api/json/v1/1/'

@app.before_request
def check_user():
    """Check to see if we are logged in and add user to flask g"""


def login():
    """login a user"""
    session[CURR_USER_KEY] = User.id

def logout():
    """log the user out"""
    g.user = None
    if CURR_USER_KEY in session:
        del session[CURR_USER_KEY]
    pass


@app.route('/')
def redirect_home():
    return redirect('/home')

@app.route('/home', methods=['GET', 'POST'])
def show_home():
    return render_template('home.html')

@app.route('/user')
def user_page():
    form = RegisterUserForm()
    return render_template('/users/user.html', form = form)

@app.route('/register', methods=['GET', 'POST'])
def register_user():
    form = RegisterUserForm()

    if form.validate_on_submit():
        try:
            username = form.data.username
            password = form.data.password
            user = User.register(username=username, password=password)
            db.session.commit()
    
        except IntegrityError:
            flash('Username already taken', 'danger')
            return render_template('/users/register.html', form=form)
    
        login(user)

        return redirect('/home')

    else:
        return render_template('/users/register.html', form = form)

@app.route('/login', methods=['POST'])
def login_user():
    form = RegisterUserForm()

    if form.validate_on_submit():
        try:
            username = form.data.username
            password = form.data.password
            user = User.register(username=username, password=password)
            db.session.commit()
    
        except IntegrityError:
            flash('Username already taken', 'danger')
            return render_template('/users/register.html', form=form)
    
        login(user)

        return redirect('/home')

    else:
        return redirect('/user', form = form)

@app.route('/random', methods=['GET'])
def random_cocktail():
    random = requests.get(URL + 'random.php').json()
    random_cocktail = random['drinks']
    ingredients = condense_ingredients(random_cocktail[0])
    print(ingredients)
    return render_template('random.html', random=random_cocktail[0], ingredients = ingredients)

def condense_ingredients(obj):
    ingredients = []
    for x in range(1, 15, 1):
        if obj[f"strIngredient{x}"]:
            ingredients.append(obj[f"strIngredient{x}"])
    
    return ingredients;