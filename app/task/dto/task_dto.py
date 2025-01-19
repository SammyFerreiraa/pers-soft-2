from typing import List
from pydantic import BaseModel
from ...collaborator.dto.collaborator_dto import CollaboratorRead
from ..task_entity import TaskStatusEnum
from datetime import date

class TaskRead(BaseModel):
    id: int
    name: str
    project_id: int
    description: str
    delivery_forecast: date | None
    start_date: date | None
    end_date: date | None
    status: TaskStatusEnum 
    collaborators: List[CollaboratorRead]