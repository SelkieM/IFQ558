from . import db
from flask_login import UserMixin
from sqlalchemy.sql import func
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, SelectField, IntegerField


# DATABSE CLASSES

# User Class
# UserMixin is a class that has some default methods that we can use
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(150))
    last_name = db.Column(db.String(150))
    email = db.Column(db.String(150), unique=True)
    password = db.Column(db.String(150))


# Book class
class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150))
    price = db.Column(db.Integer)
    description = db.Column(db.String(150))
    image = db.Column(db.String(150))
    quantity = db.Column(db.Integer, default=0)
    category = db.Column(db.String(150))


# Cart Items class
class Cart(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    book_id = db.Column(db.Integer)


# Order class
class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    status = db.Column(db.String(150))
    first_name = db.Column(db.String(150))
    last_name = db.Column(db.String(150))
    email = db.Column(db.String(150))
    phone = db.Column(db.String(150))
    address = db.Column(db.String(150))
    total_cost = db.Column(db.Integer)
    date = db.Column(db.DateTime(timezone=True), default=func.now())


# FORM CLASSES

# Sign Up Form
class SignUpForm(FlaskForm):
    first_name = StringField('First Name')
    last_name = StringField('Last Name')
    email = StringField('Email')
    password1 = PasswordField('Password')
    password2 = PasswordField('Confirm Password')
    submit = SubmitField('Sign Up')


# Login Form
class LoginForm(FlaskForm):
    email = StringField('Email')
    password = PasswordField('Password')
    submit = SubmitField('Login')


# Order Form
class OrderForm(FlaskForm):
    status = SelectField('Status', choices=[
                         ('Pending', 'Pending'), ('Shipped', 'Shipped')])
    first_name = StringField('First Name')
    last_name = StringField('Last Name')
    email = StringField('Email')
    phone = StringField('Phone')
    address = StringField('Address')
    total_cost = IntegerField('Total Cost')
    submit = SubmitField('Confirm Order')
