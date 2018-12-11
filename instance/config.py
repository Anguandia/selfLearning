import os

import psycopg2


class Config:
    DEBUG = False
    CSRF_ENABLED = True
    SECRET_KEY = os.getenv('SECRET')
    DATABASE_URL = 'postgresql: //postgres:kukuer1210@localhost/sendit'


class Development(Config):
    DEBUG = True


class Testing(Config):
    DEBUG = True
    TESTING = True
    DATABASE_URL = 'postgresql: //postgres:kukuer1210@localhost/sendit_tests'


app_config = {'DEVELOPMENT': Development, 'TESTING': Testing}


def create_db(name):
    try:
        conn = psycopg2.connect(user='postgres', password='kukuer1210')
        conn.autocommit = True
        cur = conn.cursor()
        cur.execute('''create database {}'''.format(name,))
        conn.commit()
    except (Exception, psycopg2.DatabaseError) as error:
        print('could not create db', error)
    # finally:
    #     if connection:
    #         cursor.close()
    #         connection.close()
    #         print('db created')
