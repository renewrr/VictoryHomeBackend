from typing import Optional
import datetime

from sqlalchemy import (
    ARRAY,
    Boolean,
    CheckConstraint,
    Column,
    Date,
    DateTime,
    ForeignKeyConstraint,
    Integer,
    PrimaryKeyConstraint,
    String,
    Table,
    UniqueConstraint,
    text,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class MainMessageLocationsView(Base):
    __tablename__ = "main_floors"
    __table_args__ = {"schema": "personnel"}
    ID: Mapped[int] = mapped_column(Integer, primary_key=True)
    floors: Mapped[list[str]] = mapped_column(ARRAY(String))


class MainMessageInvolvedUsersView(Base):
    __tablename__ = "main_involved"
    __table_args__ = {"schema": "personnel"}
    ID: Mapped[int] = mapped_column(Integer, primary_key=True)
    array_agg: Mapped[list[int]] = mapped_column(ARRAY(Integer()))


class UserNicknameAggregateView(Base):
    __tablename__ = "nickname_agg"
    __table_args__ = {"schema": "personnel"}
    ID: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(30))
    array_agg: Mapped[list[str]] = mapped_column(ARRAY(String))


class MainMessageDetailView(Base):
    __tablename__ = "main_message_detail_view"
    __table_args__ = {"schema": "personnel"}
    ID: Mapped[int] = mapped_column(Integer, primary_key=True)
    timestamp: Mapped[datetime.datetime] = mapped_column(DateTime)
    shift_id: Mapped[int] = mapped_column(Integer)
    shift_name: Mapped[str] = mapped_column(String(30))
    creator_id: Mapped[int] = mapped_column(Integer)
    creator_name: Mapped[str] = mapped_column(String(30))
    service_user_ids: Mapped[list[int]] = mapped_column(ARRAY(Integer))
    service_user_names: Mapped[list[str]] = mapped_column(ARRAY(String))
    message_type_ids: Mapped[list[int]] = mapped_column(ARRAY(Integer))
    message_type_names: Mapped[list[str]] = mapped_column(ARRAY(String))
    location_ids: Mapped[list[int]] = mapped_column(ARRAY(Integer))
    location_names: Mapped[list[str]] = mapped_column(ARRAY(String))


class SecondaryMessageDetailView(Base):
    __tablename__ = "secondary_message_detail_view"
    __table_args__ = {"schema": "personnel"}
    ID: Mapped[int] = mapped_column(Integer, primary_key=True)
    timestamp: Mapped[datetime.datetime] = mapped_column(DateTime)
    shift_id: Mapped[int] = mapped_column(Integer)
    shift_name: Mapped[str] = mapped_column(String(30))
    creator_id: Mapped[int] = mapped_column(Integer)
    creator_name: Mapped[str] = mapped_column(String(30))
    service_user_ids: Mapped[list[int]] = mapped_column(ARRAY(Integer), default=list)
    service_user_names: Mapped[list[str]] = mapped_column(ARRAY(String), default=list)
    message_type_id: Mapped[int] = mapped_column(Integer)
    message_type_name: Mapped[str] = mapped_column(String)
    location_ids: Mapped[list[int]] = mapped_column(ARRAY(Integer))
    location_names: Mapped[list[str]] = mapped_column(ARRAY(String))
    message_body: Mapped[str] = mapped_column(String(500))


class MaterializedSecondaryMessageDetailView(Base):
    __tablename__ = "mat_secondary_message_detail_view"
    __table_args__ = {"schema": "personnel"}
    ID: Mapped[int] = mapped_column(Integer, primary_key=True)
    timestamp: Mapped[datetime.datetime] = mapped_column(DateTime)
    shift_id: Mapped[int] = mapped_column(Integer)
    shift_name: Mapped[str] = mapped_column(String(30))
    creator_id: Mapped[int] = mapped_column(Integer)
    creator_name: Mapped[str] = mapped_column(String(30))
    service_user_ids: Mapped[list[int]] = mapped_column(ARRAY(Integer), default=list)
    service_user_names: Mapped[list[str]] = mapped_column(ARRAY(String), default=list)
    message_type_id: Mapped[int] = mapped_column(Integer)
    message_type_name: Mapped[str] = mapped_column(String)
    location_ids: Mapped[list[int]] = mapped_column(ARRAY(Integer))
    location_names: Mapped[list[str]] = mapped_column(ARRAY(String))
    message_body: Mapped[str] = mapped_column(String(500))


class MaterializedMainMessageDetailView(Base):
    __tablename__ = "mat_main_message_detail_view"
    __table_args__ = {"schema": "personnel"}
    ID: Mapped[int] = mapped_column(Integer, primary_key=True)
    timestamp: Mapped[datetime.datetime] = mapped_column(DateTime)
    shift_id: Mapped[int] = mapped_column(Integer)
    shift_name: Mapped[str] = mapped_column(String(30))
    creator_id: Mapped[int] = mapped_column(Integer)
    creator_name: Mapped[str] = mapped_column(String(30))
    service_user_ids: Mapped[list[int]] = mapped_column(ARRAY(Integer), default=list)
    service_user_names: Mapped[list[str]] = mapped_column(ARRAY(String), default=list)
    message_type_ids: Mapped[list[int]] = mapped_column(ARRAY(Integer))
    message_type_names: Mapped[list[str]] = mapped_column(ARRAY(String))
    location_ids: Mapped[list[int]] = mapped_column(ARRAY(Integer), default=list)
    location_names: Mapped[list[str]] = mapped_column(ARRAY(String), default=list)


class ServiceUserDetailsView(Base):
    __tablename__ = "service_user_details"
    __table_args__ = {"schema": "personnel"}
    ID: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_name: Mapped[str] = mapped_column(String(30))
    start_date: Mapped[datetime.date] = mapped_column(Date)
    active: Mapped[bool] = mapped_column(Boolean)
    deleted: Mapped[bool] = mapped_column(Boolean)
    room_id: Mapped[int] = mapped_column(Integer)
    room_name: Mapped[str] = mapped_column(String(30))
    floor: Mapped[str] = mapped_column(String(30))
    building_name: Mapped[str] = mapped_column(String(30))
    nicknames: Mapped[list[str]] = mapped_column(ARRAY(String))


class MatMainMessageDetailViewSimple(Base):
    __tablename__ = "main_message_detail_view_simple"
    __table_args__ = {"schema": "personnel"}
    ID: Mapped[int] = mapped_column(Integer, primary_key=True)
    timestamp: Mapped[datetime.datetime] = mapped_column(DateTime)
    shift_id: Mapped[int] = mapped_column(Integer)
    shift_name: Mapped[str] = mapped_column(String(30))
    creator_id: Mapped[int] = mapped_column(Integer)
    creator_name: Mapped[str] = mapped_column(String(30))
    message_type_ids: Mapped[list[int]] = mapped_column(ARRAY(Integer))
    message_type_names: Mapped[list[str]] = mapped_column(ARRAY(String))
    location_ids: Mapped[list[int]] = mapped_column(ARRAY(Integer), default=list)
    location_names: Mapped[list[str]] = mapped_column(ARRAY(String), default=list)


class MatSecondaryDetailViewSimple(Base):
    __tablename__ = "secondary_message_detail_view_simple"
    __table_args__ = {"schema": "personnel"}
    ID: Mapped[int] = mapped_column(Integer, primary_key=True)
    timestamp: Mapped[datetime.datetime] = mapped_column(DateTime)
    shift_id: Mapped[int] = mapped_column(Integer)
    shift_name: Mapped[str] = mapped_column(String(30))
    creator_id: Mapped[int] = mapped_column(Integer)
    creator_name: Mapped[str] = mapped_column(String(30))
    message_type_id: Mapped[int] = mapped_column(Integer)
    message_type_name: Mapped[str] = mapped_column(String)
    location_ids: Mapped[list[int]] = mapped_column(ARRAY(Integer))
    location_names: Mapped[list[str]] = mapped_column(ARRAY(String))
    message_body: Mapped[str] = mapped_column(String(500))
    is_default: Mapped[bool] = mapped_column(Boolean)
