from functools import wraps
from apiflask import abort
from flask_jwt_extended import jwt_required, get_current_user, get_jwt
from sqlalchemy.exc import SQLAlchemyError, IntegrityError, NoResultFound
from app.database import db_manager
import app.models.models_generated as models
from app.repositories.auth_repo import AuthRepository


def get_logged_in_user() -> models.Employee:
    user = get_current_user()
    assert isinstance(user, models.Employee)
    return user


def privilege_required(required_role: str = "MANAGEMENT"):
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            
            current_user = get_logged_in_user()
            if not AuthRepository.get_user_permission(current_user, required_role):
                abort(
                    403,
                    message="No required privilege, contact management for more info.",
                )
            return fn(*args, **kwargs)

        return wrapper

    return decorator


def public(f):
    """Explicitly marks an endpoint as completely public (no login required)."""
    f._is_public = True
    return f


def general(f):
    f._required_role = "GENERAL"
    return f


def two_factor_required():
    """
    Custom decorator to protect endpoints requiring completed 2FA validation.
    Must be placed underneath @jwt_required().
    """

    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            claims = get_jwt()
            if not claims.get("is_2fa_verified", False):
                abort(
                    403,
                    message="Step-up authentication required. Please complete the 2FA challenge.",
                )
            return fn(*args, **kwargs)

        return wrapper

    return decorator


def auto_rollback(error_code="DATABASE_CONFLICT", message="輸入名稱與現存資料重複"):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            try:
                return f(*args, **kwargs)
            except IntegrityError as e:
                db_manager.session.rollback()
                err_msg = str(e.orig).lower()

                # Check if it's a uniqueness issue
                if "unique" in err_msg or "duplicate" in err_msg:
                    abort(
                        409,
                        message=message,
                        extra_data={"error": error_code},
                    )

                    # Fallback for other integrity issues (e.g., foreign key)
                abort(
                    422,
                    message="選項已經受到修改，請重新整理",
                    extra_data={"error": "STALE_REFERENCE"},
                )
            except NoResultFound as e:
                db_manager.session.rollback()
                abort(
                    422,
                    message="欄位已遭修改，請重新整理",
                    extra_data={"error": "STALE_REFERENCE"},
                )
            except SQLAlchemyError as e:
                db_manager.session.rollback()
                # Log exact exception here
                abort(
                    500,
                    message="資料庫更新失敗",
                )
            except Exception as e:
                db_manager.session.rollback()
                raise e

        return decorated_function

    return decorator
