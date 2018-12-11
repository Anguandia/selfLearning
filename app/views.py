from flask import render_template, flash, redirect, url_for, request
from app.forms import LoginForm, RegistrationForm
from app import validation, app
# from flask_login import current_user, log


@app.route('/signup', methods=['POST', 'GET'])
def signup():
    form = RegistrationForm()
    if form:
        data = {}
        data['name'] = form.name.data
        data['email'] = form.email.data
        data['password'] = form.password.data
        result = validation.validateSignup(data)[0]
        if isinstance(result, dict):
            for i in result:
                flash(result[i])
        else:
            flash(result)
    return render_template('signup.html', title='SignUp', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    data = {}
    if form.validate_on_submit():
        data['identity'] = form.name.data
        data['password'] = form.password.data
        result = validation.validateLogin(data)[1]
        if isinstance(result, dict):
            for i in result:
                flash(result[i])
        else:
            flash(result)
    return render_template('login.html', form=form, title='login')


from app import app
