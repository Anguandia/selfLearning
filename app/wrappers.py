from functools import wraps
from .models import User
# import inspect
from flask import request, jsonify
from app import db


def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        auth_header = request.headers.get('Authorization')
        if auth_header:
            token = auth_header.split(" ")[1]
            key = User.decode_token(token)
            if isinstance(key, int):
                if db.fetch_user(key)['user_type'] == 'admin':
                    v = f(*args, **kwargs)
                else:
                    return jsonify(
                        {'msg': 'this action requores admin previledges'}
                        ), 403
            else:
                v = jsonify({'msg': User.decode_token(token)}), 401
        else:
            v = jsonify({'msg': 'please login or signup'}), 401
        return v
    return decorated_function


def auth_required(f):
    @wraps(f)
    def decorated_function(userid, *args, **kwargs):
        auth_header = request.headers.get('Authorization')
        if auth_header:
            token = auth_header.split(" ")[1]
            key = User.decode_token(token)
            if isinstance(key, int):
                # if 'parcelid' in str(inspect.signature(f)):
                #     #userid = db.get_order('parcelid')['userid']
                #     print('parcelid')
                # else:
                #     userid in str(inspect.signature(f))
                #     userid = 'userid'
                # return jsonify({key: userid})
                if key == int(userid) or db.fetch_user(key)[
                        'user_type'] == 'admin':
                    v = f(userid, *args, **kwargs)
                else:
                    return jsonify(
                        {'msg': 'this account doesn\'t belong to you!'}), 403
            else:
                v = jsonify({'msg': User.decode_token(token)}), 401
        else:
            v = jsonify({'msg': 'please login or signup'}), 401
        return v
    return decorated_function


def owner_required(f):
    @wraps(f)
    def decorated_function(parcelid, *args, **kwargs):
        auth_header = request.headers.get('Authorization')
        if auth_header:
            token = auth_header.split(" ")[1]
            key = User.decode_token(token)
            if isinstance(key, int):
                if db.get_order(parcelid):
                    userid = db.get_order(parcelid)['userid']
                    if key == int(userid) or db.fetch_user(key)[
                            'user_type'] == 'admin':
                        v = f(parcelid, *args, **kwargs)
                    else:
                        return jsonify(
                            {'msg': 'you do not own this order!'}), 403
                else:
                    v = jsonify(
                        {'msg': 'authentication failed, check parcelid'}
                        ), 401
            else:
                v = jsonify({'msg': User.decode_token(token)}), 401
        else:
            v = jsonify({'msg': 'please login or signup'}), 401
        return v
    return decorated_function


def anonymous(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        auth_header = request.headers.get('Authorization')
        if auth_header:
            token = auth_header.split(" ")[1]
            key = User.decode_token(token)
            if isinstance(key, int):
                v = f(*args, **kwargs)
            else:
                v = jsonify({'msg': User.decode_token(token)}), 401
        else:
            v = jsonify({'msg': 'please login or signup'}), 401
        return v
    return decorated_function
