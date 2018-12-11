from .models import User, Order
from . import db
from flask import request


def validateSignup(data):
    for key in ['name', 'email', 'password']:
        if key not in data:
            return ('{} key missing or incorrect'.format(key), 400)
    for field in data:
        if not data[field]:
            return ('please fill in {}'.format(field), 406)
        name = data['name']
        email = data['email']
        password = data['password']
    if db.fetch_user_email(email):
        return ('account already exists, please login', 403)
    elif db.fetch_user_name(name):
        return (
            'another account in same name, please use a different name', 409)
    else:
        if validatePassword(password) == password:
            if validateEmail(email):
                if validateName(name):
                    user = User(name, email, password)
                    if db.register(user):
                        res = (db.register(user), 201)
                    else:
                        res = ('signup failed', 500)
                else:
                    res = 'name must maximum 25 characters including space(s)!'
            else:
                res = ('invalid email address', 406)
        else:
            res = (validatePassword(password), 406)
    return res


def validateLogin(data):
    if 'identity' not in data:
        response = (400, 'check email or name key')
    elif 'password' not in data:
        response = (400, 'check password key')
    else:
        # single data field with nameor email
        name = data['identity']
        password = data['password']
        if name:
            if isinstance(validateUser(name), dict):
                user = db.to_object(validateUser(name))
                if password:
                    print(password)  #
                    if user.validate_password(password):
                        print('validated')  # debug
                        if user.generate_token():
                            token = user.generate_token()
                            response = (
                                    200, {'user': '{}'.format(name), 'Id':
                                          '{}'.format(user.decode_token(token)),
                                          'token': '{}'.format(str(token))}
                                        )
                        else:
                            response = (500, 'internal error')
                    else:
                        response = (401, 'wrong password')
                else:
                    response = (406, 'please enter password')
            else:
                response = validateUser(name)
        else:
            response = (406, 'please enter name or email')
    return response


def validateEditUser(data, key, userid):
    user = db.fetch_user(userid)
    if user:
        usr = db.to_object(user)
        new = data[key[6:].lower()]
        if key == 'changePassword':
            if 'current password' in data:
                old = data['current password']
                if old:
                    if usr.validate_password(old):
                        value = usr.set_password(new)
                    else:
                        return ('wrong current password', 401)
                else:
                    return ('please submit current password', 401)
            else:
                return ('problem with key \'current password\'', 401)
        else:
            value = new
        try:
            res = db.edit_user(userid, key, value)
            if res == '{} changed'.format(key[6:].lower()):
                return (res, 200)
            else:
                return ('internal server error, {}'.format(res), 500)
        except Exception as error:
            return (error, 500)
    else:
        return ('no user {}'.format(userid), 404)


def validateOrder(data):
    for field in ['origin', 'destination', 'reciever']:
        if field not in data:
            return ('{} key missing or incorrect'.format(field), 400)
        if not data[field]:
            return ('please submit {}'.format(field), 400)
    order = Order(
        User.decode_token(request.headers.get('Authorization').split(" ")[1]),
        data['reciever'],
        data['origin'],
        data['destination'],
         )
    return (db.saveOrder(order), 201)


def validateOrderEdit(data, parcelid, action):
    order = db.get_order(parcelid)
    if order:
        if order['status'] == 'delivered':
            result = ('parcel already delivered', 406)
        if action == 'cancel':
            key = 'status'
            value = 'canceled'
        else:
            key = action[6:].lower()
            value = data[key]
        result = (db.update_order(value, parcelid, key), 200)
    else:
        result = ('order not found', 404)
    return result


def validateOrderUpdate(data, parcelid, actions):
    order = db.get_order(parcelid)
    if order:
        results = {}
        for key in actions:
            if data[key]:
                result = db.update_order(request.json[key], parcelid, key)
                results[key] = result
            else:
                result = 'no value given for {}'.format(key)
                results[key] = result
            return results


def validateEmail(email):
    required = ['@', '.']
    if set(required) & set(email) == set(required):
        a = email.index('@')
        b = email.rindex('.')
        if 0 < a < (b - 2) < (len(email) - 3):
            if email.count('@') == 1:
                return email


def validateName(name):
    if len(name) < 25:
        return name


def validatePassword(password):
    if 6 <= len(password) <= 12:
        if any(i.islower() for i in password):
            if any(i.isupper() for i in password):
                if any(i.isdigit() for i in password):
                    if set('!@#$%&*') & set(password):
                        res = password
                    else:
                        res = 'password must have atleast a special character'
                else:
                    res = 'password must have atleast a decimal'
            else:
                res = 'password must have atleast an uppercase alphabet'
        else:
            res = 'password must have atleast a lowercase alphabet'
    else:
        res = 'password must be between 6 and 12 characters long'
    return res


def validateUser(identity):
    if validateEmail(identity):
        if db.fetch_user_email(identity):
            res = db.fetch_user_email(identity)
        res = (404, 'email {} not found'.format(identity))
    else:
        if db.fetch_user_name(identity):
            res = db.fetch_user_name(identity)
        else:
            res = (404, 'username {} not found'.format(identity))
    return res
