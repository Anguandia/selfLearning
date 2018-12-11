from flask import jsonify, make_response
from .auth import bp
from .parcels import parcels_bp


@bp.errorhandler(400)
@parcels_bp.errorhandler(400)
def bad_request(error):
    return make_response(jsonify({'error': 'ill formed request'}), 400)


@bp.errorhandler(404)
@parcels_bp.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'resource unavailable'}), 404)


@parcels_bp.errorhandler(406)
def not_acceptable(error):
    return make_response(jsonify({'msg': 'parcel already delivered'}), 406)
