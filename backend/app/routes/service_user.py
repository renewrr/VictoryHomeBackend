import flask_jwt_extended

from flask import jsonify
from apiflask import APIBlueprint
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.repositories.service_user_repo import ServiceUserRepository
from app import schemas
from app.decorators import (
    general,
    auto_rollback,
    privilege_required,
)

service_user_bp = APIBlueprint("service_user_bp", __name__, tag="Service User System")


@service_user_bp.get("/flat_service_user_nicknames")
@flask_jwt_extended.jwt_required()
@service_user_bp.output(schemas.NicknamesResponse)
@general
def get_flat_nicknames():
    return {"data_rows": ServiceUserRepository.get_flat_nicknames()}


@service_user_bp.get("/all_service_users")
@flask_jwt_extended.jwt_required()
@service_user_bp.output(schemas.ManagementServiceUserResponse)
@general
def get_all_service_users():
    return {"data_rows": ServiceUserRepository.get_all_service_user()}


@service_user_bp.patch("/service_user")
@flask_jwt_extended.jwt_required()
@privilege_required("MANAGEMENT")
@service_user_bp.output(schemas.ManagementServiceUserEditResponse)
@service_user_bp.input(schemas.ManagementServiceUserEditRequest, location="json")
@auto_rollback()
def patch_service_user(json_data: schemas.ManagementServiceUserEditRequest):
    patched_data = ServiceUserRepository.patch_service_user(
        json_data.before, json_data.after
    )
    return {"updated": patched_data}


@service_user_bp.post("/service_users")
@flask_jwt_extended.jwt_required()
@service_user_bp.input(schemas.ServiceUserInput, location="json")
@auto_rollback()
def post_new_service_user(json_data: schemas.ServiceUserInput):
    ServiceUserRepository.post_service_users(json_data)
    return {}, 200