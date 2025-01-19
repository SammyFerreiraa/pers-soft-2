from sqlmodel import SQLModel, Field, Relationship
from typing import TYPE_CHECKING
from typing import Optional
from datetime import datetime

if TYPE_CHECKING:
    from app.task.task_entity import Task

class Assignments(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    task_id: int = Field(foreign_key="task.id")
    collaborator_id: int = Field(foreign_key="collaborator.id")
    assignments_data: datetime = Field(default_factory=datetime.utcnow, nullable=False)

class CollaboratorBase(SQLModel):
    id: int = Field(default=None, primary_key=True)
    name: str
    email: str

class Collaborator(CollaboratorBase, table=True):
    tasks: list["Task"] = Relationship(back_populates="collaborators", link_model=Assignments)
