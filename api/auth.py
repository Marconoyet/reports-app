from flask import Blueprint, request, jsonify, make_response
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    jwt_required,
    get_jwt_identity,
    unset_jwt_cookies,
    set_access_cookies,
    set_refresh_cookies,
    get_current_user
)
from services.users_service import check_users_login
from datetime import timedelta

auth_bp = Blueprint('auth', __name__)


# Login route remains the same
@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username_or_email = data.get('username_or_email')
    password = data.get('password')
    user = check_users_login(username_or_email, password)
    if user:
        access_token = create_access_token(identity="batman", expires_delta=timedelta(minutes=15))
        refresh_token = create_refresh_token(identity="batman")
        response = make_response(jsonify({'user_auth': user}), 200)
        set_access_cookies(response, access_token)
        set_refresh_cookies(response, refresh_token)
        return response

    else:
        return jsonify({'message': 'Invalid credentials'}), 401

# Updated Refresh Token endpoint
@auth_bp.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    identity = get_jwt_identity()
    access_token = create_access_token(identity=identity, expires_delta=timedelta(minutes=15))
    
    response = make_response(jsonify({"message": "Token refreshed"}))
    set_access_cookies(response, access_token)
    return response

@auth_bp.route('/validate', methods=['GET'])
@jwt_required()  # Requires a valid access token in the HTTP-only cookie
def validate():
    current_user = get_jwt_identity()  # Retrieve the current user's identity from the token
    if current_user:
        return jsonify({"status": "success", "user": current_user}), 200
    else:
        return jsonify({"status": "error", "message": "Unauthorized"}), 401
    
@auth_bp.route('/logout', methods=['POST'])
def logout():
    response = make_response(jsonify({"message": "Logout successful"}))
    unset_jwt_cookies(response)
    return response