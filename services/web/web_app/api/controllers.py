from flask import jsonify
from flask import render_template, request
from web_app.models import User, PalacouloDoorStatus, PortoDoorStatus
from web_app.api import bp
from flask import url_for
from web_app import db
from web_app.api.apierrors import bad_request
from web_app.api.auth import token_auth

@bp.route('/users/<int:id>', methods=['GET'])
@token_auth.login_required
def get_user(id):
    return jsonify(User.query.get_or_404(id).to_dict())

@bp.route('/controller', methods=['POST'])
@token_auth.login_required
def update_controller():
    data = request.get_json() or {}
    print(data)
    if 'controller' not in data or 'status' not in data:
        return bad_request('must include username, email and password fields')

    if "Porto" in data["controller"]:
        controller = PortoDoorStatus(data["status"])
    elif "Palacoulo" in data["controller"]:
        controller = PalacouloDoorStatus(data["status"])

    db.session.add(controller)
    db.session.commit()
    response = jsonify(controller.to_dict())
    response.status_code = 201
    return response

def update_user(id):
    user = User.query.get_or_404(id)
    data = request.get_json() or {}
    if 'username' in data and data['username'] != user.username and \
            User.query.filter_by(username=data['username']).first():
        return bad_request('please use a different username')
    if 'email' in data and data['email'] != user.email and \
            User.query.filter_by(email=data['email']).first():
        return bad_request('please use a different email address')
    user.from_dict(data, new_user=False)
    db.session.commit()
    return jsonify(user.to_dict())