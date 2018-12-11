import os
from flask_api import FlaskAPI
# from flask import request, jsonify, abort, make_response
from instance.config import app_config


def create_app(config_name):
    app = FlaskAPI(__name__, instance_relative_config=True)
    app.config.from_pyfile('config.py')
    app.config.from_object(app_config[config_name])
    # with app.app_context():
    #    ctx.push
    from app.auth import bp
    app.register_blueprint(bp)
    from app.parcels import parcels_bp
    app.register_blueprint(parcels_bp)
    from app import db
    db.init_app(app)

    return app


app = create_app(config_name=os.getenv('FLASK_ENV'))

# @app.route('/signup', methods=['POST', 'GET'])
# def signup():
#     form = RegistrationForm()
#     data = {}
#     data['name'] = form.username.data
#     data['email'] = form.email.data,
#     data['password'] = form.password.data
#     result = validation.validateSignup(data)
#     flash(result)
#     return render_template('signup.html', title='SignUp', form=form)


# @app.before_request
# def db_init():
#     connection = psycopg2.connect(
#         "dbname = sendit user = postgres password = kukuer1210\
#          host = localhost port = 5432"
#         )
#     return connection
#
# @app.teardown_request
# def destroy_db(exception):
#     db_init().cursor.close()
#     db_init().close()
