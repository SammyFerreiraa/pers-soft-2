from pydantic import BaseModel

class CollaboratorRead(BaseModel):
    id: int
    name: str
    email: str