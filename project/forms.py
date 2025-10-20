from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms.fields import SubmitField, StringField, PasswordField, TextAreaField, SelectField, DecimalField, RadioField
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

# Order Management Flow

class CheckoutForm(FlaskForm):
    firstname = StringField('First Name', validators=[InputRequired(), Length(max=100)])
    lastname = StringField('Last Name', validators=[InputRequired(), Length(max=100)])
    email = StringField('Email', validators=[InputRequired(), Email(), Length(max=120)]) 
    shipping_address = StringField('Address', validators=[InputRequired(), Length(max=200)])
    shipping_city = StringField('City', validators=[InputRequired(), Length(max=100)])
    shipping_state = StringField('State', validators=[InputRequired(), Length(max=100)])
    shipping_zip = StringField('ZIP Code', validators=[InputRequired(), Length(max=20)])
    shipping_country = StringField('Country', validators=[InputRequired(), Length(max=100)])
    phone = StringField('Phone Number', validators=[InputRequired(),
        Regexp(r'^\+?1?\d{9,15}$', message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed.")
    ])

    payment_method = RadioField('Payment Method', 
                                choices = [('credit card', 'Credit Card'),
                                           ('paypal', 'Pay Pal'),
                                           ('stripe', 'Stripe')],
                                default='credit card',
                                validators=[InputRequired()])
    
    account_name = StringField('Account Name', validators=[InputRequired(), Length(max=100)])
    account_number = StringField('Account Number', validators=[InputRequired(), Length(min=4, max=16)])
    submit = SubmitField('Confirm and Place Order')

# Forms to handle Order, Checkout, Upload, Edit, Remove Artworks

class ArtworkUploadForm(FlaskForm):
    title = StringField('Artwork Title', validators=[InputRequired(), Length(min=1, max=255)])
    description = TextAreaField('Description', validators=[Optional(), Length(max=1000)])
    medium = SelectField('Medium', validators=[Optional()], choices=[
        ('', 'Select Medium'),
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
    height = DecimalField('Height (cm)', validators=[InputRequired(), NumberRange(min=1, max=999.99)], 
                         places=2, render_kw={'step': '0.01'})
    width = DecimalField('Width (cm)', validators=[InputRequired(), NumberRange(min=1, max=999.99)], 
                        places=2, render_kw={'step': '0.01'})
    category = StringField('Category', validators=[Optional(), Length(max=50)])
    art_origin = StringField('Art Origin', validators=[Optional(), Length(max=100)])
    year_of_publish = StringField('Year Published', validators=[Optional(), Length(max=4)])
    price = DecimalField('Monthly Lease Price ($)', validators=[InputRequired(), NumberRange(min=1, max=99999999.99)], 
                        places=2, render_kw={'step': '0.01'})
    image = FileField('Artwork Image', validators=[
        FileAllowed(['jpg', 'jpeg', 'png', 'gif'], 'Images only!')
    ])
    submit = SubmitField('Upload Artwork')

class ArtworkEditForm(FlaskForm):
    title = StringField('Artwork Title', validators=[InputRequired(), Length(min=1, max=255)])
    description = TextAreaField('Description', validators=[Optional(), Length(max=1000)])
    medium = SelectField('Medium', validators=[Optional()], choices=[
        ('', 'Select Medium'),
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
    height = DecimalField('Height (cm)', validators=[InputRequired(), NumberRange(min=1, max=999.99)], 
                         places=2, render_kw={'step': '0.01'})
    width = DecimalField('Width (cm)', validators=[InputRequired(), NumberRange(min=1, max=999.99)], 
                        places=2, render_kw={'step': '0.01'})
    category = StringField('Category', validators=[Optional(), Length(max=50)])
    art_origin = StringField('Art Origin', validators=[Optional(), Length(max=100)])
    year_of_publish = StringField('Year Published', validators=[Optional(), Length(max=4)])
    price = DecimalField('Monthly Lease Price ($)', validators=[InputRequired(), NumberRange(min=1, max=99999999.99)], 
                        places=2, render_kw={'step': '0.01'})
    status = SelectField('Status', validators=[InputRequired()], choices=[
        ('available', 'Available'),
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