from flask_wtf import FlaskForm
from wtforms import SelectField, StringField, TextField, SubmitField, PasswordField, TextAreaField
from wtforms.fields.html5 import SearchField
from wtforms.validators import DataRequired, Length, InputRequired, Email, EqualTo

class SignupForm(FlaskForm):
    email = StringField('Email', [Length(min=6), Email(message="Not a valid email address."), DataRequired()])
    username = StringField('Username', [DataRequired()])
    password = PasswordField('Password', [Length(min=6, message="Select a stronger password."), DataRequired(message="Please enter a password.")])
    confirm = PasswordField('Confirm Your Password', [EqualTo("password", message="Password must match."), DataRequired()])
    submit = SubmitField('Register')

class LoginForm(FlaskForm):
    email = StringField('Email', [Email(message="Not a valid email address."), DataRequired()])
    password = PasswordField('Password', [DataRequired(message="Please enter a password.")])
    submit = SubmitField('Sign in')