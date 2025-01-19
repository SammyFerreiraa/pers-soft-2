from sqlmodel import SQLModel, Field, Relationship
from typing import TYPE_CHECKING
from ..collaborator.collaborator_entity import Collaborator
from ..collaborator.collaborator_entity import Assignments
from datetime import date
from enum import Enum
if TYPE_CHECKING:
    from ..project.project_entity import Project

class TaskStatusEnum(str, Enum):
    PENDING = "PENDING"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"

class TaskBase(SQLModel):
    id: int = Field(default=None, primary_key=True)
    name: str
    description: str
    delivery_forecast: date | None
    start_date: date | None
    end_date: date | None
    status: TaskStatusEnum = Field(default=TaskStatusEnum.PENDING, sa_column_kwargs={"nullable": False})

class Task(TaskBase, table=True):
    project_id: int = Field(foreign_key="project.id")
    project: 'Project' = Relationship(back_populates="tasks")
    collaborators: list["Collaborator"] = Relationship(back_populates="tasks", link_model=Assignments)
