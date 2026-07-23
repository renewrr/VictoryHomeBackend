from typing import Optional
import datetime

from sqlalchemy import ARRAY, Boolean, CheckConstraint, Column, Date, DateTime, ForeignKeyConstraint, Index, Integer, PrimaryKeyConstraint, String, Table, UniqueConstraint, text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

class Base(DeclarativeBase):
    pass


class Building(Base):
    __tablename__ = 'building'
    __table_args__ = (
        PrimaryKeyConstraint('ID', name='building_pkey'),
        Index('active_building_name_unique', 'name', postgresql_where='(deleted = false)', unique=True),
        {'schema': 'operation'}
    )

    ID: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(30), nullable=False)
    address: Mapped[str] = mapped_column(String(300), nullable=False)
    deleted: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text('false'))
    version_id: Mapped[int] = mapped_column(Integer, nullable=False, server_default=text('1'))

    building_floors: Mapped[list['BuildingFloors']] = relationship('BuildingFloors', back_populates='building')
    classroom: Mapped[list['Classroom']] = relationship('Classroom', back_populates='building')


class MedicalFacilities(Base):
    __tablename__ = 'medical_facilities'
    __table_args__ = (
        PrimaryKeyConstraint('ID', name='medical_facilities_pkey'),
        {'schema': 'operation'}
    )

    ID: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    address: Mapped[Optional[str]] = mapped_column(String(100))


class Shifts(Base):
    __tablename__ = 'shifts'
    __table_args__ = (
        PrimaryKeyConstraint('name', name='shifts_pkey'),
        {'schema': 'operation'}
    )

    name: Mapped[str] = mapped_column(String(30), primary_key=True)
    ID: Mapped[int] = mapped_column(Integer, nullable=False)

    shift_localization: Mapped[list['ShiftLocalization']] = relationship('ShiftLocalization', back_populates='shifts')
    handover_message: Mapped[list['HandoverMessage']] = relationship('HandoverMessage', back_populates='shifts')


class SupportedLocalization(Base):
    __tablename__ = 'supported_localization'
    __table_args__ = (
        PrimaryKeyConstraint('name', name='supported_localization_pkey'),
        {'schema': 'operation'}
    )

    name: Mapped[str] = mapped_column(String(30), primary_key=True)

    message_location_localization: Mapped[list['MessageLocationLocalization']] = relationship('MessageLocationLocalization', back_populates='supported_localization')
    secondary_message_type_localization: Mapped[list['SecondaryMessageTypeLocalization']] = relationship('SecondaryMessageTypeLocalization', back_populates='supported_localization')
    shift_localization: Mapped[list['ShiftLocalization']] = relationship('ShiftLocalization', back_populates='supported_localization')
    employee: Mapped[list['Employee']] = relationship('Employee', back_populates='supported_localization')
    service_user_name_localization: Mapped[list['ServiceUserNameLocalization']] = relationship('ServiceUserNameLocalization', back_populates='supported_localization')


class Auth(Base):
    __tablename__ = 'auth'
    __table_args__ = (
        PrimaryKeyConstraint('ID', name='auth_pkey'),
        Index('partial_account_unique', 'account', postgresql_where='(deleted = false)', postgresql_with={'deduplicate_items': 'true'}),
        {'schema': 'personnel'}
    )

    account: Mapped[str] = mapped_column(String(30), nullable=False)
    password: Mapped[str] = mapped_column(String(30), nullable=False)
    ID: Mapped[int] = mapped_column(Integer, primary_key=True)
    deleted: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text('false'))
    auth_version: Mapped[int] = mapped_column(Integer, nullable=False, server_default=text('1'))
    totp_secret: Mapped[Optional[str]] = mapped_column(String(32))

    employee: Mapped[Optional['Employee']] = relationship('Employee', uselist=False, back_populates='auth')


t_main_floors = Table(
    'main_floors', Base.metadata,
    Column('ID', Integer),
    Column('floors', ARRAY(String())),
    schema='personnel'
)


t_main_involved = Table(
    'main_involved', Base.metadata,
    Column('ID', Integer),
    Column('array_agg', ARRAY(Integer())),
    schema='personnel'
)


t_main_message_detail_view = Table(
    'main_message_detail_view', Base.metadata,
    Column('ID', Integer),
    Column('timestamp', DateTime(True)),
    Column('shift_id', Integer),
    Column('shift_name', String(30)),
    Column('creator_id', Integer),
    Column('creator_name', String(30)),
    Column('service_user_ids', ARRAY(Integer())),
    Column('service_user_names', ARRAY(String())),
    Column('message_type_ids', ARRAY(Integer())),
    Column('message_type_names', ARRAY(String())),
    Column('location_ids', ARRAY(Integer())),
    Column('location_names', ARRAY(String())),
    schema='personnel'
)


t_main_message_detail_view_simple = Table(
    'main_message_detail_view_simple', Base.metadata,
    Column('ID', Integer),
    Column('timestamp', DateTime(True)),
    Column('shift_id', Integer),
    Column('shift_name', String(30)),
    Column('creator_id', Integer),
    Column('creator_name', String(30)),
    Column('message_type_ids', ARRAY(Integer())),
    Column('message_type_names', ARRAY(String())),
    Column('location_ids', ARRAY(Integer())),
    Column('location_names', ARRAY(String())),
    Index('idx_main_id', 'ID'),
    schema='personnel'
)


t_mat_main_message_detail_view = Table(
    'mat_main_message_detail_view', Base.metadata,
    Column('ID', Integer),
    Column('timestamp', DateTime(True)),
    Column('shift_id', Integer),
    Column('shift_name', String(30)),
    Column('creator_id', Integer),
    Column('creator_name', String(30)),
    Column('service_user_ids', ARRAY(Integer())),
    Column('service_user_names', ARRAY(String())),
    Column('message_type_ids', ARRAY(Integer())),
    Column('message_type_names', ARRAY(String())),
    Column('location_ids', ARRAY(Integer())),
    Column('location_names', ARRAY(String())),
    Index('main_idxs', 'ID', unique=True),
    schema='personnel'
)


t_mat_secondary_message_detail_view = Table(
    'mat_secondary_message_detail_view', Base.metadata,
    Column('ID', Integer),
    Column('timestamp', DateTime(True)),
    Column('shift_name', String(30)),
    Column('shift_id', Integer),
    Column('creator_id', Integer),
    Column('creator_name', String(30)),
    Column('message_type_name', String(30)),
    Column('message_type_id', Integer),
    Column('message_body', String(500)),
    Column('service_user_names', ARRAY(String())),
    Column('service_user_ids', ARRAY(Integer())),
    Column('location_names', ARRAY(String())),
    Column('location_ids', ARRAY(Integer())),
    Index('idx_messages_body_cjk', 'message_body', postgresql_ops={'message_body': 'gin_bigm_ops'}, postgresql_using='gin'),
    Index('secondary_main_idx', 'ID', unique=True),
    Index('secondary_su_id_gin', 'service_user_ids', postgresql_using='gin', postgresql_with={'fastupdate': 'true'}),
    schema='personnel'
)


t_nickname_agg = Table(
    'nickname_agg', Base.metadata,
    Column('ID', Integer),
    Column('name', String(30)),
    Column('array_agg', ARRAY(String())),
    schema='personnel'
)


class Permissions(Base):
    __tablename__ = 'permissions'
    __table_args__ = (
        PrimaryKeyConstraint('ID', name='permissions_pkey'),
        {'schema': 'personnel'}
    )

    ID: Mapped[int] = mapped_column(Integer, primary_key=True)
    perm_slug: Mapped[str] = mapped_column(String(50), nullable=False)

    role_perms: Mapped[list['RolePerms']] = relationship('RolePerms', back_populates='perm')
    employee_perms: Mapped[list['EmployeePerms']] = relationship('EmployeePerms', back_populates='perm')


class PossibleLocations(Base):
    __tablename__ = 'possible_locations'
    __table_args__ = (
        PrimaryKeyConstraint('name', name='possible_locations_pkey'),
        {'schema': 'personnel'}
    )

    name: Mapped[str] = mapped_column(String(30), primary_key=True)
    ID: Mapped[int] = mapped_column(Integer, nullable=False)

    message_location_localization: Mapped[list['MessageLocationLocalization']] = relationship('MessageLocationLocalization', back_populates='possible_locations')
    message_location: Mapped[list['MessageLocation']] = relationship('MessageLocation', back_populates='possible_locations')


class Roles(Base):
    __tablename__ = 'roles'
    __table_args__ = (
        PrimaryKeyConstraint('ID', name='roles_pkey'),
        {'schema': 'personnel'}
    )

    ID: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(30), nullable=False)

    role_perms: Mapped[list['RolePerms']] = relationship('RolePerms', back_populates='role')
    employee_roles: Mapped[list['EmployeeRoles']] = relationship('EmployeeRoles', back_populates='role')


t_secondary_involved = Table(
    'secondary_involved', Base.metadata,
    Column('ID', Integer),
    Column('service_users', ARRAY(Integer())),
    schema='personnel'
)


t_secondary_message_detail_view = Table(
    'secondary_message_detail_view', Base.metadata,
    Column('ID', Integer),
    Column('timestamp', DateTime(True)),
    Column('shift_name', String(30)),
    Column('shift_id', Integer),
    Column('creator_id', Integer),
    Column('creator_name', String(30)),
    Column('message_type_name', String(30)),
    Column('message_type_id', Integer),
    Column('message_body', String(500)),
    Column('service_user_names', ARRAY(String())),
    Column('service_user_ids', ARRAY(Integer())),
    Column('location_names', ARRAY(String())),
    Column('location_ids', ARRAY(Integer())),
    schema='personnel'
)


t_secondary_message_detail_view_simple = Table(
    'secondary_message_detail_view_simple', Base.metadata,
    Column('ID', Integer),
    Column('timestamp', DateTime(True)),
    Column('shift_name', String(30)),
    Column('shift_id', Integer),
    Column('creator_id', Integer),
    Column('creator_name', String(30)),
    Column('message_type_name', String(30)),
    Column('message_type_id', Integer),
    Column('message_body', String(500)),
    Column('location_names', ARRAY(String())),
    Column('location_ids', ARRAY(Integer())),
    Index('idx_secondary_id', 'ID'),
    schema='personnel'
)


class SecondaryMessageTypes(Base):
    __tablename__ = 'secondary_message_types'
    __table_args__ = (
        PrimaryKeyConstraint('ID', name='secondary_message_types_pkey'),
        {'schema': 'personnel'}
    )

    ID: Mapped[int] = mapped_column(Integer, primary_key=True)
    message_type: Mapped[str] = mapped_column(String(30), nullable=False)

    secondary_message_type_localization: Mapped[list['SecondaryMessageTypeLocalization']] = relationship('SecondaryMessageTypeLocalization', back_populates='message_type')
    secondary_message: Mapped[list['SecondaryMessage']] = relationship('SecondaryMessage', back_populates='message_type')


class ServiceGroup(Base):
    __tablename__ = 'service_group'
    __table_args__ = (
        PrimaryKeyConstraint('ID', name='service_group_pkey'),
        UniqueConstraint('name', name='service_group_name_key'),
        {'schema': 'personnel'}
    )

    ID: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(30), nullable=False)
    creation_date: Mapped[datetime.date] = mapped_column(Date, nullable=False, server_default=text('CURRENT_DATE'))

    group_enrollment: Mapped[list['GroupEnrollment']] = relationship('GroupEnrollment', back_populates='group')


t_service_user_details = Table(
    'service_user_details', Base.metadata,
    Column('ID', Integer),
    Column('user_name', String(30)),
    Column('start_date', Date),
    Column('active', Boolean),
    Column('deleted', Boolean),
    Column('room_id', Integer),
    Column('room_name', String(30)),
    Column('floor', String(30)),
    Column('building_name', String(30)),
    Column('nicknames', ARRAY(String())),
    schema='personnel'
)


class MessageLocationLocalization(Base):
    __tablename__ = 'message_location_localization'
    __table_args__ = (
        ForeignKeyConstraint(['locale'], ['operation.supported_localization.name'], onupdate='CASCADE', name='message_location_localization_locale_fkey'),
        ForeignKeyConstraint(['location_name'], ['personnel.possible_locations.name'], ondelete='CASCADE', onupdate='CASCADE', name='message_location_localization_location_name_fkey'),
        PrimaryKeyConstraint('location_name', 'locale', name='message_location_localization_pkey'),
        {'schema': 'localization'}
    )

    location_name: Mapped[str] = mapped_column(String(30), primary_key=True)
    locale: Mapped[str] = mapped_column(String(30), primary_key=True)
    text_: Mapped[Optional[str]] = mapped_column('text', String(30))

    supported_localization: Mapped['SupportedLocalization'] = relationship('SupportedLocalization', back_populates='message_location_localization')
    possible_locations: Mapped['PossibleLocations'] = relationship('PossibleLocations', back_populates='message_location_localization')


class SecondaryMessageTypeLocalization(Base):
    __tablename__ = 'secondary_message_type_localization'
    __table_args__ = (
        ForeignKeyConstraint(['locale'], ['operation.supported_localization.name'], onupdate='CASCADE', name='secondary_message_type_localization_locale_fkey'),
        ForeignKeyConstraint(['message_type_id'], ['personnel.secondary_message_types.ID'], ondelete='CASCADE', onupdate='CASCADE', name='secondary_message_type_localization_message_type_id_fkey'),
        PrimaryKeyConstraint('ID', name='secondary_message_type_localization_pkey'),
        {'schema': 'localization'}
    )

    ID: Mapped[int] = mapped_column(Integer, primary_key=True)
    message_type_id: Mapped[int] = mapped_column(Integer, nullable=False)
    locale: Mapped[str] = mapped_column(String(30), nullable=False)
    localization: Mapped[str] = mapped_column(String(30), nullable=False)

    supported_localization: Mapped['SupportedLocalization'] = relationship('SupportedLocalization', back_populates='secondary_message_type_localization')
    message_type: Mapped['SecondaryMessageTypes'] = relationship('SecondaryMessageTypes', back_populates='secondary_message_type_localization')


class BuildingFloors(Base):
    __tablename__ = 'building_floors'
    __table_args__ = (
        ForeignKeyConstraint(['building_id'], ['operation.building.ID'], ondelete='CASCADE', onupdate='CASCADE', name='building_floors_building_id_fkey'),
        PrimaryKeyConstraint('ID', name='building_floors_pkey'),
        Index('active_floor_name_unique', 'building_id', 'floor_name', postgresql_where='(deleted = false)', unique=True),
        {'schema': 'operation'}
    )

    ID: Mapped[int] = mapped_column(Integer, primary_key=True)
    building_id: Mapped[int] = mapped_column(Integer, nullable=False)
    floor_name: Mapped[str] = mapped_column(String(30), nullable=False)
    deleted: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text('false'))
    version_id: Mapped[int] = mapped_column(Integer, nullable=False, server_default=text('1'))

    building: Mapped['Building'] = relationship('Building', back_populates='building_floors')
    living_space: Mapped[list['LivingSpace']] = relationship('LivingSpace', back_populates='floor')


class Classroom(Base):
    __tablename__ = 'classroom'
    __table_args__ = (
        CheckConstraint('floor > 0', name='floor constraint'),
        ForeignKeyConstraint(['building_id'], ['operation.building.ID'], name='classroom_building_id_fkey'),
        PrimaryKeyConstraint('ID', name='classroom_pkey'),
        {'schema': 'operation'}
    )

    ID: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(30), nullable=False, server_default=text("'Default room name'::character varying"))
    building_id: Mapped[int] = mapped_column(Integer, nullable=False, server_default=text('1'))
    floor: Mapped[int] = mapped_column(Integer, nullable=False, server_default=text('1'))

    building: Mapped['Building'] = relationship('Building', back_populates='classroom')


class ShiftLocalization(Base):
    __tablename__ = 'shift_localization'
    __table_args__ = (
        ForeignKeyConstraint(['localization'], ['operation.supported_localization.name'], ondelete='CASCADE', onupdate='CASCADE', name='shift_localization_localization_fkey'),
        ForeignKeyConstraint(['shift_name'], ['operation.shifts.name'], ondelete='CASCADE', onupdate='CASCADE', name='shift_localization_shift_name_fkey'),
        PrimaryKeyConstraint('shift_name', 'localization', name='shift_localization_pkey'),
        {'schema': 'operation'}
    )

    shift_name: Mapped[str] = mapped_column(String(30), primary_key=True)
    localization: Mapped[str] = mapped_column(String(30), primary_key=True)
    text_: Mapped[str] = mapped_column('text', String(30), nullable=False)

    supported_localization: Mapped['SupportedLocalization'] = relationship('SupportedLocalization', back_populates='shift_localization')
    shifts: Mapped['Shifts'] = relationship('Shifts', back_populates='shift_localization')


class Employee(Base):
    __tablename__ = 'employee'
    __table_args__ = (
        ForeignKeyConstraint(['auth_id'], ['personnel.auth.ID'], ondelete='CASCADE', onupdate='CASCADE', name='employee_auth_id_fkey'),
        ForeignKeyConstraint(['localization'], ['operation.supported_localization.name'], ondelete='SET DEFAULT', onupdate='CASCADE', name='employee_localization_fkey'),
        PrimaryKeyConstraint('ID', name='employee_pkey'),
        UniqueConstraint('auth_id', name='auth_single'),
        {'schema': 'personnel'}
    )

    ID: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(30), nullable=False, server_default=text("'John Doe'::character varying"))
    date_of_employment: Mapped[datetime.date] = mapped_column(Date, nullable=False, server_default=text('CURRENT_DATE'))
    company_email: Mapped[str] = mapped_column(String(100), nullable=False, server_default=text("'placeholder@vhome.com'::character varying"))
    localization: Mapped[str] = mapped_column(String(30), nullable=False, server_default=text("'Chinese'::character varying"))
    deleted: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text('false'))
    auth_id: Mapped[Optional[int]] = mapped_column(Integer)

    auth: Mapped[Optional['Auth']] = relationship('Auth', back_populates='employee')
    supported_localization: Mapped['SupportedLocalization'] = relationship('SupportedLocalization', back_populates='employee')
    employee_perms: Mapped[list['EmployeePerms']] = relationship('EmployeePerms', back_populates='employee')
    employee_roles: Mapped[list['EmployeeRoles']] = relationship('EmployeeRoles', back_populates='employee')
    handover_message: Mapped[list['HandoverMessage']] = relationship('HandoverMessage', back_populates='creator')
    secondary_message_employee: Mapped[list['SecondaryMessageEmployee']] = relationship('SecondaryMessageEmployee', back_populates='employee')


class RolePerms(Base):
    __tablename__ = 'role_perms'
    __table_args__ = (
        ForeignKeyConstraint(['perm_id'], ['personnel.permissions.ID'], ondelete='CASCADE', onupdate='CASCADE', name='role_perms_perm_id_fkey'),
        ForeignKeyConstraint(['role_id'], ['personnel.roles.ID'], ondelete='CASCADE', onupdate='CASCADE', name='role_perms_role_id_fkey'),
        PrimaryKeyConstraint('ID', name='role_perms_pkey'),
        {'schema': 'personnel'}
    )

    ID: Mapped[int] = mapped_column(Integer, primary_key=True)
    role_id: Mapped[int] = mapped_column(Integer, nullable=False)
    perm_id: Mapped[int] = mapped_column(Integer, nullable=False)

    perm: Mapped['Permissions'] = relationship('Permissions', back_populates='role_perms')
    role: Mapped['Roles'] = relationship('Roles', back_populates='role_perms')


class LivingSpace(Base):
    __tablename__ = 'living_space'
    __table_args__ = (
        CheckConstraint('floor_id > 0', name='floor_constraint'),
        ForeignKeyConstraint(['floor_id'], ['operation.building_floors.ID'], ondelete='CASCADE', onupdate='CASCADE', name='living_space_floor_id_fkey'),
        PrimaryKeyConstraint('ID', name='living_space_pkey'),
        Index('active_room_name_unique', 'floor_id', 'name', postgresql_where='(deleted = false)', unique=True),
        Index('living_space_name_active', 'name', postgresql_where='(deleted IS FALSE)', unique=True),
        {'schema': 'operation'}
    )

    ID: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(30), nullable=False)
    floor_id: Mapped[int] = mapped_column(Integer, nullable=False, server_default=text('9'))
    deleted: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text('false'))
    version_id: Mapped[int] = mapped_column(Integer, nullable=False, server_default=text('1'))

    floor: Mapped['BuildingFloors'] = relationship('BuildingFloors', back_populates='living_space')
    service_user: Mapped[list['ServiceUser']] = relationship('ServiceUser', back_populates='living_space')


class EmployeePerms(Base):
    __tablename__ = 'employee_perms'
    __table_args__ = (
        ForeignKeyConstraint(['employee_id'], ['personnel.employee.ID'], ondelete='CASCADE', onupdate='CASCADE', name='employee_perms_employee_id_fkey'),
        ForeignKeyConstraint(['perm_id'], ['personnel.permissions.ID'], ondelete='CASCADE', onupdate='CASCADE', name='employee_perms_perm_id_fkey'),
        PrimaryKeyConstraint('ID', name='employee_perms_pkey'),
        {'schema': 'personnel'}
    )

    ID: Mapped[int] = mapped_column(Integer, primary_key=True)
    employee_id: Mapped[int] = mapped_column(Integer, nullable=False)
    perm_id: Mapped[int] = mapped_column(Integer, nullable=False)

    employee: Mapped['Employee'] = relationship('Employee', back_populates='employee_perms')
    perm: Mapped['Permissions'] = relationship('Permissions', back_populates='employee_perms')


class EmployeeRoles(Base):
    __tablename__ = 'employee_roles'
    __table_args__ = (
        ForeignKeyConstraint(['employee_id'], ['personnel.employee.ID'], name='employee_roles_employee_id_fkey'),
        ForeignKeyConstraint(['role_id'], ['personnel.roles.ID'], ondelete='CASCADE', onupdate='CASCADE', name='employee_roles_role_id_fkey'),
        PrimaryKeyConstraint('ID', name='employee_roles_pkey'),
        {'schema': 'personnel'}
    )

    employee_id: Mapped[int] = mapped_column(Integer, nullable=False)
    start_time: Mapped[datetime.datetime] = mapped_column(DateTime(True), nullable=False, server_default=text('now()'))
    expiration_time: Mapped[datetime.datetime] = mapped_column(DateTime(True), nullable=False, server_default=text("(now() + '100 years'::interval)"))
    ID: Mapped[int] = mapped_column(Integer, primary_key=True)
    role_id: Mapped[int] = mapped_column(Integer, nullable=False)

    employee: Mapped['Employee'] = relationship('Employee', back_populates='employee_roles')
    role: Mapped['Roles'] = relationship('Roles', back_populates='employee_roles')


class HandoverMessage(Base):
    __tablename__ = 'handover_message'
    __table_args__ = (
        ForeignKeyConstraint(['creator_id'], ['personnel.employee.ID'], onupdate='CASCADE', name='handover_message_creator_id_fkey'),
        ForeignKeyConstraint(['shift'], ['operation.shifts.name'], onupdate='CASCADE', name='handover_message_shift_fkey'),
        PrimaryKeyConstraint('ID', name='handover_message_pkey'),
        {'schema': 'personnel'}
    )

    ID: Mapped[int] = mapped_column(Integer, primary_key=True)
    timestamp: Mapped[datetime.datetime] = mapped_column(DateTime(True), nullable=False, server_default=text('now()'))
    creator_id: Mapped[int] = mapped_column(Integer, nullable=False, server_default=text('0'))
    shift: Mapped[str] = mapped_column(String(30), nullable=False, server_default=text("'day'::character varying"))

    creator: Mapped['Employee'] = relationship('Employee', back_populates='handover_message')
    shifts: Mapped['Shifts'] = relationship('Shifts', back_populates='handover_message')
    extra_location_message: Mapped[list['ExtraLocationMessage']] = relationship('ExtraLocationMessage', back_populates='parent_message')
    message_location: Mapped[list['MessageLocation']] = relationship('MessageLocation', back_populates='parent_message')
    secondary_message: Mapped[list['SecondaryMessage']] = relationship('SecondaryMessage', back_populates='parent_message')


class ExtraLocationMessage(Base):
    __tablename__ = 'extra_location_message'
    __table_args__ = (
        ForeignKeyConstraint(['parent_message_id'], ['personnel.handover_message.ID'], ondelete='CASCADE', onupdate='CASCADE', name='extra_location_message_parent_message_id_fkey'),
        PrimaryKeyConstraint('ID', name='extra_location_message_pkey'),
        {'schema': 'personnel'}
    )

    ID: Mapped[int] = mapped_column(Integer, primary_key=True)
    parent_message_id: Mapped[int] = mapped_column(Integer, nullable=False)
    location: Mapped[str] = mapped_column(String(200), nullable=False)

    parent_message: Mapped['HandoverMessage'] = relationship('HandoverMessage', back_populates='extra_location_message')


class MessageLocation(Base):
    __tablename__ = 'message_location'
    __table_args__ = (
        ForeignKeyConstraint(['location_name'], ['personnel.possible_locations.name'], onupdate='CASCADE', name='message_location_location_name_fkey'),
        ForeignKeyConstraint(['parent_message_id'], ['personnel.handover_message.ID'], ondelete='CASCADE', onupdate='CASCADE', name='message_location_parent_message_id_fkey'),
        PrimaryKeyConstraint('ID', name='message_location_pkey'),
        {'schema': 'personnel'}
    )

    ID: Mapped[int] = mapped_column(Integer, primary_key=True)
    parent_message_id: Mapped[int] = mapped_column(Integer, nullable=False)
    location_name: Mapped[Optional[str]] = mapped_column(String(30))

    possible_locations: Mapped[Optional['PossibleLocations']] = relationship('PossibleLocations', back_populates='message_location')
    parent_message: Mapped['HandoverMessage'] = relationship('HandoverMessage', back_populates='message_location')


class SecondaryMessage(Base):
    __tablename__ = 'secondary_message'
    __table_args__ = (
        ForeignKeyConstraint(['message_type_id'], ['personnel.secondary_message_types.ID'], ondelete='CASCADE', name='secondary_message_message_type_id_fkey'),
        ForeignKeyConstraint(['parent_message_id'], ['personnel.handover_message.ID'], ondelete='CASCADE', onupdate='CASCADE', name='secondary_message_parent_message_id_fkey'),
        PrimaryKeyConstraint('ID', name='secondary_message_pkey'),
        {'schema': 'personnel'}
    )

    ID: Mapped[int] = mapped_column(Integer, primary_key=True)
    parent_message_id: Mapped[int] = mapped_column(Integer, nullable=False)
    message_type_id: Mapped[int] = mapped_column(Integer, nullable=False)
    message_body: Mapped[Optional[str]] = mapped_column(String(500))

    message_type: Mapped['SecondaryMessageTypes'] = relationship('SecondaryMessageTypes', back_populates='secondary_message')
    parent_message: Mapped['HandoverMessage'] = relationship('HandoverMessage', back_populates='secondary_message')
    secondary_message_employee: Mapped[list['SecondaryMessageEmployee']] = relationship('SecondaryMessageEmployee', back_populates='message')
    secondary_message_service_user: Mapped[list['SecondaryMessageServiceUser']] = relationship('SecondaryMessageServiceUser', back_populates='message')


class ServiceUser(Base):
    __tablename__ = 'service_user'
    __table_args__ = (
        ForeignKeyConstraint(['living_space_id'], ['operation.living_space.ID'], ondelete='SET DEFAULT', onupdate='CASCADE', name='service_user_living_space_id_fkey'),
        PrimaryKeyConstraint('ID', name='service_user_pkey'),
        {'schema': 'personnel'}
    )

    ID: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(30), nullable=False, server_default=text("'請輸入姓名'::character varying"))
    start_date: Mapped[datetime.date] = mapped_column(Date, nullable=False, server_default=text('CURRENT_DATE'))
    active: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text('true'))
    deleted: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text('false'))
    version_id: Mapped[int] = mapped_column(Integer, nullable=False, server_default=text('1'))
    living_space_id: Mapped[Optional[int]] = mapped_column(Integer)

    living_space: Mapped[Optional['LivingSpace']] = relationship('LivingSpace', back_populates='service_user')
    service_user_name_localization: Mapped[list['ServiceUserNameLocalization']] = relationship('ServiceUserNameLocalization', back_populates='service_user')
    group_enrollment: Mapped[list['GroupEnrollment']] = relationship('GroupEnrollment', back_populates='service_user')
    secondary_message_service_user: Mapped[list['SecondaryMessageServiceUser']] = relationship('SecondaryMessageServiceUser', back_populates='service_user')
    service_user_nicknames: Mapped[list['ServiceUserNicknames']] = relationship('ServiceUserNicknames', back_populates='service_user')


class ServiceUserNameLocalization(Base):
    __tablename__ = 'service_user_name_localization'
    __table_args__ = (
        ForeignKeyConstraint(['locale'], ['operation.supported_localization.name'], onupdate='CASCADE', name='service_user_name_localization_locale_fkey'),
        ForeignKeyConstraint(['service_user_id'], ['personnel.service_user.ID'], onupdate='CASCADE', name='service_user_name_localization_service_user_id_fkey'),
        PrimaryKeyConstraint('locale', 'service_user_id', name='service_user_name_localization_pkey'),
        {'schema': 'localization'}
    )

    locale: Mapped[str] = mapped_column(String(30), primary_key=True)
    text_: Mapped[str] = mapped_column('text', String(30), nullable=False)
    service_user_id: Mapped[int] = mapped_column(Integer, primary_key=True)

    supported_localization: Mapped['SupportedLocalization'] = relationship('SupportedLocalization', back_populates='service_user_name_localization')
    service_user: Mapped['ServiceUser'] = relationship('ServiceUser', back_populates='service_user_name_localization')


class GroupEnrollment(Base):
    __tablename__ = 'group_enrollment'
    __table_args__ = (
        ForeignKeyConstraint(['group_id'], ['personnel.service_group.ID'], name='group_enrollment_group_id_fkey'),
        ForeignKeyConstraint(['service_user_id'], ['personnel.service_user.ID'], name='group_enrollment_service_user_id_fkey'),
        PrimaryKeyConstraint('group_id', 'service_user_id', name='group_enrollment_pkey'),
        {'schema': 'personnel'}
    )

    service_user_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    group_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    start_date: Mapped[datetime.date] = mapped_column(Date, nullable=False, server_default=text('CURRENT_DATE'))
    end_date: Mapped[datetime.date] = mapped_column(Date, nullable=False, server_default=text("(CURRENT_DATE + '100 years'::interval)"))

    group: Mapped['ServiceGroup'] = relationship('ServiceGroup', back_populates='group_enrollment')
    service_user: Mapped['ServiceUser'] = relationship('ServiceUser', back_populates='group_enrollment')


class SecondaryMessageEmployee(Base):
    __tablename__ = 'secondary_message_employee'
    __table_args__ = (
        ForeignKeyConstraint(['employee_id'], ['personnel.employee.ID'], ondelete='CASCADE', onupdate='CASCADE', name='secondary_message_employee_employee_id_fkey'),
        ForeignKeyConstraint(['message_id'], ['personnel.secondary_message.ID'], ondelete='CASCADE', onupdate='CASCADE', name='secondary_message_employee_message_id_fkey'),
        PrimaryKeyConstraint('ID', name='secondary_message_employee_pkey'),
        {'schema': 'personnel'}
    )

    ID: Mapped[int] = mapped_column(Integer, primary_key=True)
    message_id: Mapped[int] = mapped_column(Integer, nullable=False)
    employee_id: Mapped[int] = mapped_column(Integer, nullable=False)

    employee: Mapped['Employee'] = relationship('Employee', back_populates='secondary_message_employee')
    message: Mapped['SecondaryMessage'] = relationship('SecondaryMessage', back_populates='secondary_message_employee')


class SecondaryMessageServiceUser(Base):
    __tablename__ = 'secondary_message_service_user'
    __table_args__ = (
        ForeignKeyConstraint(['message_id'], ['personnel.secondary_message.ID'], ondelete='CASCADE', onupdate='CASCADE', name='secondary_message_service_user_message_id_fkey'),
        ForeignKeyConstraint(['service_user_id'], ['personnel.service_user.ID'], ondelete='CASCADE', onupdate='CASCADE', name='secondary_message_service_user_service_user_id_fkey'),
        PrimaryKeyConstraint('ID', name='secondary_message_service_user_pkey'),
        {'schema': 'personnel'}
    )

    ID: Mapped[int] = mapped_column(Integer, primary_key=True)
    message_id: Mapped[int] = mapped_column(Integer, nullable=False)
    service_user_id: Mapped[int] = mapped_column(Integer, nullable=False)

    message: Mapped['SecondaryMessage'] = relationship('SecondaryMessage', back_populates='secondary_message_service_user')
    service_user: Mapped['ServiceUser'] = relationship('ServiceUser', back_populates='secondary_message_service_user')


class ServiceUserNicknames(Base):
    __tablename__ = 'service_user_nicknames'
    __table_args__ = (
        ForeignKeyConstraint(['service_user_id'], ['personnel.service_user.ID'], ondelete='CASCADE', onupdate='CASCADE', name='service_user_nicknames_service_user_id_fkey'),
        PrimaryKeyConstraint('ID', name='service_user_nicknames_pkey'),
        {'schema': 'personnel'}
    )

    ID: Mapped[int] = mapped_column(Integer, primary_key=True)
    service_user_id: Mapped[int] = mapped_column(Integer, nullable=False)
    nickname: Mapped[str] = mapped_column(String(30), nullable=False)

    service_user: Mapped['ServiceUser'] = relationship('ServiceUser', back_populates='service_user_nicknames')
