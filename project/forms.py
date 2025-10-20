from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms.fields import SubmitField, StringField, PasswordField, TextAreaField, SelectField, DecimalField
from wtforms.validators import InputRequired, Email, Length, Regexp, ValidationError, EqualTo, Optional, NumberRange
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

class ArtworkUploadForm(FlaskForm):
    title = StringField('Artwork Title', validators=[InputRequired(), Length(min=1, max=200)])
    artist_name = StringField('Artist Name', validators=[InputRequired(), Length(min=1, max=100)])
    description = TextAreaField('Description', validators=[InputRequired(), Length(min=10, max=1000)])
    medium = SelectField('Medium', validators=[InputRequired()], choices=[
        ('Oil on Canvas', 'Oil on Canvas'),
        ('Acrylic on Canvas', 'Acrylic on Canvas'),
        ('Watercolor', 'Watercolor'),
        ('Mixed Media', 'Mixed Media'),
        ('Digital Art', 'Digital Art'),
        ('Photography', 'Photography'),
        ('Sculpture', 'Sculpture'),
        ('Print', 'Print'),
        ('Other', 'Other')
    ])
    dimensions = StringField('Dimensions', validators=[InputRequired(), Length(min=1, max=50)], 
                           render_kw={'placeholder': 'e.g., 24x36 inches'})
    price = DecimalField('Price ($)', validators=[InputRequired(), NumberRange(min=1, max=100000)], 
                        places=2, render_kw={'step': '0.01'})
    image = FileField('Artwork Image', validators=[
        FileAllowed(['jpg', 'jpeg', 'png', 'gif'], 'Images only!')
    ])
    submit = SubmitField('Upload Artwork')

class ArtworkEditForm(FlaskForm):
    title = StringField('Artwork Title', validators=[InputRequired(), Length(min=1, max=200)])
    artist_name = StringField('Artist Name', validators=[InputRequired(), Length(min=1, max=100)])
    description = TextAreaField('Description', validators=[InputRequired(), Length(min=10, max=1000)])
    medium = SelectField('Medium', validators=[InputRequired()], choices=[
        ('Oil on Canvas', 'Oil on Canvas'),
        ('Acrylic on Canvas', 'Acrylic on Canvas'),
        ('Watercolor', 'Watercolor'),
        ('Mixed Media', 'Mixed Media'),
        ('Digital Art', 'Digital Art'),
        ('Photography', 'Photography'),
        ('Sculpture', 'Sculpture'),
        ('Print', 'Print'),
        ('Other', 'Other')
    ])
    dimensions = StringField('Dimensions', validators=[InputRequired(), Length(min=1, max=50)])
    price = DecimalField('Price ($)', validators=[InputRequired(), NumberRange(min=1, max=100000)], 
                        places=2)
    status = SelectField('Status', validators=[InputRequired()], choices=[
        ('available', 'Available'),
        ('sold', 'Sold'),
        ('pending', 'Pending'),
        ('unavailable', 'Unavailable')
    ])
    submit = SubmitField('Update Artwork')

class UserManagementForm(FlaskForm):
    firstname = StringField('First Name', validators=[InputRequired(), Length(max=50)])
    lastname = StringField('Last Name', validators=[InputRequired(), Length(max=50)])
    email = StringField('', validators=[InputRequired(), Email(), Length(max=120)])
    role = SelectField('Role', validators=[InputRequired()], choices=[
        ('customer', 'Customer'),
        ('artist', 'Artist'),
        ('admin', 'Admin')
    ])
    submit = SubmitField('Update User')

class OrderStatusForm(FlaskForm):
    status = SelectField('Order Status', validators=[InputRequired()], choices=[
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('processing', 'Processing'),
        ('shipped', 'Shipped'),
        ('in_transit', 'In Transit'),
        ('delivered', 'Delivered'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
        ('refunded', 'Refunded')
    ])
    submit = SubmitField('Update Status')