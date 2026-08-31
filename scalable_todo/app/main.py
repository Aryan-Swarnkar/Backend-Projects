from fastapi import FastAPI, HTTPException, status
from app.models.todo import Todo, TodoCreate
from typing import List
app = FastAPI()

todos_list = [
    {"id": 1, "title": "work", "completed": False},
    {"id": 2, "title": "cleaning", "completed": False},
    {"id": 3, "title": "workout", "completed": False},
    {"id": 4, "title": "golang", "completed": True},
    {"id": 5, "title": "fastapi", "completed": True},
]

# todos_list: List[Todo] = [Todo.model_validate(item) for item in todos]

todos: dict[int, Todo] = {
    item["id"]: Todo.model_validate(item)
    for item in todos_list
}

@app.get("/hello")
def say_hello():
    return {"message": "hi"}

@app.get("/todos", response_model=List[Todo])
def show(
    completed: bool | None = None,
    title: str | None = None,
):
    result = list(todos.values())

    if completed is not None:
        result = [
            todo
            for todo in result
            if todo.completed == completed
        ]

    if title is not None:
        result = [
            todo
            for todo in result
            if todo.title == title
        ]

    return result

@app.post("/todos", response_model=Todo)
def create(todo: TodoCreate):
    new_id = max(todos.keys(), default=0) + 1
    
    new_todo = Todo(
        id=new_id,
        title=todo.title,
        completed=todo.completed,
        description=todo.description,
        started_at=todo.started_at,
        completed_at=todo.completed_at,
    )
    
    todos[new_id] = new_todo
    
    return new_todo

@app.get("/todos/{todo_id}", response_model=Todo)
def get_todo(todo_id: int):
    todo = todos.get(todo_id)
    
    if todo is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Todo item with id {todo_id} not found."
        )
    
    return todo


@app.put("/todos/{todos_id}", response_model=Todo)
def update_todo(todos_id: int, todo: Todo):
    existing = todos.get(todos_id)
    
    if existing is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Todo item with {todos_id} not found."
        )
    
    updated = Todo(id=todos_id, **todo.model_dump(exclude={"id"}))
    
    todos[todos_id] = updated
    
    return updated

@app.delete("/todos/{todos_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_todo(todos_id: int):
    
    existing = todos.get(todos_id)
    
    if existing is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Todo item with {todos_id} not found."
        )
    
    del todos[todos_id]
