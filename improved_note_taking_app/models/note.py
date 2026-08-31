from pydantic import BaseModel
from typing import Optional, List

class Note(BaseModel):
    id: int
    tags: List[str] = []
    title: str
    description: Optional[str] = None
    
class NoteCreate(BaseModel):
    tags: List[str] = []
    title: str
    description: Optional[str] = None
    
class NoteNotFound(Exception):
    def __init__(self, note_id):
        self.note_id = note_id
        super().__init__(f"Note with id {note_id} not found.")