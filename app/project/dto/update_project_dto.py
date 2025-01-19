from pydantic import BaseModel
from ..project_entity import ProjectStatus
from datetime import date

class UpdateProjectDTO(BaseModel):
    name: str = None
    description: str = None
    start_date: date = None
    end_date: date = None
    forecast_completion: date = None
    status: ProjectStatus = None