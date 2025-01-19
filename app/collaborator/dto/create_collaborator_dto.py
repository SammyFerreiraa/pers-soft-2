from pydantic import BaseModel

class CreateCollaboratorDTO(BaseModel):
    name: str
    email: str