from pydantic import BaseModel
from typing import Optional

class ProductCategorySchema(BaseModel):
    id: int
    name: str
    description: Optional[str]

    model_config = dict(from_attributes=True)

class HPEProductBase(BaseModel):
    name: str
    description: Optional[str]
    business_value: Optional[str]
    product_url: Optional[str]

class HPEProductCreate(HPEProductBase):
    category_id: int

class HPEProductUpdate(BaseModel):
    name: Optional[str]
    description: Optional[str]
    business_value: Optional[str]
    product_url: Optional[str]
    category_id: Optional[int]

class HPEProductRead(HPEProductBase):
    id: int
    category: ProductCategorySchema

    model_config = dict(from_attributes=True)