import os
from flask import Flask, redirect, render_template, g, session, request, jsonify, flash
import requests
import itertools
from sqlalchemy.exc import IntegrityError
import json

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


def login(user):
    """login a user"""
    session[CURR_USER_KEY] = user.id

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


#_____USER METHODS GO BELOW_____#

@app.route('/login', methods=['GET', 'POST'])
def login_page():
    form = RegisterUserForm()

    if form.validate_on_submit():
        user = User.authenticate(form.username.data,
                                form.password.data)
        if user:
            login(user)
            flash(f"Hello, {user.username}!", "success")
            return redirect('/')
    
        flash('Invalid credentials', 'danger')

        
    return render_template('/users/login.html', form = form)

@app.route('/register', methods=['GET', 'POST'])
def register_user():
    """Register user. IS NOT WORKING -- TYPE ERROR??"""

    form = RegisterUserForm()

    if form.validate_on_submit():
        try:
            user = User.register(
                username = form.username.data,
                password = form.password.data,
            )
            db.session.commit()
    
        except IntegrityError:
            flash('Username already taken', 'danger')
            return render_template('/users/register.html', form=form)
    
        login(user)

        return redirect('/')

    else:
        return render_template('/users/register.html', form = form)

@app.route('/logout', methods=["POST"])
def logout_user():
    """logout current user"""
    logout()
    return render_template('home.html')

#_______COCKTAIL API METHODS GO BELOW_______#

@app.route('/random', methods=['GET'])
def random_cocktail():
    """get a random cocktail from the api"""
    random = requests.get(URL + 'random.php').json()
    random_cocktail = random['drinks']
    ingredients = condense_ingredients(random_cocktail[0])
    return render_template('/cocktails/random.html', random=random_cocktail[0], ingredients = ingredients)

def condense_ingredients(obj):
    """A method to condense ingredients to be readable"""
    ingredients = []
    for x in range(1, 15, 1):
        if obj[f"strIngredient{x}"]:
            ingredient = obj[f"strIngredient{x}"]
            if obj[f'strMeasure{x}']:
                ingredient = obj[f"strIngredient{x}"] + ', ' + obj[f'strMeasure{x}']
            ingredients.append(ingredient)
    return ingredients;


@app.route('/favorite', methods=["POST"])
def favorite_cocktail():
    """Add the cocktail to the database and to the User"""

@app.route('/search/ingredient', methods=["POST", "GET"])
def search_cocktail():
    """search the cocktail API by ingredients, using a drop down menu"""
    ingredient = request.args

@app.route('/search/name', methods=["GET", "POST"])
def search_ingredient():
    """search the cocktail API by name"""