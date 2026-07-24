from app.database import db_manager
from app.models import model_views, models_generated as models
from app import schemas
from typing import Tuple, Sequence
import datetime


from sqlalchemy import select, insert, delete, Integer, or_
from sqlalchemy.orm import with_loader_criteria, selectinload, noload


class ServiceUserRepository:
    @staticmethod
    def get_active_service_users():
        return (
            db_manager.session.query(models.ServiceUser)
            .where(models.ServiceUser.active == True)
            .where(models.ServiceUser.deleted == False)
            .all()
        )

    @staticmethod
    def get_flat_nicknames() -> Sequence[models.ServiceUserNicknames]:
        return (
            db_manager.session.query(models.ServiceUserNicknames)
            .where(
                models.ServiceUserNicknames.service_user.has(
                    models.ServiceUser.deleted == False
                )
            )
            .all()
        )

    @staticmethod
    def get_all_service_user() -> Sequence[models.ServiceUser]:
        return (
            db_manager.session.query(models.ServiceUser)
            .where(models.ServiceUser.deleted == False)
            .options(
                selectinload(models.ServiceUser.living_space).selectinload(
                    models.ServiceUser.service_user_nicknames
                )
            )
            .all()
        )

    @staticmethod
    def patch_service_user(
        before: schemas.ServiceUserData, after: schemas.ServiceUserData
    ) -> models.ServiceUser:
        before_object = (
            db_manager.session.query(models.ServiceUser)
            .where(models.ServiceUser.ID == before.ID)
            .one()
        )
        before_object.deleted = after.deleted
        if after.deleted:
            db_manager.session.commit()
            return before_object
        before_object.active = after.active
        if after.living_space:
            new_living_space = (
                db_manager.session.query(models.LivingSpace)
                .where(models.LivingSpace.ID == after.living_space.ID)
                .options(
                    with_loader_criteria(
                        models.LivingSpace, lambda cls: cls.deleted == False
                    )
                )
                .one()
            )
            before_object.living_space = new_living_space
        else:
            before_object.living_space = None
        before_object.name = after.name
        new_nicknames = {nn.ID: nn for nn in after.service_user_nicknames}
        for existing in before_object.service_user_nicknames:
            if existing.ID in new_nicknames:
                existing.nickname = new_nicknames[existing.ID].nickname
            else:
                before_object.service_user_nicknames.remove(existing)
                db_manager.session.delete(existing)
        for incoming in after.service_user_nicknames:
            if incoming.ID < 0:
                new_nickname = models.ServiceUserNicknames(
                    nickname=incoming.nickname, service_user=before_object
                )
                before_object.service_user_nicknames.append(new_nickname)
        db_manager.session.commit()
        return before_object

    @staticmethod
    def post_service_users(data: schemas.ServiceUserInput):
        for service_user in data.data_rows:
            user_obj = models.ServiceUser(name=service_user.name)
            if service_user.living_space_id:
                target_living_space = db_manager.session.scalars(
                    select(models.LivingSpace)
                    .where(models.LivingSpace.ID == service_user.living_space_id)
                    .options(
                        with_loader_criteria(
                            models.LivingSpace, lambda cls: cls.deleted == False
                        )
                    )
                ).one()
                user_obj.living_space = target_living_space
            db_manager.session.add(user_obj)
            db_manager.session.flush()
            for nickname in service_user.nicknames:
                nickname_obj = models.ServiceUserNicknames(
                    service_user_id=user_obj.ID, nickname=nickname
                )
                db_manager.session.add(nickname_obj)
                db_manager.session.flush()
        db_manager.session.commit()
        return
