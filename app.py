import os
from flask import Flask, redirect, render_template, g, session, request, jsonify, flash
import requests
import itertools
from sqlalchemy.exc import IntegrityError
import json

from models import db, connect_db, User, Cocktail, Favorites
from forms import RegisterUserForm, SearchForm, SignInForm

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
    if CURR_USER_KEY in session:
        g.user = User.query.get(session[CURR_USER_KEY])
    
    else:
        g.user = None

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
    form = SignInForm()

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
                email = form.email.data
            )
            db.session.commit()
    
        except IntegrityError:
            flash('Username already taken', 'danger')
            return render_template('/users/register.html', form=form)
    
        login(user)

        return redirect('/')

    else:
        return render_template('/users/register.html', form = form)

@app.route('/logout')
def logout_user():
    """logout current user"""
    logout()
    return render_template('home.html')

@app.route('/favorites')
def show_favorites():
    """show all user favorites"""
    user = g.user
    favorite_cocktails = g.user.favorite_cocktails
    print(favorite_cocktails)
    return render_template('users/favorites.html', favorite_cocktails = favorite_cocktails, user = user)

@app.route('/user/profile-edit', methods=['GET', 'POST'])
def edit_user():
    user = g.user
    form = RegisterUserForm(obj=user)
    if form.validate_on_submit():
        if User.authenticate(g.user.username,form.password.data):
            flash("Success! Profile edited.", "success")
            user.username = form.username.data
            user.email = form.email.data

            db.session.add(user)
            db.session.commit()
            return redirect(f'/favorites')
        else:
            flash("Password was incorrect, try again!", "danger")

    return render_template("users/profile-edit.html", user=user, form=form)

@app.route('/user/delete', methods=['GET','POST'])
def delete_user():
    """Delete user"""
    user = g.user
    logout()
    db.session.delete(user)
    db.session.commit()
    flash("Your account has been deleted!", "danger")
    return redirect('/')


#_______COCKTAIL API METHODS GO BELOW_______#

@app.route('/random', methods=['GET'])
def random_cocktail():
    """get a random cocktail from the api"""
    random = requests.get(URL + 'random.php').json()
    random_cocktail = random['drinks']
    ingredients = condense_ingredients(random_cocktail[0])
    return render_template('/cocktails/cocktail.html', random=random_cocktail[0], ingredients = ingredients)

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

@app.route('/cocktail/<int:idDrink>', methods=["GET"])
def show_cocktail_id(idDrink):
    """show a cocktail by its API_id"""
    cocktail = requests.get(URL + f'lookup.php?i={idDrink}').json()
    cocktail_data = cocktail['drinks']
    ingredients = condense_ingredients(cocktail_data[0])
    return render_template('cocktails/cocktail.html', random = cocktail_data[0], ingredients = ingredients)


@app.route('/favorite/<int:idDrink>', methods=["POST"])
def favorite_cocktail(idDrink):
    """Add the cocktail to the database and to the User"""
    cocktail = requests.get(URL + f'lookup.php?i={idDrink}').json()
    favorite_cocktail = cocktail['drinks']
    fct = favorite_cocktail[0]
    
    new_favorite_cocktail = Cocktail.add_cocktail(api_id=idDrink, name=fct['strDrink'])
    
    user_favorite = g.user.favorite_cocktails

    if idDrink in user_favorite:
        g.user.favorite_cocktails = [favorite for favorite in user_favorite if favorite != idDrink]
    else:
        g.user.favorite_cocktails.append(new_favorite_cocktail)

    db.session.commit()

    return redirect('/favorites')


@app.route('/search/ingredient', methods=['POST', 'GET'])
def search_ingredient():
    """function for searching by ingredient"""
    form = SearchForm()
    if form.validate_on_submit():
        return redirect(f'/search_results/ingredient/{form.search.data}')
    return render_template('/search/ingredient.html', form = form)


@app.route('/search/name', methods=['POST', 'GET'])
def search_name():
    """function for searching by name of cocktail"""
    form = SearchForm()
    if form.validate_on_submit():
        return redirect(f'/search_results/name/{form.search.data}')

    return render_template('/search/name.html', form = form)

@app.route('/search_results/ingredient/<query>', methods=["GET"])
def search_results_ingredient(query):
    """search the cocktail API by ingredients, using a query"""
    ingredient = query
    cocktails = requests.get(URL + f'filter.php?i={ingredient}').json()
    if cocktails['drinks']:
        cocktail_data = cocktails['drinks']
        return render_template('cocktails/list.html', list=cocktail_data)
    return render_template('cocktails/list.html', list = cocktail_data)

@app.route('/search_results/name/<query>', methods=["GET"])
def search_results_name(query):
    """search the cocktail API by name"""
    name = query
    cocktail = requests.get(URL + f'search.php?s={name}').json()
    if cocktail['drinks']:
        cocktail_data = cocktail['drinks']
        ingredients = condense_ingredients(cocktail_data[0])
        return render_template('cocktails/cocktail.html', random = cocktail_data[0], ingredients = ingredients)
    else:
        return render_template('404.html')