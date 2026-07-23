from flask_jwt_extended import JWTManager
from app.database import db_manager
from app.models.models_generated import Employee
from app.repositories.auth_repo import AuthRepository


def init_jwt_loaders(jwt: JWTManager):

    @jwt.user_identity_loader
    def user_identity_lookup(user_obj):
        """Pulls the unique identifier when generating access tokens."""
        # Accepts raw object (e.g., create_access_token(identity=user))
        return str(user_obj.ID)

    @jwt.user_lookup_loader
    def user_lookup_callback(_jwt_header, jwt_data):
        """Automatically populates `current_user` with active database model."""
        identity = jwt_data["sub"]
        return AuthRepository.get_user_cache_data(int(identity))

    @jwt.token_in_blocklist_loader
    def check_if_token_revoked(jwt_header, jwt_payload):
        identity = jwt_payload["sub"]
        token_version = jwt_payload.get("version")
        employee = AuthRepository.get_user_cache_data(int(identity))
        return token_version != employee.auth.auth_version
