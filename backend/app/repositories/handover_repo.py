from app.database import db_manager
from app.models import model_views, models_generated as models
from app.repositories.auth_repo import EmployeeCache
from app import schemas
from typing import Tuple, Sequence
import datetime
import time


from sqlalchemy import select, insert, delete, Integer, or_, text


class HandoverRepository:
    @staticmethod
    def get_filtered_secondary_message(
        message_filter: schemas.HandoverMessageFilter,
    ) -> Tuple[Sequence[model_views.MatSecondaryDetailViewSimple], int]:
        stmt = db_manager.session.query(
            model_views.MatSecondaryDetailViewSimple
        ).filter(model_views.MatSecondaryDetailViewSimple.is_default == False)
        start_date, end_date = message_filter.get(
            "start_date", datetime.datetime.now() - datetime.timedelta(days=1)
        ), message_filter.get("end_date", datetime.datetime.now())
        # When someone search for something between 6/10 and 6/11, we need to search for anything between 6/10 00:00 and 6/12 00:00
        exclusive_end_date = end_date + datetime.timedelta(days=1)
        message_type_ids, shift_ids, creator_ids = (
            message_filter.get("message_type_ids", []),
            message_filter.get("shift_ids", []),
            message_filter.get("creator_ids", []),
        )
        stmt = stmt.filter(
            model_views.MatSecondaryDetailViewSimple.timestamp.between(
                start_date, exclusive_end_date
            )
        )
        if message_type_ids:
            stmt = stmt.filter(
                model_views.MatSecondaryDetailViewSimple.message_type_id.in_(
                    message_type_ids
                )
            )
        if shift_ids:
            stmt = stmt.filter(
                model_views.MatSecondaryDetailViewSimple.shift_id.in_(shift_ids)
            )

        if creator_ids:
            stmt = stmt.filter(
                model_views.MatSecondaryDetailViewSimple.creator_id.in_(creator_ids)
            )
        # GIN
        location_ids, service_user_ids, keywords = (
            message_filter.get("location_ids", []),
            message_filter.get("service_user_ids", []),
            message_filter.get("keywords", []),
        )
        nicknames: dict[int, list[str]] = {}
        for suid in service_user_ids:
            su = (
                db_manager.session.query(models.ServiceUser)
                .where(models.ServiceUser.ID == suid)
                .one()
            )
            nicknames[su.ID] = [su.name]
            for nn in su.service_user_nicknames:
                nicknames[su.ID].append(nn.nickname)

        if location_ids:
            stmt = stmt.filter(
                model_views.MatSecondaryDetailViewSimple.location_ids.op("&&")(
                    location_ids
                )
            )
        if nicknames:
            conditions = [
                model_views.MatSecondaryDetailViewSimple.message_body.ilike(f"%{term}%")
                for nn_list in nicknames.values()
                for term in nn_list
            ]
            stmt = stmt.filter(or_(*conditions))
        page_index, page_size = message_filter.get("page_index", 0), message_filter.get(
            "page_size", 0
        )
        if keywords:
            conditions = [
                model_views.MatSecondaryDetailViewSimple.message_body.ilike(f"%{term}%")
                for term in keywords
            ]
            stmt = stmt.filter(or_(*conditions))

        offset = page_index * page_size
        row_count = stmt.count()
        stmt = (
            stmt.order_by(model_views.MatSecondaryDetailViewSimple.timestamp.desc())
            .limit(page_size)
            .offset(offset)
        )
        return (stmt.all(), row_count)

    @staticmethod
    def get_filtered_handover_message(
        message_filter: schemas.HandoverMessageFilter,
    ):
        t0 = time.perf_counter()
        stmt = db_manager.session.query(model_views.MatMainMessageDetailViewSimple)
        start_date, end_date = message_filter.get(
            "start_date", datetime.datetime.now() - datetime.timedelta(days=1)
        ), message_filter.get("end_date", datetime.datetime.now())
        # When someone search for something between 6/10 and 6/11, we need to search for anything between 6/10 00:00 and 6/12 00:00
        exclusive_end_date = end_date + datetime.timedelta(days=1)
        message_type_ids, shift_ids, creator_ids = (
            message_filter.get("message_type_ids", []),
            message_filter.get("shift_ids", []),
            message_filter.get("creator_ids", []),
        )
        stmt = stmt.filter(
            model_views.MatMainMessageDetailViewSimple.timestamp.between(
                start_date, exclusive_end_date
            )
        )
        if shift_ids:
            stmt = stmt.filter(
                model_views.MatMainMessageDetailViewSimple.shift_id.in_(shift_ids)
            )
        if creator_ids:
            stmt = stmt.filter(
                model_views.MatMainMessageDetailViewSimple.creator_id.in_(creator_ids)
            )
        # GIN
        location_ids, service_user_ids, keywords = (
            message_filter.get("location_ids", []),
            message_filter.get("service_user_ids", []),
            message_filter.get("keywords", []),
        )
        nicknames: dict[int, list[str]] = {}
        for suid in service_user_ids:
            su = db_manager.session.scalars(
                select(models.ServiceUser).where(models.ServiceUser.ID == suid)
            ).one()
            nicknames[su.ID] = [su.name]
            for nn in su.service_user_nicknames:
                nicknames[su.ID].append(nn.nickname)

        if message_type_ids:
            stmt = stmt.filter(
                model_views.MatMainMessageDetailViewSimple.message_type_ids.op("&&")(
                    message_type_ids
                )
            )
        if location_ids:
            stmt = stmt.filter(
                model_views.MatMainMessageDetailViewSimple.location_ids.op("&&")(
                    location_ids
                )
            )
        selected_keywords = []
        if nicknames:
            for nn_list in nicknames.values():
                for term in nn_list:
                    selected_keywords.append(term)
        if keywords:
            for term in keywords:
                selected_keywords.append(term)
        if selected_keywords:
            stmt2 = db_manager.session.query(models.SecondaryMessage.parent_message_id)
            conditions = [
                models.SecondaryMessage.message_body.ilike(f"%{term}%")
                for term in selected_keywords
            ]
            stmt2 = (
                stmt2.filter(or_(*conditions))
                .group_by(models.SecondaryMessage.parent_message_id)
                .distinct()
            )
            sub2 = stmt2.subquery()
            stmt = stmt.join(
                sub2,
                model_views.MatMainMessageDetailViewSimple.ID
                == sub2.c.parent_message_id,
            )
        page_index, page_size = message_filter.get("page_index", 0), message_filter.get(
            "page_size", 0
        )

        offset = page_index * page_size
        row_count = stmt.count()
        stmt = (
            stmt.order_by(model_views.MatMainMessageDetailViewSimple.timestamp.desc())
            .limit(page_size)
            .offset(offset)
        )
        t2 = time.perf_counter()

        print(f"DB + Network Wire Time:  {(t2 - t0) * 1000:.1f} ms", flush=True)

        return (stmt.all(), row_count)

    @staticmethod
    def get_message_types():
        return db_manager.session.query(models.SecondaryMessageTypes).all()

    @staticmethod
    def post_new_message(message_data: schemas.NewMessageInput):
        creator = db_manager.session.scalars(
            select(models.Employee)
            .where(models.Employee.ID == message_data.creator.ID)
            .where(models.Employee.deleted == False)
        ).one()
        main_msg = models.HandoverMessage(
            timestamp=message_data.datetime,
            creator=creator,
            shift=message_data.shift.name,
        )
        db_manager.session.add(main_msg)
        db_manager.session.flush()
        for msg_loc_data in message_data.locations:
            msg_loc = models.MessageLocation(
                parent_message_id=main_msg.ID, location_name=msg_loc_data.name
            )
            db_manager.session.add(msg_loc)
        for secondary_data in message_data.secondary_data:
            secondary_msg = models.SecondaryMessage(
                parent_message_id=main_msg.ID,
                message_body=secondary_data.message_body,
                message_type_id=secondary_data.message_type.ID,
            )
            db_manager.session.add(secondary_msg)
            db_manager.session.flush()
        db_manager.session.execute(
            text(
                "REFRESH MATERIALIZED VIEW CONCURRENTLY personnel.main_message_detail_view_simple;"
            )
        )
        db_manager.session.execute(
            text(
                "REFRESH MATERIALIZED VIEW CONCURRENTLY personnel.secondary_message_detail_view_simple;"
            )
        )
        db_manager.session.commit()

    @staticmethod
    def get_secondary_messages(
        handover_message_id: int,
    ) -> Sequence[model_views.MatSecondaryDetailViewSimple]:
        stmt = (
            select(models.SecondaryMessage, model_views.MatSecondaryDetailViewSimple)
            .join(
                model_views.MatSecondaryDetailViewSimple,
                models.SecondaryMessage.ID
                == model_views.MatSecondaryDetailViewSimple.ID,
            )
            .where(models.SecondaryMessage.parent_message_id == handover_message_id)
        )
        out = db_manager.session.execute(stmt).tuples().all()
        return [o for _, o in out]

    @staticmethod
    def patch_secondary_message(
        before: schemas.SecondaryMessageDetail,
        after: schemas.SecondaryMessageDetail,
        user: EmployeeCache,
    ):
        try:
            original = (
                db_manager.session.query(models.SecondaryMessage)
                .where(models.SecondaryMessage.ID == before.ID)
                .one()
            )
        except:
            return "No object found", None
        if (
            "MANAGEMENT" not in user.slugs
            and original.parent_message.creator_id != user.ID
        ):
            return "No privilege and User mismatch.", original
        original.message_body = after.message_body
        original.is_deleted = after.is_deleted
        db_manager.session.commit()
        return "Success", original
