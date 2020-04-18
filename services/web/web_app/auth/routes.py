from flask import render_template, redirect, url_for, flash, request
from flask_babel import _
from flask_login import current_user, login_required
from flask_login import login_user, logout_user
from werkzeug.urls import url_parse

from web_app import db
from web_app.auth import blueprint
from web_app.auth.forms import LoginForm, RegistrationForm, \
    ResetPasswordRequestForm, ResetPasswordForm
from web_app.models import User


# from app.auth.email import send_password_reset_email


@blueprint.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('app.index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()

        if user is None or not user.check_password(form.password.data):
            print("Invalid username or password")
            flash(_('Invalid username or password'))
            return redirect(url_for('auth.login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('app.index')
        return redirect(next_page)
    return render_template('auth/login.html', title=_('Sign In'), form=form)


@blueprint.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('app.index'))


@blueprint.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('app.index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash(_('Congratulations, you are now a registered user!'))
        return redirect(url_for('auth.login'))
    return render_template('auth/register.html', title=_('Register'),
                           form=form)


@blueprint.route('/reset_password_request', methods=['GET', 'POST'])
def reset_password_request():
    if current_user.is_authenticated:
        return redirect(url_for('app.index'))
    form = ResetPasswordRequestForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            print("send user")
            # send_password_reset_email(user)
        flash(
            _('Check your email for the instructions to reset your password'))
        return redirect(url_for('auth.login'))
    return render_template('auth/reset_password_request.html',
                           title=_('Reset Password'), form=form)


@blueprint.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    if current_user.is_authenticated:
        return redirect(url_for('app.index'))
    user = User.verify_reset_password_token(token)
    if not user:
        return redirect(url_for('app.index'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        user.set_password(form.password.data)
        db.session.commit()
        flash(_('Your password has been reset.'))
        return redirect(url_for('auth.login'))
    return render_template('auth/reset_password.html', form=form)


@blueprint.route('/settings/index')
@login_required
def settings():
    reset_form = ResetPasswordForm()
    reg_form = RegistrationForm()
    users = User.query.all()
    return render_template('auth/Settings.html', reset_form=reset_form,
                           reg_form=reg_form, users=users)


@blueprint.route('/settings/new_user', methods=['POST'])
@login_required
def new_user():
    reset_form = ResetPasswordForm()
    reg_form = RegistrationForm()
    users = User.query.all()

    if reg_form.validate_on_submit():
        print("elo")
        user = User(
            username=reg_form.username.data,
            email=reg_form.email.data,
            admin=reg_form.admin.data)
        user.set_password(reg_form.password.data)
        db.session.add(user)
        db.session.commit()
        flash(_('Congratulations, you are now a registered user!'))

    # handle the register form
    # render the same template to pass the error message
    # or pass `form.errors` with `flash()` or `session` then redirect to /
    return render_template('auth/Settings.html', reset_form=reset_form,
                           reg_form=reg_form, users=users)


@blueprint.route('/settings/change_pass', methods=['POST'])
@login_required
def change_pass():
    reset_form = ResetPasswordForm()
    reg_form = RegistrationForm()
    users = User.query.all()

    if reset_form.validate_on_submit():
        print("ola")
        current_user.set_password(reset_form.password.data)
        db.session.commit()
        flash(_('Your password has been reset.'))
        return redirect(url_for('auth.settings'))

    # handle the login form
    # render the same template to pass the error message
    # or pass `form.errors` with `flash()` or `session` then redirect to /
    return render_template('auth/Settings.html', reset_form=reset_form,
                           reg_form=reg_form, users=users)


@blueprint.route(
    '/settings/delete_user/<token>',
    methods=[
        'GET',
        'POST'])
@login_required
def delete_user(token):
    reset_form = ResetPasswordForm()
    reg_form = RegistrationForm()
    users = User.query.all()

    User.query.filter_by(id=token).delete()
    db.session.commit()

    return render_template('auth/Settings.html', reset_form=reset_form,
                           reg_form=reg_form, users=users)
