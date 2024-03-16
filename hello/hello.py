# Import the required libraries
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from fastapi import FastAPI
import streamlit as st

# Create the SQLAlchemy engine
engine = create_engine("neon+database://username:password@localhost:5432/db_name")
Base = declarative_base()
Session = sessionmaker(bind=engine)
session = Session()

# Define the Todo model
class Todo(Base):
    __tablename__ = "todos"

    id = Column(Integer, primary_key=True)
    title = Column(String(100), nullable=False)
    description = Column(String(500), nullable=True)

# Create the FastAPI app
app = FastAPI()

# Define the API endpoints
@app.post("/todos")
def create_todo(todo: Todo):
    session.add(todo)
    session.commit()
    return {"message": "Todo created successfully"}

@app.get("/todos")
def get_todos():
    todos = session.query(Todo).all()
    return {"todos": todos}

# Create the Streamlit UI
def main():
    st.title("Todo App")

    # Add UI components here

if __name__ == "__main__":
    main()
import unittest


class TestTodoApp(unittest.TestCase):
    def setUp(self):
        # Set up test data or initialize resources
        self.app = app.test_client()
        self.todo = {
            "title": "Test Todo",
            "description": "This is a test todo"
        }

    def tearDown(self):
        # Clean up resources
        pass

    def test_create_todo(self):
        response = self.app.post("/todos", json=self.todo)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json["message"], "Todo created successfully")

    def test_get_todos(self):
        response = self.app.get("/todos")
        self.assertEqual(response.status_code, 200)
        todos = response.json["todos"]
        self.assertIsInstance(todos, list)
        self.assertGreater(len(todos), 0)
        self.assertIsInstance(todos[0]["id"], int)
        self.assertIsInstance(todos[0]["title"], str)
        self.assertIsInstance(todos[0]["description"], str)


if __name__ == "__main__":
    unittest.main()
