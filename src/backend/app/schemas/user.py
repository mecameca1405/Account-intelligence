from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional

# ------------------------------
# Roles y Regiones
# ------------------------------
class UserRoleSchema(BaseModel):
    id: int
    name: str
    description: Optional[str]

    model_config = dict(from_attributes=True)

class RegionSchema(BaseModel):
    id: int
    code: str
    name: str

    model_config = dict(from_attributes=True)

# ------------------------------
# Users
# ------------------------------
class UserBase(BaseModel):
    email: str
    full_name: Optional[str]

class UserCreate(UserBase):
    password: str
    role_id: int
    region_id: int

class UserUpdate(BaseModel):
    full_name: Optional[str]
    role_id: Optional[int]
    region_id: Optional[int]

class UserRead(UserBase):
    id: int
    role: UserRoleSchema
    region: RegionSchema

    model_config = dict(from_attributes=True)