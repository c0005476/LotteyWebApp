# IMPORTS
import logging
from functools import wraps
from datetime import datetime
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import check_password_hash
from flask import Blueprint, render_template, flash, redirect, url_for, request, session
import pyotp

from app import db
from models import User
from users.forms import RegisterForm
from users.forms import LoginForm

# CONFIG
users_blueprint = Blueprint('users', __name__, template_folder='templates')

user = User.query.first()
draw_key = user.draw_key

# VIEWS
# view registration


@users_blueprint.route('/register', methods=['GET', 'POST'])
def register():
    # create signup form object
    form = RegisterForm()

    # if request method is POST or form is valid
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        # if this returns a user, then the email already exists in database

        # if email already exists redirect user back to signup page with error message so user can try again
        if user:
            flash('Email address already exists')
            return render_template('register.html', form=form)

        # create a new user with the form data
        new_user = User(email=form.email.data,
                        firstname=form.firstname.data,
                        lastname=form.lastname.data,
                        phone=form.phone.data,
                        password=form.password.data,
                        pin_key=form.pin_key.data,
                        role='user')

        # add the new user to the database
        db.session.add(new_user)
        db.session.commit()

        logging.warning('SECURITY - User registration [%s, %s]', form.email.data, request.remote_addr)

        # sends user to login page
        return redirect(url_for('users.login'))
    # if request method is GET or form not valid re-render signup page
    return render_template('register.html', form=form)


# view user login
@users_blueprint.route('/login', methods=['GET', 'POST'])
def login():

    if not session.get('logins'):
        session['logins'] = 0
    elif session.get('logins') >= 3:
        flash('Number of incorrect logins exceeded')

    form = LoginForm()

    if form.validate_on_submit():
        session['logins'] += 1

        user = User.query.filter_by(email=form.email.data).first()

        if not user or not check_password_hash(user.password, form.password.data):
            if session['logins'] == 3:
                logging.warning('SECURITY - Invalid Login attempt 3 [%s, %s]', form.email.data, request.remote_addr)
                flash('Number of incorrect logins exceeded')
            elif session['logins'] == 2:
                logging.warning('SECURITY - Invalid Login attempt 2 [%s, %s]', form.email.data, request.remote_addr)
                flash('Please check your login details and try again. 1 login attempt remaining')
            else:
                logging.warning('SECURITY - Invalid Login attempt 1 [%s, %s]', form.email.data, request.remote_addr)
                flash('Please check your login details and try again. 2 login attempts remaining')

            return render_template('login.html', form=form)

        if pyotp.TOTP(user.pin_key).verify(form.pin.data):
            session['logins'] = 0

            login_user(user)

            user.last_logged_in = user.current_logged_in
            user.current_logged_in = datetime.now()
            db.session.add(user)
            db.session.commit()
            logging.warning('SECURITY - User login [%s, %s]', form.email.data, request.remote_addr)

            if current_user.role == 'admin':
                return redirect(url_for('admin.admin'))
            else:
                return profile()

        else:
            flash("You have supplied an invalid 2FA token!", "danger")

    return render_template('login.html', form=form)


# view user profile
@login_required
@users_blueprint.route('/profile', methods=['GET', 'POST'])
def profile():
    return render_template('profile.html', name=user.firstname)


# view user account
@login_required
@users_blueprint.route('/account')
def account():
    return render_template('account.html',
                           acc_no=user.id,
                           email=user.email,
                           firstname=user.firstname,
                           lastname=user.lastname,
                           phone=user.phone)


@login_required
@users_blueprint.route('/logout')
def logout():
    logging.warning('SECURITY - Log out [%s, %s, %s]', current_user.id, current_user.email, request.remote_addr)
    logout_user()
    return redirect(url_for('index'))
