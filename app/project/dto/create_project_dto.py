from pydantic import BaseModel
from ..project_entity import ProjectStatus
from datetime import date
from typing import List

class CreateProjectDTO(BaseModel):
    name: str
    description: str = None
    start_date: date = None
    end_date: date = None
    forecast_completion: date = None
    status: ProjectStatus = ProjectStatus.PENDING