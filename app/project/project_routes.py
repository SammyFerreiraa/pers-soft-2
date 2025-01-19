from fastapi import APIRouter, Depends, HTTPException
from app.database import get_session
from sqlmodel import select, Session
from sqlalchemy.orm import joinedload
from .project_entity import Project
from .dto.create_project_dto import CreateProjectDTO
from .dto.project_dto import ProjectRead, ProjectReadWithTasks
from .dto.update_project_dto import UpdateProjectDTO
from ..task.task_entity import Task

router = APIRouter(
    prefix="/projects",
    tags=["Projects"],
)

@router.get("", response_model=list[ProjectRead], summary="Buscar todos os projetos.", status_code=200)
def read_projects(offset: int = 0, limit: int = 10, order_by: str = "id", session: Session = Depends(get_session)):
    valid_order_fields = {
        "id": Project.id,
        "name": Project.name,
        "created_date": Project.created_date
    }
    if order_by not in valid_order_fields:
        raise HTTPException(status_code=400, detail=f"Invalid order field. Valid options are: {', '.join(valid_order_fields.keys())}")

    statement = select(Project).order_by(valid_order_fields[order_by]).offset(offset).limit(limit)
    projects = session.exec(statement).all()
    return projects
    valid_order_fields = {"id": Project.id, "name": Project.name, "created_date": Project.created_date}
    if order_by not in valid_order_fields:
        raise HTTPException(status_code=400, detail="Invalid order field")
    
    statement = select(Project).order_by(valid_order_fields[order_by]).offset(offset).limit(limit)
    projects = session.exec(statement).all()
    return projects

@router.get("/{project_id}", response_model=ProjectRead, summary="Buscar um projeto.", status_code=200)
def read_project(project_id: int, session: Session = Depends(get_session)):
    project = session.exec(select(Project).where(Project.id == project_id)).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project
    
@router.post("", response_model=Project, status_code=201, summary="Criar um novo projeto.")
def create_project(project_dto: CreateProjectDTO, session: Session = Depends(get_session)):
    project = Project(**project_dto.dict())

    session.add(project)
    session.commit()
    session.refresh(project)
    return project

@router.delete("/{project_id}", status_code=204, summary="Deletar um projeto.")
def delete_project(project_id: int, session: Session = Depends(get_session)):
    project = session.get(Project, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    session.delete(project)
    session.commit()
    return {"message": "Project deleted successfully"}

@router.put("/{project_id}", response_model=Project, summary="Atualiza um projeto.", status_code=200)
def update_project(
    project_id: int, updated_project: UpdateProjectDTO, session: Session = Depends(get_session)
):
    project = session.get(Project, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    for key, value in updated_project.dict(exclude_unset=True).items():
        setattr(project, key, value)
    
    session.add(project)
    session.commit()
    session.refresh(project)
    return project

@router.get("/{project_id}/task_count", response_model=int, summary="Retorna a quantidade de tarefas de um projeto.", status_code=200)
def get_task_count(project_id: int, session: Session = Depends(get_session)):
    project = session.get(Project, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    task_count = len(project.task)
    return task_count

@router.get("/search/{search}", response_model=list[ProjectRead], summary="Buscar projetos por nome.", status_code=200)
def search_project(search: str, session: Session = Depends(get_session)):
    statement = select(Project).where(Project.name.ilike(f"%{search}%"))
    projects = session.exec(statement).all()
    return projects

@router.get("/{project_id}/full", response_model=ProjectReadWithTasks, summary="Buscar um projeto com suas tarefas e colaboradores.", status_code=200)
def read_project_full(project_id: int, session: Session = Depends(get_session)):
    statement = select(Project).where(Project.id == project_id).options(
        joinedload(Project.tasks).joinedload(Task.collaborators)
    )

    project = session.exec(statement).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project
