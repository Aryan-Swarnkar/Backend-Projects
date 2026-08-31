from pydantic import BaseModel, Field
from datetime import date, datetime, time, timedelta
from typing import Optional

class Todo(BaseModel):
    id: int
    title: str = Field(..., min_length=3, max_length=20)
    description: Optional[str] = None
    completed: bool = False
    started_at: Optional[time] = None
    completed_at: Optional[time] = None
    
class TodoCreate(BaseModel):
    title: str = Field(..., min_length=3, max_length=20)
    description: Optional[str] = None
    completed: bool = False
    started_at: Optional[time] = None
    completed_at: Optional[time] = None
        