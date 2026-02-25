from pydantic import BaseModel, Field, EmailStr
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
    first_name: Optional[str]
    last_name: Optional[str]

class UserCreate(UserBase):
    password: str
    region_id: int

class AdminUserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    password: Optional[str] = Field(default=None, min_length=8, max_length=72)
    role_id: Optional[int] = None
    region_id: Optional[int] = None

class SelfUserUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    password: Optional[str] = Field(default=None, min_length=8, max_length=72)

class UserRead(UserBase):
    id: int
    role: UserRoleSchema
    region: RegionSchema

    model_config = dict(from_attributes=True)