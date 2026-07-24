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
        handle_behavioral(answers, main_msg)
        handle_equipment(answers, main_msg)
        handle_familial(answers, main_msg)
        handle_others(answers, main_msg)


def handle_physcon(answers: dict[str, str], main_msg: models.HandoverMessage):
    physcon_str = answers.get(
        "服務對象身體狀況\n  (Tình trạng sức khỏe và khám bệnh)  ", ""
    )
    if not physcon_str or "無 Không có gì bất thường" in physcon_str:
        return
    phys_msg = models.SecondaryMessage(
        parent_message_id=main_msg.ID, message_type_id=1, message_body=physcon_str
    )
    main_msg.secondary_message.append(phys_msg)
    db_manager.session.add(phys_msg)
    db_manager.session.commit()


def handle_behavioral(answers: dict[str, str], main_msg: models.HandoverMessage):
    beh_str = answers.get(
        "服務使用者行為問題\nVấn đề hành vi của người sử dụng dịch vụ  ", ""
    ).strip()
    if not beh_str or "無 Không có gì bất thường" in beh_str:
        return
    beh_msg = models.SecondaryMessage(
        parent_message_id=main_msg.ID, message_type_id=3, message_body=beh_str
    )
    main_msg.secondary_message.append(beh_msg)
    db_manager.session.add(beh_msg)
    db_manager.session.commit()


def handle_equipment(answers: dict[str, str], main_msg: models.HandoverMessage):
    eq_str = answers.get(
        "設施設備  Cơ sở vật chất, thiết bị \n若有損壞，請在其他項目填寫物品，並註記是否有填維修單  Nếu có hư hỏng, vui lòng ghi rõ vật phẩm vào mục "
        "Khác"
        " và chú thích đã điền đơn sửa chữa chưa ",
        "",
    ).strip()
    if not eq_str or "無 Không có gì bất thường" in eq_str:
        return
    eq_msg = models.SecondaryMessage(
        parent_message_id=main_msg.ID, message_type_id=4, message_body=eq_str
    )
    main_msg.secondary_message.append(eq_msg)
    db_manager.session.add(eq_msg)
    db_manager.session.commit()


def handle_familial(answers: dict[str, str], main_msg: models.HandoverMessage):
    fam_str = answers.get(
        "家屬交辦事項  Nội dung gia đình bàn giao ",
        "",
    ).strip()
    if not fam_str or fam_str == "無":
        return
    fam_msg = models.SecondaryMessage(
        parent_message_id=main_msg.ID, message_type_id=5, message_body=fam_str
    )
    main_msg.secondary_message.append(fam_msg)
    db_manager.session.add(fam_msg)
    db_manager.session.commit()


def handle_others(answers: dict[str, str], main_msg: models.HandoverMessage):
    otr_str = answers.get(
        "其他  Khác\n非上述項目，但需要讓大家知道的 \n (Không thuộc các mục trên nhưng cần mọi người biết)  ",
        "",
    ).strip()
    if not otr_str or "一切平安 Mọi việc bình an, ổn định" in otr_str:
        return
    otr_msg = models.SecondaryMessage(
        parent_message_id=main_msg.ID, message_type_id=6, message_body=otr_str
    )
    main_msg.secondary_message.append(otr_msg)
    db_manager.session.add(otr_msg)
    db_manager.session.commit()
