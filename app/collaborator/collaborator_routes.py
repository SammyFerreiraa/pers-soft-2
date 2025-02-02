from fastapi import APIRouter, Depends, HTTPException
from app.database import get_session
from sqlmodel import select, Session
from .collaborator_entity import Collaborator, Assignments
from .dto.collaborator_dto import CollaboratorRead
from .dto.create_collaborator_dto import CreateCollaboratorDTO
from .dto.update_collaborator_dto import UpdateCollaboratorDTO
from app.task.task_entity import Task
from datetime import date

router = APIRouter(
    prefix="/collaborators",
    tags=["Collaborator"],
)

@router.get("", response_model=list[CollaboratorRead], summary="Buscar todos os colaboradores.", status_code=200)
def read_collaborators(offset: int = 0, limit: int = 10, session: Session = Depends(get_session)):
    """
    Recupera lista de colaboradores.

    - **offset**: Número de registros a serem pulados.
    - **limit**: Número de registros a serem retornados.

    Retorna uma lista de colaboradores.
    """
    statement = select(Collaborator).offset(offset).limit(limit)
    collaborators = session.exec(statement).all()
    return collaborators


@router.get("/{collaborator_id}", response_model=CollaboratorRead, summary="Buscar colaborador por id.", status_code=200)
def read_collaborator(collaborator_id: int, session: Session = Depends(get_session)):
    """
    Recupera um colaborador específico pelo ID.

    - **collaborator_id**: O ID do colaborador a ser recuperado.

    Retorna as informações do colaborador se encontrado, caso contrário, retorna um erro 404.
    """
    collaborator = session.exec(select(Collaborator).where(Collaborator.id == collaborator_id)).first()
    if not collaborator:
        raise HTTPException(status_code=404, detail="Collaborator not found")
    return collaborator

@router.post("", response_model=CollaboratorRead, summary="Criar colaborador.", status_code=201)
def create_collaborator(collaborator_dto: CreateCollaboratorDTO, session: Session = Depends(get_session)):
    """
    Cria um novo colaborador.

    - **collaborator_dto**: Dados do colaborador a serem criados.

    Retorna o colaborador criado.
    """
    try:
        collaborator = Collaborator.from_orm(collaborator_dto)
        session.add(collaborator)
        session.commit()
        session.refresh(collaborator)
        return collaborator
    except Exception as e:
        session.rollback()
        raise HTTPException(status_code=400, detail=str(e))

@router.put("/{collaborator_id}", response_model=CollaboratorRead, summary="Atualizar colaborador.", status_code=200)
def update_collaborator(
    collaborator_id: int, updated_collaborator: UpdateCollaboratorDTO, session: Session = Depends(get_session)
):
    """
    Atualiza as informações de um colaborador existente.

    - **collaborator_id**: ID do colaborador a ser atualizado.
    - **updated_collaborator**: Dados a serem atualizados no colaborador.

    Retorna o colaborador atualizado.
    """
    collaborator = session.get(Collaborator, collaborator_id)
    if not collaborator:
        raise HTTPException(status_code=404, detail="Collaborator not found")
    for key, value in updated_collaborator.model_dump(exclude_unset=True).items():
        setattr(collaborator, key, value)
    session.add(collaborator)
    session.commit()
    session.refresh(collaborator)
    return collaborator

@router.delete("/{collaborator_id}", summary="Deletar colaborador.", status_code=204)
def delete_collaborator(collaborator_id: int, session: Session = Depends(get_session)):
    """
    Deleta um colaborador.

    - **collaborator_id**: ID do colaborador a ser deletado.

    Retorna uma mensagem de sucesso após a exclusão.
    """
    collaborator = session.get(Collaborator, collaborator_id)
    if not collaborator:
        raise HTTPException(status_code=404, detail="Collaborator not found")
    session.delete(collaborator)
    session.commit()
    return {"message": "Collaborator deleted successfully"}

@router.get("/{collaborator_id}/tasks", response_model=list[Task], summary="Buscar tarefas de um colaborador.")
def read_collaborator_tasks(collaborator_id: int, session: Session = Depends(get_session)):
    """
    Recupera todas as tarefas de um colaborador específico.

    - **collaborator_id**: ID do colaborador cujas tarefas serão recuperadas.

    Retorna uma lista de tarefas associadas ao colaborador.
    """
    collaborator = session.get(Collaborator, collaborator_id)
    if not collaborator:
        raise HTTPException(status_code=404, detail="Collaborator not found")
    return collaborator.tasks

@router.get("/{collaborator_id}/tasks/{date}", response_model=list[Task], summary="Buscar tarefas de um colaborador por data.")
def read_collaborator_tasks_by_date(
    collaborator_id: int, date: date, session: Session = Depends(get_session)
):
    """
    Recupera todas as tarefas de um colaborador para uma data específica.

    - **collaborator_id**: ID do colaborador cujas tarefas serão recuperadas.
    - **date**: A data para a qual as tarefas serão recuperadas.

    Retorna uma lista de tarefas associadas ao colaborador para a data informada.
    """
    collaborator = session.get(Collaborator, collaborator_id)
    if not collaborator:
        raise HTTPException(status_code=404, detail="Collaborator not found")
    return (
        session.query(Task)
        .join(Assignments)
        .join(Collaborator)
        .filter(
            Collaborator.id == collaborator_id,
            Task.start_date <= date,
            Task.end_date >= date,
        )
        .all()
    )
