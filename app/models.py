from datetime import datetime, timedelta
import jwt
from werkzeug.security import generate_password_hash, check_password_hash
from app import db
# from instance.config import create_db
# from flask import current_app, g
# from flask.cli import with_appcontext

db.connect()

cursor = db.connect().cursor()


class User:
    def __init__(self, name, email, password, user_type='user'):
        self.name = name
        self.email = email
        self.password = password
        # self.tel = tel
        self.user_type = user_type
        create_user_table_query = 'CREATE TABLE IF NOT EXISTS users(\
            userid SERIAL PRIMARY KEY NOT NULL, name varchar,\
            email varchar unique not null, password_hash varchar not null,\
            user_type varchar\
            )'
        cursor.execute(create_user_table_query)
        db.save()

    def __repr__(self):
        return 'user: {}, email: {}, user_type: {}'.format(
            self.name, self.email, self.user_type)

    def set_password(self, password):
        return generate_password_hash(password)

    def validate_password(self, password):
        password_hash = db.fetch_user_name(self.name)['password_hash']
        return check_password_hash(password_hash, password)

    def generate_token(self):
        userid = self.userid
        try:
            payload = {
                'exp': datetime.utcnow() + timedelta(
                    minutes=125),
                'iat': datetime.utcnow(),
                'sub': userid
                }
            self.token = jwt.encode(
                payload,
                'trying',
                algorithm='HS256',
                )
            return self.token
        except Exception as error:
            print('error in token:', error)
            # return str(error)

    def renew_token(self, token):
        if self.decode_token(token)['exp'] < datetime.utcnow()\
                + timedelta(minutes=1):
            return self.generate_token()
        else:
            return token

    @staticmethod
    def decode_token(token):
        if db.check_token(token):
            result = 'please login'
        else:
            try:
                payload = jwt.decode(
                    token, 'trying', algorithms=['HS256'], verify=True)
                result = payload['sub']
            except jwt.ExpiredSignatureError:
                result = "Expired token. Please login to get a new token"
            except jwt.InvalidTokenError:
                result = "Invalid token. Please register or login"
            except Exception as error:
                print(error)
                result = error
        return result


# class Admin(User):
#     def __init__(self, name, email, password, isadmin=True):
#         super(Admin, self).__init__(
#             self, name, email, password, tel=00, isadmin=True)
#         self.isadmin = isadmin
#
#     def is_admin(self):
#         return self.isadmin


class Order:
    def __init__(
        self, userid, reciever, origin, destination, weight='1',
            status='recieved', service_class='standard',
            category='domestic', current_location='unknown',
            description='none', charge='0'):
        self.userid = userid
        self.reciever = reciever
        self.origin = origin
        self.destination = destination
        self.weight = weight
        self.status = status
        self.service_class = service_class
        self.category = category
        self.current_location = current_location
        self.description = description
        self.charge = charge

        create_order_table_query = 'CREATE TABLE IF NOT EXISTS orders(\
            parcelid serial PRIMARY KEY NOT NULL, userid  varchar NOT NULL,\
            reciever varchar, origin varchar, destination varchar, weight\
            varchar, status varchar, service_class varchar, category varchar,\
            current_location varchar, description varchar, charge varchar\
            )'
        cursor.execute(create_order_table_query)
        db.save()

    def __repr__(self):
        return 'sender: {}, reciever: {}, destination: {}, origin: {}'.format(
            db.fetch_user(self.userid)['name'], self.reciever,
            self.destination, self.origin)


# class RevokedTokens:
#     def __init__(self, token):
#         self.token = token
#         create_token_table_query = 'CREATE TABLE IF NOT EXISTS
#                 revoked_tokens(\
#             tokenid serial PRIMARY KEY NOT NULL, token VARCHAR NOT NULL)'
#         cursor.execute(create_token_table_query)
#         db.save()
#
#     def __repr__(self):
#         return '{}'.format(str(self.token))
#
#     def revoke(self):
#         try:
#             query = 'INSERT INTO revoked_tokens (token) values (%s);'
#             cursor.execute(query, (self.token,))
#             db.save()
#             print('token blacklisted')
#             return "logged out"
#         except (Exception, psycopg2.Error) as error:
#             print("Failed logout", error)
#             return "failed to logout"

# class Boots(Model):
#     __tablename__ = 'boots'
#
#     id = serial primary key
#     size = int NOT NU
#
#     def __repr__(self):
#         return '{}'.format(self.size)
