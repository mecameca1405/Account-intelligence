from pydantic import BaseModel, EmailStr


class MeResponse(BaseModel):
    email: EmailStr
    first_name: str
    last_name: str
    role: str
    region: str