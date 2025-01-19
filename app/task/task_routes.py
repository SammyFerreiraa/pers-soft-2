from ..collaborator.collaborator_entity import Assignments, Collaborator
from fastapi import APIRouter, Depends, HTTPException
from app.database import get_session
from sqlmodel import select, Session
from .dto.task_dto import TaskRead
from .task_entity import Task
from .dto.create_task_dto import CreateTaskDTO
from .dto.update_task_dto import UpdateTaskDTO
from ..project.project_entity import Project

router = APIRouter(
    prefix="/tasks",
    tags=["Tasks"],
)

@router.get("", response_model=list[TaskRead], status_code=200, summary="Buscar todas as tarefas.")
def read_tasks(offset: int = 0, limit: int = 10, session: Session = Depends(get_session)):
    """
    Recupera uma lista de tarefas.

    - **offset**: Número de registros a serem pulados.
    - **limit**: Número de registros a serem retornados.

    Retorna uma lista de tarefas.
    """
    statement = select(Task).offset(offset).limit(limit)
    tasks = session.exec(statement).all()
    return tasks

@router.post("", response_model=Task, status_code=201, summary="Criar uma nova tarefa.")
def create_task(
    task_data: CreateTaskDTO,
    session: Session = Depends(get_session)
):
    """
    Cria uma nova tarefa.

    - **task_data**: Dados da tarefa a ser criados.

    Retorna a tarefa criada.
    """
    project = session.exec(select(Project).where(Project.id == task_data.project_id)).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    task = Task(
        name=task_data.name,
        description=task_data.description,
        delivery_forecast=task_data.delivery_forecast,
        start_date=task_data.start_date,
        end_date=task_data.end_date,
        status=task_data.status or TaskStatusEnum.PENDING,
        project_id=task_data.project_id
    )

    session.add(task)
    session.commit()
    session.refresh(task)

    if task_data.collaborators:
        collaborators = session.exec(select(Collaborator).where(Collaborator.id.in_(task_data.collaborators))).all()
        if len(collaborators) != len(task_data.collaborators):
            raise HTTPException(status_code=404, detail="One or more collaborators not found")
        
        assignments = [
            Assignments(task_id=task.id, collaborator_id=collaborator.id)
            for collaborator in collaborators
        ]
        session.add_all(assignments)
        session.commit()

    return task

@router.get("/{task_id}", response_model=TaskRead, status_code=200, summary="Buscar uma tarefa.")
def read_task(task_id: int, session: Session = Depends(get_session)):
    """
    Recupera uma tarefa específico pelo ID.

    - **task_id**: O ID da tarefa a ser recuperado.

    Retorna a tarefa correspondente ao ID fornecido.
    """
    task = session.exec(select(Task).where(Task.id == task_id)).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task

@router.put("/{task_id}", response_model=TaskRead, status_code=200, summary="Atualizar uma tarefa.")
def update_task(
    task_id: int,
    task_data: UpdateTaskDTO,
    session: Session = Depends(get_session)
):
    """
    Atualiza as informações de uma tarefa existente.

    - **task_id**: O ID da tarefa a ser atualizado.
    - **task_data**: Dados a serem atualizados na tarefa.

    Retorna a tarefa atualizada.
    """
    task = session.get(Task, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    for key, value in task_data.model_dump(exclude_unset=True).items():
        if key == "collaborators":
            if value:
                collaborators = session.exec(select(Collaborator).where(Collaborator.id.in_(value))).all()
                if len(collaborators) != len(value):
                    raise HTTPException(status_code=404, detail="One or more collaborators not found")
                task.collaborators = collaborators
            else:
                task.collaborators = []
        else:
            setattr(task, key, value)
    session.add(task)
    session.commit()
    session.refresh(task)
    return task

@router.delete("/{task_id}", status_code=204, summary="Deletar uma tarefa.")
def delete_task(task_id: int, session: Session = Depends(get_session)):
    """
    Deleta uma tarefa específico pelo ID.

    - **task_id**: O ID da tarefa a ser deletado.

    Retorna uma mensagem de sucesso após a exclusão.
    """
    task = session.get(Task, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    session.delete(task)
    session.commit()
    return {"message": "Task deleted successfully"} 

@router.get("/{task_id}/collaborators", response_model=list[Collaborator], status_code=200, summary="Buscar colaboradores de uma tarefa.")
def read_task_collaborators(task_id: int, session: Session = Depends(get_session)):
    """
    Busca os colaboradores de uma tarefa específica pelo ID.

    - **task_id**: O ID da tarefa a ser buscada.

    Retorna uma lista de colaboradores associados à tarefa.
    """
    task = session.get(Task, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task.collaborators
