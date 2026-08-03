from flask_jwt_extended import JWTManager, unset_jwt_cookies
from app.database import db_manager
from app.repositories.auth_repo import AuthRepository, EmployeeCache, invalidate_cache
from flask import jsonify


def init_jwt_loaders(jwt: JWTManager):

    @jwt.user_identity_loader
    def user_identity_lookup(user_obj):
        """Pulls the unique identifier when generating access tokens."""
        # Accepts raw object (e.g., create_access_token(identity=user))
        return str(user_obj.ID)

    @jwt.user_lookup_loader
    def user_lookup_callback(_jwt_header, jwt_data) -> EmployeeCache:
        """Automatically populates `current_user` with active database model."""
        identity = jwt_data["sub"]
        return AuthRepository.get_user_cache_data(int(identity))

    @jwt.token_in_blocklist_loader
    def check_if_token_revoked(jwt_header, jwt_payload):
        identity = jwt_payload["sub"]
        token_version = jwt_payload.get("version")
        employee = AuthRepository.get_user_cache_data(int(identity))
        if token_version > employee.auth_version:
            invalidate_cache(int(identity))
        print(
            f"Token version: sent:{token_version}, db:{employee.auth_version}",
            flush=True,
        )
        return token_version != employee.auth_version

    @jwt.expired_token_loader
    def my_expired_token_callback(jwt_header, jwt_payload):
        # 1. Create a custom error response
        response = jsonify({"status": 401, "msg": "The token has expired"})

        # 2. Clear the JWT cookies from the response header
        unset_jwt_cookies(response)

        return response, 401
