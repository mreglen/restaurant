from pydantic import BaseModel
from typing import Optional

class RoleCreate(BaseModel):
    name: str
    description: Optional[str] = None

class RoleRead(RoleCreate):
    id: int

    class Config:
        from_attributes = True