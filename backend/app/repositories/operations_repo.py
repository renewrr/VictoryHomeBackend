from app.database import db_manager
from app.models import model_views, models_generated as models
from app import schemas
from typing import Tuple, Sequence
import datetime


from sqlalchemy import select, insert, delete, Integer, or_
from sqlalchemy.orm import with_loader_criteria, selectinload


class OperationsRepository:
    @staticmethod
    def get_shifts():
        return db_manager.session.query(models.Shifts).all()

    @staticmethod
    def get_building_floors(building_id: int):
        return (
            db_manager.session.query(models.BuildingFloors)
            .where(models.BuildingFloors.building_id == building_id)
            .where(models.Building.deleted == False)
        )

    @staticmethod
    def get_possible_locations():
        return db_manager.session.query(models.PossibleLocations).all()

    @staticmethod
    def get_all_buildings() -> Sequence[models.Building]:
        stmt = select(models.Building).options(
            selectinload(models.Building.building_floors)
            .selectinload(models.BuildingFloors.living_space)
            .selectinload(models.LivingSpace.service_user),
            with_loader_criteria(models.Building, lambda cls: cls.deleted == False),
            with_loader_criteria(
                models.BuildingFloors, lambda cls: cls.deleted == False
            ),
            with_loader_criteria(models.LivingSpace, lambda cls: cls.deleted == False),
            with_loader_criteria(models.ServiceUser, lambda cls: cls.deleted == False),
        )
        buildings = db_manager.session.scalars(stmt).all()
        return buildings

    @staticmethod
    def get_all_living_spaces() -> Sequence[models.LivingSpace]:
        stmt = select(models.LivingSpace).where(models.LivingSpace.deleted == False)
        return db_manager.session.scalars(stmt).all()

    @staticmethod
    def get_localization():
        stmt = select(models.SupportedLocalization)
        return db_manager.session.scalars(stmt).all()

    @staticmethod
    def add_new_building(building_request: schemas.NewBuildingRequest) -> bool:
        building_obj = models.Building(
            name=building_request.name, address=building_request.address
        )
        db_manager.session.add(building_obj)
        db_manager.session.commit()
        return True

    @staticmethod
    def add_new_floor(floor_request: schemas.NewFloorRequest) -> bool:
        target_building = db_manager.session.scalars(
            select(models.Building).where(
                models.Building.ID == floor_request.building_id
            )
        ).one()
        floor_obj = models.BuildingFloors(
            floor_name=floor_request.name, building=target_building
        )
        db_manager.session.add(floor_obj)
        db_manager.session.commit()
        return True

    @staticmethod
    def add_new_room(room_request: schemas.NewRoomRequest) -> bool:
        target_floor = db_manager.session.scalars(
            select(models.BuildingFloors).where(
                models.BuildingFloors.ID == room_request.floor_id
            )
        ).one()
        room_obj = models.LivingSpace(name=room_request.name, floor=target_floor)
        db_manager.session.add(room_obj)
        db_manager.session.commit()
        return True

    @staticmethod
    def delete_room(room_id: int) -> bool:
        target_room = db_manager.session.scalars(
            select(models.LivingSpace).where(models.LivingSpace.ID == room_id)
        ).one()
        target_room.deleted = True
        target_room.service_user = []
        db_manager.session.commit()

        return True

    @staticmethod
    def delete_floor(floor_id: int) -> bool:
        target_floor = db_manager.session.scalars(
            select(models.BuildingFloors).where(models.BuildingFloors.ID == floor_id)
        ).one()
        target_floor.deleted = True
        db_manager.session.commit()
        for room in target_floor.living_space:
            OperationsRepository.delete_room(room.ID)
        return True

    @staticmethod
    def delete_building(building_id: int) -> bool:
        target_building = db_manager.session.scalars(
            select(models.Building).where(models.Building.ID == building_id)
        ).one()
        target_building.deleted = True
        db_manager.session.commit()
        for floor in target_building.building_floors:
            OperationsRepository.delete_floor(floor.ID)
        return True
