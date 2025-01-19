from pydantic import BaseModel
from ..task_entity import TaskStatusEnum
from datetime import date

class UpdateTaskDTO(BaseModel):
    name: str = None
    description: str = None
    delivery_forecast: date = None
    start_date: date = None
    end_date: date = None
    status: TaskStatusEnum = None
    collaborators: list[int] = []