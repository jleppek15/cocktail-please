from turtle import title
from wtforms import SelectField, StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Email, Length
from flask_wtf import FlaskForm


class RegisterUserForm(FlaskForm):
    """form for registering a user"""
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[Length(min=6)])

class SearchForm(FlaskForm):
    """form for searching the cocktail API"""
    search = StringField('search', validators=[DataRequired()])
    submit = SubmitField('Search',
                            render_kw={'class':'btn btn-success btn-block'})