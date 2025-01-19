from sqlmodel import SQLModel, Field, Relationship
from ..task.task_entity import Task
from datetime import datetime, timezone, date
from enum import Enum

class ProjectStatus(str, Enum):
    ONGOING = "ongoing"
    COMPLETED = "completed"
    PENDING = "pending"
    CANCELLED = "cancelled"


class ProjectBase(SQLModel):
    id: int = Field(default=None, primary_key=True)
    name: str
    description: str | None
    start_date: date | None
    end_date: date | None
    forecast_completion: date | None
    status: ProjectStatus = Field(default=ProjectStatus.PENDING, sa_column_kwargs={"nullable": False})

    created_date: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    updated_date: datetime = Field(default_factory=datetime.utcnow, nullable=False, sa_column_kwargs={"onupdate": datetime.utcnow})

class Project(ProjectBase, table=True):
  tasks: list['Task'] = Relationship(back_populates="project")