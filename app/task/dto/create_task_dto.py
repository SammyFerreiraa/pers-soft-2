from pydantic import BaseModel
from ..task_entity import TaskStatusEnum
from typing import List
from datetime import date

class CreateTaskDTO(BaseModel):
    project_id: int
    name: str
    description: str = None
    delivery_forecast: date = None
    start_date: date = None
    end_date: date = None
    status: TaskStatusEnum = None
    collaborators: List[int] = []