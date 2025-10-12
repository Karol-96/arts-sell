from flask_wtf import FlaskForm
from wtforms.fields import SubmitField, StringField, PasswordField, TextAreaField
from wtforms.validators import InputRequired, Email, Length, Regexp, ValidationError, EqualTo, Optional
from project.db import check_username, check_email

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[InputRequired(), Length(min=4, max=25)])
    password = PasswordField('Password', validators=[
        InputRequired(), 
        Length(min=8, message="Password must be at least 8 characters long.")
    ])
    confirm_password = PasswordField('Confirm Password', validators=[InputRequired(), EqualTo('password', message="Passwords must match.")])
    firstname = StringField('First Name', validators=[InputRequired(), Length(max=50)])
    lastname = StringField('Last Name', validators=[InputRequired(), Length(max=50)])
    email = StringField('Email', validators=[InputRequired(), Email(), Length(max=120)])
    submit = SubmitField('Register')

    def validate_username(self, field):
        if check_username(field.data):
            raise ValidationError("Username already taken.")
    
    def validate_email(self, field):
        if check_email(field.data):
            raise ValidationError("Email already registered.")

class ArtistRegistrationForm(RegistrationForm):
    submit = SubmitField('Register as Artist')

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[InputRequired(), Length(min=4, max=25)])
    password = PasswordField('Password', validators=[InputRequired(), Length(min=8)])
    submit = SubmitField('Login')

class ProfileForm(FlaskForm):
    firstname = StringField('First Name', validators=[InputRequired(), Length(max=50)])
    lastname = StringField('Last Name', validators=[InputRequired(), Length(max=50)])
    email = StringField('Email', validators=[InputRequired(), Email(), Length(max=120)])
    phone = StringField('Phone Number', validators=[InputRequired(), 
            Regexp(r'^\+?1?\d{9,15}$',
            message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed.")
    ])
    bio = TextAreaField('Bio (Optional)', validators=[Optional(), Length(max=500)])
    address = TextAreaField('Address (Optional)', validators=[Optional(), Length(max=200)])
    city = StringField('City (Optional)', validators=[Optional(), Length(max=100)])
    state = StringField('State (Optional)', validators=[Optional(), Length(max=100)])
    zip = StringField('ZIP Code (Optional)', validators=[Optional(), Length(max=20)])
    country = StringField('Country (Optional)', validators=[Optional(), Length(max=100)])
    submit = SubmitField('Update Profile')

# Forms to handle Order, Checkout, Upload, Edit, Remove Artworks