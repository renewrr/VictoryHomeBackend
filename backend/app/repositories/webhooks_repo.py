from app.database import db_manager
from app.models import model_views, models_generated as models
from app import schemas
from typing import Tuple, Sequence
import datetime


from sqlalchemy import select, insert, delete, Integer, or_
from sqlalchemy.orm import with_loader_criteria, selectinload, noload


class WebhookRepository:

    @staticmethod
    def post_webhook_message(
        response_id: str, timestamp_str: str, answers: dict[str, str]
    ):
        timestamp = datetime.datetime.fromisoformat(timestamp_str)
        employee_name = answers.get("交班者 Người giao ca ", "").strip("")
        if not employee_name:
            return False
        try:
            employee = (
                db_manager.session.query(models.Employee)
                .where(models.Employee.name == employee_name)
                .one()
            )
        except:
            employee = models.Employee(name=employee_name)
            db_manager.session.add(employee)
            db_manager.session.commit()
        shift_str = answers.get("班別 Ca làm việc ", "").strip()
        if "白班" in shift_str:
            shift_str = "day"
        elif "小夜班" in shift_str:
            shift_str = "evening"
        elif "大夜班" in shift_str:
            shift_str = "night"
        else:
            shift_str = "day"
        shift = (
            db_manager.session.query(models.Shifts)
            .where(models.Shifts.name == shift_str)
            .one()
        )
        main_msg = models.HandoverMessage(
            timestamp=timestamp,
            creator_id=employee.ID,
            shift=shift.name,
            google_form_response_id=response_id,
        )
        db_manager.session.add(main_msg)
        db_manager.session.commit()
        handle_physcon(answers, main_msg)


def handle_physcon(answers: dict[str, str], main_msg: models.HandoverMessage):
    physcon_str = answers.get(
        "服務對象身體狀況\n  (Tình trạng sức khỏe và khám bệnh)  ", ""
    )
    print(physcon_str, flush=True)
    if not physcon_str or "無 Không có gì bất thường" in physcon_str:
        return
    phys_msg = models.SecondaryMessage(
        parent_message_id=main_msg.ID, message_type_id=1, message_body=physcon_str
    )
    main_msg.secondary_message.append(phys_msg)
    db_manager.session.add(main_msg)
    db_manager.session.commit()
