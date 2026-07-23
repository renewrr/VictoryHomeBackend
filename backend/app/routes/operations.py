import flask_jwt_extended

from flask import jsonify
from apiflask import APIBlueprint
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.repositories.operations_repo import OperationsRepository
from app import schemas
from app.decorators import (
    public,
    general,
    privilege_required,
    two_factor_required,
    auto_rollback,
)

operations_bp = APIBlueprint("operations", __name__, tag="Operations System")


@operations_bp.get("/supported_localization")
@flask_jwt_extended.jwt_required()
@operations_bp.output(schemas.ManagementLocalizationResponse)
@general
def get_supported_localization():
    return {"data_rows": OperationsRepository.get_localization()}


@operations_bp.get("/buildings")
@flask_jwt_extended.jwt_required()
@two_factor_required()
@operations_bp.output(schemas.BuildingResponse)
def get_buildings():
    return {"data_rows": OperationsRepository.get_all_buildings()}


@operations_bp.get("/living_spaces")
@flask_jwt_extended.jwt_required()
@two_factor_required()
@operations_bp.output(schemas.ManagementLivingSpaceResponse)
def get_living_spaces():
    return {"data_rows": OperationsRepository.get_all_living_spaces()}


@operations_bp.post("/building")
@flask_jwt_extended.jwt_required()
@privilege_required("MANAGEMENT")
@two_factor_required()
@operations_bp.output(schemas.BuildingModifyResponse)
@operations_bp.input(schemas.NewBuildingRequest, location="json")
@auto_rollback()
def post_building(json_data: schemas.NewBuildingRequest):
    status = OperationsRepository.add_new_building(json_data)
    return {"status": status, "message": "Success"}


@operations_bp.post("/floor")
@flask_jwt_extended.jwt_required()
@privilege_required("MANAGEMENT")
@two_factor_required()
@operations_bp.output(schemas.FloorModifyResponse)
@operations_bp.input(schemas.NewFloorRequest, location="json")
@auto_rollback()
def post_floor(json_data: schemas.NewFloorRequest):
    status = OperationsRepository.add_new_floor(json_data)
    return {"status": status, "message": "Success"}


@operations_bp.post("/room")
@flask_jwt_extended.jwt_required()
@privilege_required("MANAGEMENT")
@two_factor_required()
@operations_bp.output(schemas.RoomModifyResponse)
@operations_bp.input(schemas.NewRoomRequest, location="json")
@auto_rollback()
def post_room(json_data: schemas.NewRoomRequest):
    status = OperationsRepository.add_new_room(json_data)
    return {"status": status, "message": "Success"}


@operations_bp.delete("/building")
@flask_jwt_extended.jwt_required()
@privilege_required("MANAGEMENT")
@two_factor_required()
@operations_bp.output(schemas.BuildingModifyResponse)
@operations_bp.input(schemas.BuildingDeleteRequest, location="json")
@auto_rollback()
def delete_building(json_data: schemas.BuildingDeleteRequest):
    status = OperationsRepository.delete_building(json_data.building_id)
    return {"status": status, "message": "Success"}


@operations_bp.delete("/floor")
@flask_jwt_extended.jwt_required()
@privilege_required("MANAGEMENT")
@two_factor_required()
@operations_bp.output(schemas.FloorModifyResponse)
@operations_bp.input(schemas.FloorDeleteRequest, location="json")
@auto_rollback()
def delete_floor(json_data: schemas.FloorDeleteRequest):
    status = OperationsRepository.delete_floor(json_data.floor_id)
    return {"status": status, "message": "Success"}


@operations_bp.delete("/room")
@flask_jwt_extended.jwt_required()
@privilege_required("MANAGEMENT")
@two_factor_required()
@operations_bp.output(schemas.RoomModifyResponse)
@operations_bp.input(schemas.RoomDeleteRequest, location="json")
@auto_rollback()
def delete_room(json_data: schemas.RoomDeleteRequest):
    status = OperationsRepository.delete_room(json_data.room_id)
    return {"status": status, "message": "Success"}, 200
