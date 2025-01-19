from pydantic import BaseModel
from typing import List
from ..project_entity import ProjectStatus
from datetime import datetime, date
from ...task.dto.task_dto import TaskRead

class ProjectRead(BaseModel):
    id: int
    name: str
    description: str | None
    created_date: datetime
    updated_date: datetime
    start_date: date | None
    end_date: date | None
    forecast_completion: date | None
    status: ProjectStatus

class ProjectReadWithTasks(BaseModel):
    id: int
    name: str
    description: str | None
    created_date: datetime
    updated_date: datetime
    start_date: date | None
    end_date: date | None
    forecast_completion: date | None
    status: ProjectStatus
    tasks: List[TaskRead]