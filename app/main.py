from fastapi import FastAPI
from app.database import create_db_and_tables
from app.project.project_routes import router as project_routes
from app.collaborator.collaborator_routes import router as collaborator_routes
from app.task.task_routes import router as task_routes

app = FastAPI()

@app.on_event("startup")
def on_startup():
    create_db_and_tables()

app.include_router(collaborator_routes)
app.include_router(project_routes)
app.include_router(task_routes)

