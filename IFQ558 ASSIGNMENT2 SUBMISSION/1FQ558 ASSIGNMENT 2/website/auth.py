from flask import Blueprint, render_template, request, flash, url_for, redirect
from .models import User
from . import db
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy.exc import IntegrityError
from flask_login import login_user, login_required, logout_user
from .models import LoginForm, SignUpForm


# create blueprint
auth = Blueprint('auth', __name__)


# ROUTES

# route to login user
@auth.route('/login', methods=['GET', 'POST'])
def login():
    # create login form object
    form = LoginForm()
    # handle POST request
    if request.method == 'POST':
        # get data from form
        email = form.email.data
        password = form.password.data
        # check if user exists
        user = User.query.filter_by(email=email).first()
        if user:
            # check if password is correct
            if check_password_hash(user.password, password):
                flash('Logged in successfully!')
                # log in user
                login_user(user, remember=True)
                # return to order page
                return redirect(url_for('views.confirm_order'))
            else:
                flash('Invalid Password.')
        else:
            flash('User not found. Please sign up.')
            return redirect(url_for('auth.signup'))

    return render_template('login.html', form=form)


# route to logout user
@auth.route('/logout')
@login_required
def logout():
    # log out user
    logout_user()
    # flash message
    flash('Logged out successfully!')
    # return to home page
    return redirect(url_for('views.home'))


# route to sign up user
@auth.route('/sign-up', methods=['GET', 'POST'])
def signup():
    # create sign up form object
    form = SignUpForm()
    # handle POST request
    if request.method == 'POST':
        # get data from form
        first_name = form.first_name.data
        last_name = form.last_name.data
        email = form.email.data
        password1 = form.password1.data
        password2 = form.password2.data

        # basic validation
        if len(email) < 4:
            flash('Email must be at least 4 characters.')
        elif len(first_name) < 2:
            flash('Name must be at least 2 characters.')
        elif len(password1) < 7:
            flash('Password must be at least 7 characters.')
        elif password1 != password2:
            flash('Passwords do not match.')
        else:
            # add new user to database
            new_user = User(email=email, first_name=first_name, last_name=last_name,
                            password=generate_password_hash(password1, method='sha256'))
            try:
                db.session.add(new_user)
                db.session.commit()
                flash('Account Created!', category='success')
                # log in user
                login_user(new_user, remember=True)

            # handle duplicate email error (user already exists)
            except IntegrityError:
                flash(
                    'User with that email already exists. Please log in instead.')
                return redirect(url_for('auth.login'))

            # return to order page
            return redirect(url_for('views.confirm_order'))

    return render_template('sign_up.html', form=form)
