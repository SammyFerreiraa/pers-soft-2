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
    """
    Recupera uma lista de projetos.

    - **offset**: Número de registros a serem pulados.
    - **limit**: Número de registros a serem retornados.
    - **order_by**: Campo pelo qual os projetos serão ordenados. Opções válidas: 'id', 'name', 'created_date'.

    Retorna uma lista de projetos.
    """
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
    """
    Recupera um projeto específico pelo ID.

    - **project_id**: O ID do projeto a ser recuperado.

    Retorna o projeto correspondente ao ID fornecido.
    """
    project = session.exec(select(Project).where(Project.id == project_id)).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project
    
@router.post("", response_model=Project, status_code=201, summary="Criar um novo projeto.")
def create_project(project_dto: CreateProjectDTO, session: Session = Depends(get_session)):
    """
    Cria um novo projeto.

    - **project_dto**: Dados do projeto a serem criados.

    Retorna o projeto recém-criado.
    """
    project = Project(**project_dto.model_dump())

    session.add(project)
    session.commit()
    session.refresh(project)
    return project

@router.delete("/{project_id}", status_code=204, summary="Deletar um projeto.")
def delete_project(project_id: int, session: Session = Depends(get_session)):
    """
    Deleta um projeto.

    - **project_id**: O ID do projeto a ser deletado.

    Retorna uma mensagem de sucesso após a exclusão.
    """
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
    """
    Atualiza as informações de um projeto existente.

    - **project_id**: O ID do projeto a ser atualizado.
    - **updated_project**: Dados a serem atualizados no projeto.

    Retorna o projeto atualizado.
    """
    project = session.get(Project, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    for key, value in updated_project.model_dump(exclude_unset=True).items():
        setattr(project, key, value)
    
    session.add(project)
    session.commit()
    session.refresh(project)
    return project

@router.get("/{project_id}/task_count", response_model=int, summary="Retorna a quantidade de tarefas de um projeto.", status_code=200)
def get_task_count(project_id: int, session: Session = Depends(get_session)):
    """
    Recupera o número total de tarefas associadas a um projeto.

    - **project_id**: O ID do projeto para o qual a contagem de tarefas será feita.

    Retorna o número de tarefas associadas ao projeto.
    """
    project = session.get(Project, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    task_count = len(project.task)
    return task_count

@router.get("/search/{search}", response_model=list[ProjectRead], summary="Buscar projetos por nome.", status_code=200)
def search_project(search: str, session: Session = Depends(get_session)):
    """
    Busca projetos pelo nome.

    - **search**: O nome (ou parte dele) para buscar projetos.

    Retorna uma lista de projetos que correspondem ao nome informado.
    """
    statement = select(Project).where(Project.name.ilike(f"%{search}%"))
    projects = session.exec(statement).all()
    return projects

@router.get("/{project_id}/full", response_model=ProjectReadWithTasks, summary="Buscar um projeto com suas tarefas e colaboradores.", status_code=200)
def read_project_full(project_id: int, session: Session = Depends(get_session)):
    """
    Recupera um projeto específico com suas tarefas e colaboradores.

    - **project_id**: O ID do projeto a ser recuperado.

    Retorna um projeto com as suas tarefas e colaboradores associados.
    """
    statement = select(Project).where(Project.id == project_id).options(
        joinedload(Project.tasks).joinedload(Task.collaborators)
    )

    project = session.exec(statement).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project
