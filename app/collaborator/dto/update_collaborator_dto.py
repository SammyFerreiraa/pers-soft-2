from pydantic import BaseModel

class UpdateCollaboratorDTO(BaseModel):
    name: str = None
    email: str = None