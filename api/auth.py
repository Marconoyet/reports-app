from flask import Blueprint, request, jsonify, make_response
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    jwt_required,
    get_jwt_identity,
    unset_jwt_cookies,
    get_csrf_token,

)
from services.centers_service import fetch_user_and_center
from services.users_service import check_users_login
from datetime import timedelta

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username_or_email = data.get('username_or_email')
    password = data.get('password')
    user = check_users_login(username_or_email, password)
    if user:
        # Create tokens
        access_token = create_access_token(
            identity=user.get("user").get('id'), expires_delta=timedelta(minutes=15))
        refresh_token = create_refresh_token(
            identity=user.get("user").get('id'), expires_delta=timedelta(days=365*10))
        response = make_response(jsonify({'user_auth': user}), 200)
        response.set_cookie(
            'access_token_cookie', access_token,
            httponly=True, samesite='None', secure=True, path='/',
            max_age=60 * 60  # 15 minutes in seconds
        )

        # Set refresh token cookie to expire in 10 years
        response.set_cookie(
            'refresh_token_cookie', refresh_token,
            httponly=True, samesite='None', secure=True, path='/',
            max_age=60 * 60 * 24 * 365 * 10  # 10 years in seconds
        )

        response.set_cookie(
            'user_id', str(user.get("user").get('id')),
            httponly=True, samesite='None', secure=True, path='/',
            max_age=60 * 60 * 24 * 365 * 10  # 10 years in seconds
        )

        response.set_cookie(
            'center_id', str(user.get("user").get('center_id')),
            httponly=True, samesite='None', secure=True, path='/',
            max_age=60 * 60 * 24 * 365 * 10  # 10 years in seconds
        )


        # Set CSRF tokens in separate cookies with the same expiration as their corresponding token
        # response.set_cookie(
        #     'csrf_access_token', csrf_access_token,
        #     httponly=False, samesite='None', secure=True, path='/',
        #     max_age=60 * 15  # 15 minutes in seconds
        # )

        # response.set_cookie(
        #     'csrf_refresh_token', csrf_refresh_token,
        #     httponly=False, samesite='None', secure=True, path='/',
        #     max_age=60 * 60 * 24 * 365 * 10  # 10 years in seconds
        # )

        return response

    return jsonify({'message': 'Invalid credentials'}), 401

# Updated Refresh Token endpoint


@auth_bp.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    identity = get_jwt_identity()
    access_token = create_access_token(
        identity=identity, expires_delta=timedelta(minutes=60))
    response = make_response(jsonify({"message": "Token refreshed"}))
    response.set_cookie('access_token_cookie', access_token,
                        httponly=True, samesite='None', secure=True)
    return response


@auth_bp.route('/validate', methods=['GET'])
@jwt_required()  # Requires a valid access token in the HTTP-only cookie
def validate():
    # Retrieve the current user's identity from the token
    current_user_id = get_jwt_identity()
    if not current_user_id:
        return jsonify({"status": "error", "message": "Unauthorized"}), 401

    # Fetch user and center data using the helper function
    user, center, error = fetch_user_and_center(current_user_id)
    if error:
        return jsonify({"status": "error", "message": error}), 500

    if user:
        return jsonify({
            "status": "success",
            "user": user,
            "center": center
        }), 200
    else:
        return jsonify({"status": "error", "message": "Unauthorized"}), 401

@auth_bp.route('/logout', methods=['POST'])
def logout():
    response = make_response(jsonify({"message": "Logout successful"}))
    
    unset_jwt_cookies(response)

    response.set_cookie('access_token_cookie', '', expires=0, httponly=True, samesite='None', secure=True)
    response.set_cookie('refresh_token_cookie', '', expires=0, httponly=True, samesite='None', secure=True)
    response.set_cookie('user_id', '', expires=0, httponly=True, samesite='None', secure=True)
    response.set_cookie('center_id', '', expires=0, httponly=True, samesite='None', secure=True)


    return response