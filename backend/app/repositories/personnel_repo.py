from app.database import db_manager
from app.models import model_views, models_generated as models
from app import schemas
from typing import Tuple, Sequence
import datetime


from sqlalchemy import select, insert, delete, Integer, or_
from sqlalchemy.orm import with_loader_criteria

import pyotp


class PersonnelRepository:
    @staticmethod
    def get_all_employee() -> Sequence[models.Employee]:
        stmt = select(models.Employee).options(
            with_loader_criteria(models.Employee, lambda cls: cls.deleted == False),
            with_loader_criteria(models.Auth, lambda cls: cls.deleted == False),
        )
        return db_manager.session.scalars(stmt).all()

    @staticmethod
    def get_active_employees():
        return db_manager.session.query(models.Employee).where(
            models.Employee.deleted == False
        )

    @staticmethod
    def patch_employee(
        before: schemas.EmployeeDetails, after: schemas.EmployeeDetails
    ) -> models.Employee:
        before_object = db_manager.session.scalars(
            select(models.Employee).where(models.Employee.ID == before.ID)
        ).one()
        before_object.deleted = after.deleted
        if after.date_of_employment:
            before_object.date_of_employment = after.date_of_employment
        before_object.name = after.name
        before_object.company_email = after.company_email
        before_object.localization = after.localization
        if after.auth:
            account, password = after.auth.account.strip(), after.auth.password.strip()
            if account and password:
                if not before_object.auth:
                    before_object.auth = models.Auth()
                before_object.auth.account = after.auth.account
                before_object.auth.password = after.auth.password
            if before_object.auth:
                before_object.auth.totp_secret = after.auth.totp_secret
        db_manager.session.commit()
        return before_object

    @staticmethod
    def new_employee(employee_data: schemas.NewEmployeeRequest) -> models.Employee:
        employee_obj = models.Employee(name=employee_data.name)
        email = employee_data.email.strip()
        if email:
            employee_obj.company_email = email
        account = employee_data.account.strip()
        password = employee_data.password.strip()
        if account and password:
            auth_obj = models.Auth(account=account, password=password)
            db_manager.session.add(auth_obj)
            employee_obj.auth = auth_obj
            if employee_data.use_two_factor:
                auth_obj.totp_secret = pyotp.random_base32()
        db_manager.session.add(employee_obj)
        db_manager.session.commit()
        return employee_obj

    @staticmethod
    def setup_totp(employee: schemas.EmployeeDetails) -> models.Employee:
        new_secret = pyotp.random_base32()
        target = db_manager.session.scalars(
            select(models.Employee).where(models.Employee.ID == employee.ID)
        ).one()
        if not target.auth:
            return target
        target.auth.totp_secret = new_secret
        db_manager.session.commit()
        return target

    @staticmethod
    def patch_password(user_id: int, before: str, after: str) -> bool:
        employee = db_manager.session.scalars(
            select(models.Employee).where(models.Employee.ID == user_id)
        ).one()
        if not employee.auth or employee.auth.password != before:
            return False
        employee.auth.password = after
        db_manager.session.commit()
        return True
