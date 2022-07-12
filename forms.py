from turtle import title
from wtforms import SelectField, StringField, PasswordField
from wtforms.validators import DataRequired, Email, Length
from flask_wtf import FlaskForm


class RegisterUserForm(FlaskForm):
    """form for registering a user"""
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[Length(min=6)])