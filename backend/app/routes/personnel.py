import flask_jwt_extended

from flask import jsonify
from apiflask import APIBlueprint, abort
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.repositories.personnel_repo import PersonnelRepository
from app import schemas
from app.decorators import (
    get_logged_in_user,
    general,
    auto_rollback,
    privilege_required,
    two_factor_required,
)

personnel_bp = APIBlueprint("personnel", __name__, tag="Personnel System")


@personnel_bp.get("/employee_details")
@flask_jwt_extended.jwt_required()
@privilege_required("MANAGEMENT")
@two_factor_required()
@personnel_bp.output(schemas.ManagementEmployeeResponse)
def get_employee_details():
    return {"data_rows": PersonnelRepository.get_all_employee()}


@personnel_bp.post("/employee_details")
@flask_jwt_extended.jwt_required()
@privilege_required("MANAGEMENT")
@two_factor_required()
@personnel_bp.output(schemas.ManagementEmployeeEditResponse)
@personnel_bp.input(schemas.NewEmployeeRequest, location="json")
@auto_rollback()
def post_employee(json_data: schemas.NewEmployeeRequest):
    patched_data = PersonnelRepository.new_employee(json_data)
    return {"updated": patched_data}


@personnel_bp.patch("/employee_details")
@flask_jwt_extended.jwt_required()
@privilege_required("MANAGEMENT")
@two_factor_required()
@personnel_bp.output(schemas.ManagementEmployeeEditResponse)
@personnel_bp.input(schemas.ManagementEmployeeEditRequest, location="json")
@auto_rollback()
def patch_employee(json_data: schemas.ManagementEmployeeEditRequest):
    patched_data = PersonnelRepository.patch_employee(json_data.before, json_data.after)
    return {"updated": patched_data}


@personnel_bp.patch("/employee_setup_totp")
@flask_jwt_extended.jwt_required()
@privilege_required("MANAGEMENT")
@two_factor_required()
@personnel_bp.output(schemas.EmployeeDetails)
@personnel_bp.input(schemas.EmployeeDetails, location="json")
def setup_totp(json_data: schemas.EmployeeDetails):
    patched_data = PersonnelRepository.setup_totp(json_data)
    return patched_data


@personnel_bp.patch("/password_change")
@flask_jwt_extended.jwt_required()
@personnel_bp.output(schemas.PasswordChangeResponse)
@personnel_bp.input(schemas.PasswordChangeRequest, location="json")
@general
@auto_rollback()
def patch_employee_password(json_data: schemas.PasswordChangeRequest):
    current_user = get_logged_in_user()
    if json_data.confirm_password != json_data.new_password:
        abort(422, message="PASSWORD CHANGE FAILED")
    status = PersonnelRepository.patch_password(
        current_user.ID, json_data.old_password, json_data.new_password
    )
    if not status:
        abort(422, message="PASSWORD CHANGE FAILED")
    return {"status": status}, 200
