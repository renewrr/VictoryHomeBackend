from pydantic import BaseModel, ConfigDict, computed_field, Field, WithJsonSchema
from datetime import datetime, date
from typing import Optional, TYPE_CHECKING, Literal, TypedDict, List
from enum import Enum
from apiflask import Schema, fields

if TYPE_CHECKING:
    import app.models.model_views as models


class EmployeeData(BaseModel):
    ID: int
    name: str
    date_of_employment: datetime
    company_email: str
    localization: str
    deleted: bool

    model_config = ConfigDict(from_attributes=True)


class EmployeeBasicData(BaseModel):
    ID: int
    name: str

    model_config = ConfigDict(from_attributes=True)


class ServiceUserBasicData(BaseModel):
    ID: int
    name: str

    model_config = ConfigDict(from_attributes=True)


class MessageLocationData(BaseModel):
    ID: int
    location_name: str

    model_config = ConfigDict(from_attributes=True)


class LoginWithoutTotpInput(BaseModel):
    account: str
    password: str

    model_config = ConfigDict(from_attributes=True)


class LoginWithTotpInput(BaseModel):
    account: str
    password: str
    totp: str

    model_config = ConfigDict(from_attributes=True)


class TotpStepUpRequest(BaseModel):
    totp: str
    model_config = ConfigDict(from_attributes=True)


class LoginResponse(BaseModel):
    status: bool
    authenticated: bool
    management_privilege: bool
    is_2fa_verified: bool

    model_config = ConfigDict(from_attributes=True)


class LogoutResponse(BaseModel):
    status: bool

    model_config = ConfigDict(from_attributes=True)


class RoomDetails(BaseModel):
    ID: int
    name: str
    service_user: list[ServiceUserBasicData]

    model_config = ConfigDict(from_attributes=True)


class FloorDetails(BaseModel):
    ID: int
    floor_name: str
    living_space: list[RoomDetails]

    model_config = ConfigDict(from_attributes=True)


class BuildingDetails(BaseModel):
    ID: int
    name: str
    address: str
    building_floors: list[FloorDetails]

    model_config = ConfigDict(from_attributes=True)


class BuildingResponse(BaseModel):
    data_rows: list[BuildingDetails]

    model_config = ConfigDict(from_attributes=True)


class WhoAmIResponse(BaseModel):
    user_id: int
    authenticated: bool
    management_privilege: bool
    is_2fa_verified: bool

    model_config = ConfigDict(from_attributes=True)


class MainHandoverMessageRow(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    ID: int
    timestamp: datetime
    shift_id: int
    shift_name: str
    creator_id: int
    creator_name: str
    location_ids: list[int]
    location_names: list[str]
    message_type_ids: list[int]
    message_type_names: list[str]


class SecondaryHandoverMessageRow(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    ID: int
    timestamp: datetime
    shift_id: int
    shift_name: str
    creator_id: int
    creator_name: str
    location_ids: list[int]
    location_names: list[str]
    message_type_id: int
    message_type_name: str
    message_body: str


class ServiceUserNickName(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    ID: int
    service_user_id: int
    nickname: str


class MainHandoverMessageResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    data_rows: list[MainHandoverMessageRow]


class MainPagedHandoverMessageResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    data_rows: list[MainHandoverMessageRow]
    data_count: int


class SecondaryHandoverMessageResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    data_rows: list[SecondaryHandoverMessageRow]
    data_count: int


class BuildingData(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    ID: int
    name: str


class FloorData(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    ID: int
    floor_name: str
    building: BuildingData


class LivingSpaceData(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    ID: int
    name: str
    floor: FloorData


class ServiceUserData(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    ID: int
    name: str
    start_date: date
    living_space: LivingSpaceData | None
    service_user_nicknames: list[ServiceUserNickName]
    active: bool
    deleted: bool


class ForcedLogoutRequest(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    user_id: int


class ForcedLogoutResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    statuts: bool


class FloorsMessageResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    data_rows: list[FloorData]


class FilterQuery(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    filter_option: Literal["FLOORS", "SHIFTS", "EMPLOYEE", "SERVICEUSER", "MESSAGETYPE"]


class FilterData(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    ID: int
    name: str


class FilterMessageResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    data_rows: list[FilterData]


class NicknamesResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    data_rows: list[ServiceUserNickName]


class MessageQuery(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    handover_message_id: int


class SingleHandoverMessage(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    secondary_messages: list[SecondaryHandoverMessageRow]


class HandoverMessageQueryFilter(Schema):
    start_date = fields.DateTime()
    end_date = fields.DateTime()
    message_type_ids = fields.List(fields.Integer(), load_default=list)
    shift_ids = fields.List(fields.Integer(), load_default=list)
    creator_ids = fields.List(fields.Integer(), load_default=list)

    location_ids = fields.List(fields.Integer(), load_default=list)
    service_user_ids = fields.List(fields.Integer(), load_default=list)

    keywords = fields.List(fields.String(), load_default=list)

    page_index = fields.Integer()
    page_size = fields.Integer()


class HandoverMessageFilter(TypedDict, total=False):
    start_date: datetime
    end_date: datetime
    message_type_ids: List[int]
    shift_ids: List[int]
    creator_ids: List[int]

    location_ids: List[int]  # GIN
    service_user_ids: List[int]  # GIN
    keywords: List[str]

    page_index: int
    page_size: int


class GenericSelectObject(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    ID: int
    name: str


class SecondaryInput(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    message_body: str
    message_type: GenericSelectObject


class NewMessageInput(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    creator: GenericSelectObject
    datetime: datetime
    shift: GenericSelectObject
    locations: list[GenericSelectObject]
    secondary_data: list[SecondaryInput]


class StaleReferenceError(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    error: str
    message: str
    extra_data: dict[str, str]


class ManagementServiceUserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    data_rows: list[ServiceUserData]


class ManagementLivingSpaceResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    data_rows: list[LivingSpaceData]


class ManagementServiceUserEditRequest(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    before: ServiceUserData
    after: ServiceUserData


class ManagementServiceUserEditResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    updated: ServiceUserData


class ServiceUserInputData(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    name: str
    living_space_id: int | None
    nicknames: list[str]


class ServiceUserInput(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    data_rows: list[ServiceUserInputData]


class ManagementServiceUserEditInput(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    updated: ServiceUserData


class Auth(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    account: str
    password: str
    ID: int
    totp_secret: str | None = None


class EmployeeDetails(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    ID: int
    name: str
    date_of_employment: datetime
    company_email: str
    localization: str
    deleted: bool
    auth: Auth | None = None


class PasswordChangeRequest(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    old_password: str
    new_password: str
    confirm_password: str


class PasswordChangeResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    status: bool


class ManagementEmployeeResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    data_rows: list[EmployeeDetails]


class ManagementEmployeeEditRequest(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    before: EmployeeDetails
    after: EmployeeDetails


class ManagementEmployeeEditResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    updated: EmployeeDetails


class Localization(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    name: str


class ManagementEmployeeDetails(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class ManagementLocalizationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    data_rows: list[Localization]


class NewEmployeeRequest(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    name: str
    email: str
    account: str
    password: str
    use_two_factor: bool


class NewBuildingRequest(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    name: str
    address: str


class BuildingModifyResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    status: bool
    message: str


class NewFloorRequest(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    name: str
    building_id: int


class FloorModifyResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    status: bool
    message: str


class NewRoomRequest(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    name: str
    floor_id: int


class RoomModifyResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    status: bool
    message: str


class BuildingDeleteRequest(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    building_id: int


class FloorDeleteRequest(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    floor_id: int


class RoomDeleteRequest(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    room_id: int

class SecondaryMessageDetail(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    ID: int
    message_body: str
    delete: bool

class SecondaryEditRequest(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    before: SecondaryMessageDetail
    after: SecondaryMessageDetail

