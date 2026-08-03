import flask_jwt_extended
import time

from flask import jsonify
from apiflask import APIBlueprint, abort
from flask_jwt_extended import jwt_required, get_jwt_identity, get_current_user
from app.repositories.handover_repo import HandoverRepository
from app.repositories.personnel_repo import PersonnelRepository
from app.repositories.operations_repo import OperationsRepository
from app.repositories.service_user_repo import ServiceUserRepository
from app import schemas
from app.decorators import public, general, auto_rollback

handover_bp = APIBlueprint("handover", __name__, tag="Handover System")


@handover_bp.get("/filtered_secondary_message")
@flask_jwt_extended.jwt_required()
@handover_bp.output(schemas.SecondaryHandoverMessageResponse)
@handover_bp.input(
    schemas.HandoverMessageQueryFilter, location="query", arg_name="filter_data"
)
@general
def get_filtered_secondary_message(filter_data: schemas.HandoverMessageFilter):
    data_rows, data_count = HandoverRepository.get_filtered_secondary_message(
        filter_data
    )
    # time.sleep(1) # Artificial lag
    return {"data_rows": data_rows, "data_count": data_count}


@handover_bp.get("/filtered_handover_message")
@flask_jwt_extended.jwt_required()
@handover_bp.output(schemas.MainPagedHandoverMessageResponse)
@handover_bp.input(
    schemas.HandoverMessageQueryFilter, location="query", arg_name="filter_data"
)
@general
def get_filtered_handover_message(filter_data: schemas.HandoverMessageFilter):
    start_time = time.perf_counter()
    data_rows, data_count = HandoverRepository.get_filtered_handover_message(
        filter_data
    )
    process_time = (time.perf_counter() - start_time) * 1000
    # time.sleep(1) # Artificial lag
    print(f"TOTAL HTTP REQUEST TIME: {process_time:.2f} ms", flush=True)
    return {"data_rows": data_rows, "data_count": data_count}


@handover_bp.get("/single_handover_message")
@flask_jwt_extended.jwt_required()
@handover_bp.output(schemas.SingleHandoverMessage)
@handover_bp.input(schemas.MessageQuery, location="query", arg_name="message_query")
@general
def get_targeted_handover_details(message_query: schemas.MessageQuery):
    return {
        "secondary_messages": HandoverRepository.get_secondary_messages(
            message_query.handover_message_id
        )
    }


@handover_bp.post("/new_handover_message")
@flask_jwt_extended.jwt_required()
@handover_bp.input(schemas.NewMessageInput, location="json")
@general
@auto_rollback()
def post_new_message(json_data: schemas.NewMessageInput):
    HandoverRepository.post_new_message(json_data)
    return {}, 200


@handover_bp.get("/filter_option")
@flask_jwt_extended.jwt_required()
@handover_bp.output(schemas.FilterMessageResponse)
@handover_bp.input(schemas.FilterQuery, location="query", arg_name="filter_option")
@general
def get_filter_options(filter_option: schemas.FilterQuery):
    if filter_option.filter_option == "FLOORS":
        return {"data_rows": OperationsRepository.get_possible_locations()}
    if filter_option.filter_option == "SHIFTS":
        return {"data_rows": OperationsRepository.get_shifts()}
    if filter_option.filter_option == "EMPLOYEE":
        return {"data_rows": PersonnelRepository.get_active_employees()}
    if filter_option.filter_option == "SERVICEUSER":
        return {"data_rows": ServiceUserRepository.get_active_service_users()}
    if filter_option.filter_option == "MESSAGETYPE":
        rows = []
        for r in HandoverRepository.get_message_types():
            rows.append({"ID": r.ID, "name": r.message_type})
        return {"data_rows": rows}


@handover_bp.patch("/secondary_message")
@flask_jwt_extended.jwt_required()
@handover_bp.output(schemas.SecondaryEditResponse)
@handover_bp.input(schemas.SecondaryEditRequest, location="json")
@auto_rollback()
@general
def patch_secondary_message(json_data: schemas.SecondaryEditRequest):
    status, secondary = HandoverRepository.patch_secondary_message(
        json_data.before, json_data.after, user=get_current_user()
    )
    if secondary is None:
        abort(410, message=status)
    return {"msg": secondary, "status": status}, 200
