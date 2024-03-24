# main.py
from contextlib import asynccontextmanager
from typing import Union, Optional, Annotated
from api import settings
from sqlmodel import Field, Session, SQLModel, create_engine, select
from fastapi import FastAPI, Depends


class Todo(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    content: str = Field(index=True)


# only needed for psycopg 3 - replace postgresql
# with postgresql+psycopg in settings.DATABASE_URL
connection_string = str(settings.DATABASE_URL).replace(
    "postgresql", "postgresql+psycopg"
)


# recycle connections after 5 minutes
# to correspond with the compute scale down
engine = create_engine(
    connection_string, connect_args={"sslmode": "require"}, pool_recycle=300
)


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)


# The first part of the function, before the yield, will
# be executed before the application starts.
# https://fastapi.tiangolo.com/advanced/events/#lifespan-function
@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Creating tables..")
    create_db_and_tables()
    yield


app = FastAPI(lifespan=lifespan, title="Hello World API with DB", 
    version="0.0.1",
    servers=[
        {
            "url": "http://localhost:8000", # ADD NGROK URL Here Before Creating GPT Action
            "description": "Development Server"
        }
        ])

def get_session():
    with Session(engine) as session:
        yield session


@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.post("/todos/create_todo", response_model=Todo)
def create_todo(todo: Todo, session: Annotated[Session, Depends(get_session)]):
        session.add(todo)
        session.commit()
        session.refresh(todo)
        return todo


@app.get("/todos/get_all", response_model=list[Todo])
def read_todos(session: Annotated[Session, Depends(get_session)]):
        todos = session.exec(select(Todo)).all()
        return todos
    

@app.put("/todos/update/{id}", response_model=Todo)
def update_todo(id: int, todo: Todo, session: Annotated[Session, Depends(get_session)]):
    statment = select(Todo).where(Todo.id == id)
    updated_todo = session.exec(statment).one()
    updated_todo.content = todo.content
    session.add(updated_todo)
    session.commit()
    session.refresh(updated_todo)
    return updated_todo
    

@app.delete("/todos/delete/{id}")
def delete_todo(id: int, session: Annotated[Session, Depends(get_session)]):
    statment = select(Todo).where(Todo.id == id)
    todo = session.exec(statment).one()
    session.delete(todo)
    session.commit()
    return {"message": "item deleted"}