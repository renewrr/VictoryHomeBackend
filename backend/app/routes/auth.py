import flask_jwt_extended

from flask import jsonify
from apiflask import APIBlueprint, abort
from flask_jwt_extended import jwt_required, get_jwt_identity, get_current_user
from app.repositories.auth_repo import AuthRepository
from app import schemas
from app.decorators import (
    public,
    two_factor_required,
    auto_rollback,
    general,
    get_logged_in_user_cache,
)

auth_bp = APIBlueprint("auth", __name__, tag="Auth System")


@auth_bp.post("/login_no_totp")
@auth_bp.output(schemas.LoginResponse)
@auth_bp.input(schemas.LoginWithoutTotpInput, location="form")
@public
def login_without_totp(form_data: schemas.LoginWithoutTotpInput):
    user = AuthRepository.get_user_by_credentials(
        form_data.account, form_data.password, None
    )
    management_privilege = AuthRepository.get_user_permission(user, "MANAGEMENT")
    if user.auth:
        access_token = flask_jwt_extended.create_access_token(
            identity=user,
            additional_claims={
                "is_2fa_verified": False,
                "version": user.auth.auth_version,
                "management_privilege": management_privilege,
            },
        )
    else:
        access_token = flask_jwt_extended.create_access_token(
            identity=user,
            additional_claims={
                "is_2fa_verified": False,
                "version": -1,
                "management_privilege": management_privilege,
            },
        )
    response = jsonify(
        {
            "status": True,
            "authenticated": True,
            "management_privilege": management_privilege,
            "is_2fa_verified": False,
        }
    )
    flask_jwt_extended.set_access_cookies(response, access_token)
    return response


@auth_bp.post("/login_with_totp")
@auth_bp.output(schemas.LoginResponse)
@auth_bp.input(schemas.LoginWithTotpInput, location="form")
@public
def login_with_totp(form_data: schemas.LoginWithTotpInput):
    user = AuthRepository.get_user_by_credentials(
        form_data.account, form_data.password, form_data.totp
    )
    management_privilege = AuthRepository.get_user_permission(user, "MANAGEMENT")
    if user.auth:
        access_token = flask_jwt_extended.create_access_token(
            identity=user,
            additional_claims={
                "is_2fa_verified": True,
                "version": user.auth.auth_version,
                "management_privilege": management_privilege,
            },
        )
    else:
        access_token = flask_jwt_extended.create_access_token(
            identity=user,
            additional_claims={
                "is_2fa_verified": False,
                "version": -1,
                "management_privilege": management_privilege,
            },
        )
    response = jsonify(
        {
            "status": True,
            "authenticated": True,
            "management_privilege": management_privilege,
            "is_2fa_verified": True,
        }
    )
    flask_jwt_extended.set_access_cookies(response, access_token)
    return response


@auth_bp.post("/logout")
@flask_jwt_extended.jwt_required()
@auth_bp.output(schemas.LogoutResponse)
@general
def logout():
    current_user = get_logged_in_user_cache()
    AuthRepository.set_user_logout_with_id(current_user.ID)
    response = jsonify({"msg": "logout successful"})
    flask_jwt_extended.unset_jwt_cookies(response)
    return {"status": True}, 200


@auth_bp.post("/force_logout")
@flask_jwt_extended.jwt_required()
@two_factor_required()
@auth_bp.output(schemas.ForcedLogoutResponse)
@auth_bp.input(schemas.ForcedLogoutRequest, location="json")
def force_logout(json_data: schemas.ForcedLogoutRequest):
    AuthRepository.set_user_logout_with_id(json_data.user_id)
    return {"statuts": True}, 200


@auth_bp.post("/two_factor_step_up")
@flask_jwt_extended.jwt_required()
@auth_bp.output(schemas.LoginResponse)
@auth_bp.input(schemas.TotpStepUpRequest, location="form")
@general
def totp_step_up(form_data: schemas.TotpStepUpRequest):
    current_user_id = get_logged_in_user_cache().ID
    current_user = AuthRepository.get_user_by_id(current_user_id)
    management_privilege = AuthRepository.get_user_permission(
        current_user, "MANAGEMENT"
    )
    if current_user.auth:
        two_factor_step_up = AuthRepository.verify_step_up_authentication(
            current_user, form_data.totp
        )
        access_token = flask_jwt_extended.create_access_token(
            identity=current_user,
            additional_claims={
                "is_2fa_verified": two_factor_step_up,
                "version": current_user.auth.auth_version,
                "management_privilege": management_privilege,
            },
        )
        response = jsonify(
            {
                "status": True,
                "authenticated": True,
                "management_privilege": management_privilege,
                "is_2fa_verified": two_factor_step_up,
            }
        )
        if not two_factor_step_up:
            abort(403, message="TWO_FACTOR_STEP_UP_CHALLENGE_FAILED")
    else:
        access_token = flask_jwt_extended.create_access_token(
            identity=current_user,
            additional_claims={
                "is_2fa_verified": False,
                "version": -1,
                "management_privilege": management_privilege,
            },
        )
        response = jsonify(
            {
                "status": True,
                "authenticated": True,
                "management_privilege": management_privilege,
                "is_2fa_verified": False,
            }
        )
        abort(403, message="NO_ACCOUNT_IN_RECORD")
    flask_jwt_extended.set_access_cookies(response, access_token)
    return response


@auth_bp.patch("/employee_password")
@flask_jwt_extended.jwt_required()
@auth_bp.output(schemas.PasswordChangeResponse)
@auth_bp.input(schemas.PasswordChangeRequest, location="json")
@general
@auto_rollback()
def patch_employee_password(json_data: schemas.PasswordChangeRequest):
    current_user = get_logged_in_user_cache()
    if json_data.confirm_password != json_data.new_password:
        abort(422, message="Password does not match")
    status = AuthRepository.set_user_password(
        current_user.ID, json_data.old_password, json_data.new_password
    )
    if status:
        return {"status": True}, 200
    else:
        abort(422, message="Password does not match")


@auth_bp.get("/auth_me")
@auth_bp.output(schemas.WhoAmIResponse)
@public
def who_am_i():
    data = flask_jwt_extended.verify_jwt_in_request(optional=True)
    current_user_id = flask_jwt_extended.get_jwt_identity()
    if data is not None and current_user_id is not None:
        current_user = AuthRepository.get_user_by_id(int(current_user_id))
        claims = flask_jwt_extended.get_jwt()
        verified: bool = claims.get("is_2fa_verified", False)
        assert isinstance(verified, bool)
        management_privilege = AuthRepository.get_user_permission(
            current_user, "MANAGEMENT"
        )
        return {
            "user_id": current_user.ID,
            "authenticated": True,
            "management_privilege": management_privilege,
            "is_2fa_verified": verified,
        }
    return {
        "user_id": -1,
        "authenticated": False,
        "management_privilege": False,
        "is_2fa_verified": False,
    }


@auth_bp.get("/me")
@flask_jwt_extended.jwt_required()
@auth_bp.output(schemas.EmployeeData)
@general
def get_me():
    current_user_id = flask_jwt_extended.get_jwt_identity()
    return AuthRepository.get_user_by_id(int(current_user_id))
