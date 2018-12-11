import psycopg2
from flask.cli import with_appcontext
import click


def connect(db_name='sendit'):
    connection = psycopg2.connect(
        "dbname = {} user = postgres password = kukuer1210 host = localhost \
        port = 5432".format(db_name)
        )
    connection.autocommit = True
    return connection


# def cursor(db_name):
#     return connect(db_name).cursor()
cursor = connect().cursor()


def close(db_name='sendit', error=None):
    if connect():
        connect().close()


def cur(db_name='sendit'):
    cursor = connect(db_name='sendit').cursor()
    return cursor


def init_db():
    cur('postgres').execute('create database pilo')
    save('postgres')
    close('postgres')
    print('creaed')


def save(db_name='sendit'):
    connect(db_name).commit()


def init_app(app):
    app.teardown_appcontext(close)
    app.cli.add_command(init_db_command)


@click.command('init-db')
@with_appcontext
def init_db_command():
    init_db()
    click.echo('Initialized the database.')


def register(user):
    try:
        create_user_query = ' INSERT INTO users (name, email, \
        password_hash, user_type) VALUES (%s,%s,%s,%s)'
        cursor.execute(
            create_user_query, (
                user.name, user.email,
                user.set_password(user.password), user.user_type
                ))
        save()
        print("user", user.__dict__, "saved to db")
        return {
            'msg': 'Hello {}, you have successfully signedup, please login'
            .format(user.name), 'userid': fetch_user_name(user.name)['userid']
            }
    except (Exception, psycopg2.Error) as error:
        print("Failed to create user:", error)


def get_users():
    cursor.execute("SELECT * FROM users ORDER BY userid DESC")
    uzers = cursor.fetchall()
    users = [dict_user(user) for user in uzers]
    return users


def fetch_user_name(name):
    cursor.execute((
        "SELECT * FROM users where name = %s"), (name,))
    user = cursor.fetchone()
    return dict_user(user)


def fetch_user(userid):
    try:
        cursor.execute((
            "SELECT * FROM users where userid = %s"), (userid,))
        user = cursor.fetchone()
        return dict_user(user)
    except Exception as error:
        print(error)


def fetch_user_email(email):
    try:
        cursor.execute((
            "SELECT * FROM users where email = %s"), (email,))
        user = cursor.fetchone()
        return dict_user(user)
    except Exception as error:
        print(error)


def get_count(table):
    try:
        cursor.execute("SELECT * FROM {}".format(table))
        count = cursor.rowcount
        return count
    except Exception as error:
        print(error)
        return error


def edit_user(userid, key, value):
    if key == 'changeName':
        sql_update_query = 'Update users set name = %s where userid = %s'
    elif key == 'changeEmail':
        sql_update_query = 'Update users set email = %s where userid = %s'
    elif key == 'changePassword':
        sql_update_query = 'Update users set password_hash = %s\
            where userid = %s'
    else:
        return 'invalid endpoint, can not change {}'.format(key[6:].lower())  #
    try:
        cursor.execute(sql_update_query, (value, userid))
        save()
        print('ok')
        return '{} changed'.format(key[6:].lower())
    except (Exception, psycopg2.Error) as error:
        print(error)
        return("Error in update operation", error)


def logout(token):
    create_token_table_query = 'CREATE TABLE IF NOT EXISTS revoked_tokens(\
            tokenid serial PRIMARY KEY NOT NULL, token VARCHAR NOT NULL)'
    cursor.execute(create_token_table_query)
    save()
    try:
        query = 'INSERT INTO revoked_tokens (token) values (%s);'
        cursor.execute(query, (token,))
        save()
        print('token blacklisted')
        return "logged out"
    except (Exception, psycopg2.Error) as error:
        print("Failed logout", error)
        return "failed to logout"


def delete_user(userid):
    user = fetch_user(userid)
    if user:
        try:
            sql_delete_query = 'delete from users where userid = %s'
            cursor.execute(sql_delete_query, (userid,))
            save()
            res = (
                'user {}: {} deleted'.format(user['userid'], user['name']),
                200)
        except (Exception, psycopg2.Error) as error:
            res = (
                'error deleting user {}: {}'.format(
                    user['userid'], user['name']),
                500)
            print("Error deleting", error)
    res = ('no user {}: {}'.format(user['userid'], user['name']), 404)
    return res


def dict_user(tup):
    user = {}
    keys = ['userid', 'name', 'email', 'password_hash', 'user_type']
    try:
        for key in keys:
            user[key] = tup[keys.index(key)]
        return user
    except Exception as e:
        print(e)


def to_object(dic):
    from .models import User
    user = User('', '', '')
    for key in dic.keys():
        if key in user.__dict__.keys():
            user.__setattr__(key, dic[key])
        user.userid = dic['userid']
    return user


def saveOrder(order):
        try:
            create_order_query = ' INSERT INTO orders (userid, reciever, origin,\
            destination, weight, status, service_class, category,\
            current_location, description, charge ) VALUES\
            (%s,%s,%s, %s,%s, %s,%s, %s,%s,%s,%s)'
            cursor.execute(
                create_order_query, (
                    order.userid, order.reciever, order.origin,
                    order.destination, order.weight, order.status,
                    order.service_class, order.category,
                    order.current_location, order.description,
                    order.charge))
            save()
            print('created')
            return {
                'order': 'created', 'parcelid': get_user_orders(order.userid)
                [0][0]['parcelid'], 'summary': '{}'.format(order)
                }
        except (Exception, psycopg2.Error) as error:
            print("Failed to create order", error)
            return 'failed to create order contact support'


def update_order(input, id, key):
    if input:
        try:
            if key == 'destination':
                sql_update_query = 'Update orders set destination = %s\
                    where parcelid = %s;'
            elif key == 'status':
                sql_update_query = 'Update orders set status = %s\
                    where parcelid = %s;'
            # elif key == 'cancel':
            #     sql_update_query = 'Update orders set status = canceled\
            #         where parcelid = %s;'
            else:
                key == 'location'
                sql_update_query = 'Update orders set current_location = %s\
                    where parcelid = %s; '

            cursor.execute((sql_update_query), (input, id))
            save()
            print("success")
            result = '{} updated to \'{}\''.format(key, input)
        except (Exception, psycopg2.Error) as error:
            print("Error in update operation", error)
            result = ('update failed, contact sendit', 500)
    else:
        result = ('please fill in value for {}'.format(key), 400)
    return result


def delete_order(parcelid):
    try:
        sql_delete_query = 'delete from orders where parcelid = %s'
        cursor.execute(sql_delete_query, (parcelid,))
        save()
        print("deleted")
    except (Exception, psycopg2.Error) as error:
        print("Error in delete operation", error)


def get_orders():
    try:
        cursor.execute("SELECT * FROM orders ORDER BY parcelid DESC")
        save()
        orders = cursor.fetchall()
        count = cursor.rowcount
        print(count, "orders fetched", orders)
        result = [dict_order(order) for order in orders]
    except (Exception, psycopg2.Error) as error:
        print('problem in get orders function', error)
        result = ('an error occured, please contact support', 500)
    except (Exception) as error:
        print('error', error)
        result = ('order not found', 404)
    return result


# def get_parcelid()


def get_user_orders(userid):
    try:
        cursor.execute(
            "SELECT * FROM orders where userid = {}\
            ORDER BY parcelid DESC".format(userid)
            )
        orders = cursor.fetchall()
        res = [dict_order(order) for order in orders]
        count = cursor.rowcount
        print(count, "orders fetched")
        result = (res, 200)
    except (Exception, psycopg2.Error) as error:
        print('error in get_user_orders function:', error)
        result = ('system error, contact support', 500)
    except Exception as error:
        print(error)
        result = ('no orders for this user', 404)
    return result


def get_order(parcelid):
    try:
        cursor.execute(
            "SELECT * FROM orders where parcelid = {}"
            .format(parcelid))
        order = cursor.fetchone()
        print("order fetched")
        return dict_order(order)
    except (Exception, psycopg2.Error) as error:
        print(error)


def check_token(token):
    try:
        cursor.execute((
            'select * FROM revoked_tokens where token = %s'),
            (str(token),))
        revoked = cursor.fetchone()
        print(revoked)
        return revoked
    except (Exception, psycopg2.Error) as e:
        print(e)


def dict_order(order):
    do = {
        'parcelid': order[0],
        'userid': order[1],
        'reciever': order[2],
        'origin': order[3],
        'destination': order[4],
        'weight': order[5],
        'status': order[6],
        'service_class': order[7],
        'category': order[8],
        'current_location': order[9],
        'description': order[10],
        'charge': order[11]
    }
    return do


# def edit_user_password(user, old_password, new_password):
#     if user.validate_password(old_password):
#         try:
#             sql_update_query = 'Update users set password_hash = %s where\
#                 userid = %s'
#             cursor.execute(sql_update_query, (
#                 user.set_password(new_password), user.userid))
#             save()
#             return 'password changed'
#         except (Exception, psycopg2.Error) as error:
#             return("Error in update operation", error)
#     else:
#         return "wrong current password"s
