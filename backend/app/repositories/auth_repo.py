from app.database import db_manager
from app.models import model_views, models_generated as models
import pyotp
from cachetools import TTLCache
from dataclasses import dataclass


@dataclass
class EmployeeCache:
    ID: int
    name: str
    auth_version: int
    slugs: list[str]


class AuthenticationFailedError(Exception):
    pass


USERCACHE = TTLCache[int, EmployeeCache](maxsize=10000, ttl=300)


def get_active_user(user_id: int) -> EmployeeCache:
    """Fetch from RAM first; hit Supabase only if cache expired."""
    if user_id in USERCACHE:
        return USERCACHE[user_id]

    # Cache miss: fetch from DB
    db_manager.session.remove()
    user = (
        db_manager.session.query(models.Employee)
        .where(models.Employee.ID == user_id)
        .where(models.Employee.deleted == False)
        .one()
    )
    print(f"User auth version fetched: {user.auth.auth_version if user.auth else -1}", flush=True)
    auth_v = -1 if not user.auth else user.auth.auth_version
    perm_slugs = [perm.perm.perm_slug for perm in user.employee_perms]
    USERCACHE[user_id] = EmployeeCache(
        ID=user.ID, name=user.name, auth_version=auth_v, slugs=perm_slugs
    )
    return USERCACHE[user_id]


class AuthRepository:

    @staticmethod
    def get_user_by_id(user_id: int) -> models.Employee:
        user = (
            db_manager.session.query(models.Employee)
            .where(models.Employee.ID == user_id)
            .where(models.Employee.deleted == False)
            .one()
        )
        return user

    @staticmethod
    def get_user_cache_data(user_id: int) -> EmployeeCache:
        return get_active_user(user_id)

    @staticmethod
    def get_user_by_credentials(account: str, password: str, totp: str | None):
        auth = (
            db_manager.session.query(models.Auth)
            .where(models.Auth.account == account)
            .where(models.Auth.password == password)
            .where(models.Auth.deleted == False)
            .one()
        )
        if not auth.employee:
            raise AuthenticationFailedError
        if totp:
            if not auth.totp_secret:
                raise AuthenticationFailedError
            totp_checker = pyotp.TOTP(auth.totp_secret)
            if not totp_checker.verify(totp):
                raise AuthenticationFailedError
        return auth.employee

    @staticmethod
    def get_user_permission(user: models.Employee, permission: str):
        return any(permission in perm.perm.perm_slug for perm in user.employee_perms)

    @staticmethod
    def set_user_logout_with_id(user_id: int):
        user = (
            db_manager.session.query(models.Employee)
            .where(models.Employee.ID == user_id)
            .one()
        )
        if user.auth:
            user.auth.auth_version += 1
        db_manager.session.commit()
        db_manager.session.remove()

    @staticmethod
    def verify_step_up_authentication(user: models.Employee, code: str):
        if user.auth and user.auth.totp_secret:
            totp = pyotp.TOTP(user.auth.totp_secret)
            if totp.verify(code):
                return True
        return False

    @staticmethod
    def set_user_password(user_id: int, old_password: str, new_password: str):
        employee = (
            db_manager.session.query(models.Employee)
            .where(models.Employee.ID == user_id)
            .one()
        )
        if not employee.auth or employee.auth.password != old_password:
            return False
        employee.auth.password = new_password
        db_manager.session.commit()
        return True
