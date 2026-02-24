from pydantic import BaseModel
from typing import Optional

class CompanyBase(BaseModel):
    name: str
    domain: Optional[str]
    industry: Optional[str]
    description: Optional[str]
    logo_url: Optional[str]
    location: Optional[str]
    is_simulated: Optional[bool] = False

class CompanyCreate(CompanyBase):
    pass

class CompanyUpdate(BaseModel):
    name: Optional[str]
    domain: Optional[str]
    industry: Optional[str]
    description: Optional[str]
    logo_url: Optional[str]
    location: Optional[str]
    is_simulated: Optional[bool]

class CompanyRead(CompanyBase):
    id: int

    model_config = dict(from_attributes=True)