from fastapi import FastAPI, HTTPException, status, Query, Request, status
from typing import List
from fastapi.responses import JSONResponse
from models.note import Note, NoteCreate, NoteNotFound

app = FastAPI()

notes_raw = [
    {"id": 1, "tags": ["work", "code"], "title": "My Work", "description": "This is my work"},
    {"id": 2, "tags": ["work", "self"], "title": "shopping", "description": "going for shopping"},
    {"id": 3, "tags": ["self"], "title": "learn", "description": "learning skills"},
    {"id": 4, "tags": ["room"], "title": "Cleaning", "description": "learning fastapi"},
    {"id": 5, "tags": ["FastAPI", "code"], "title": "FastAPI", "description": "fastapi learning"},
]

notes: dict[int, Note] = {
    item["id"]: Note.model_validate(item)
    for item in notes_raw
}

@app.exception_handler(NoteNotFound)
async def note_not_found_handler(request: Request, exc: NoteNotFound):
    return JSONResponse(status_code=status.HTTP_404_NOT_FOUND, content={"message": f"Note with id {exc.note_id} not found."})
    

@app.get("/")
def home():
    return {
        "message": "chill bruh this is workin fr."
    }


@app.get("/notes", response_model=List[Note])
def get_notes(search: str = "", skip: int = Query(0, ge=0), limit: int = Query(10, ge=1), tags: List[str] = Query([]), sort_by: str = "id"):
    list_notes = []
    
    for note in notes.values():
        
        actual_search = search.lower()
        
        passes_search =  (actual_search in note.title.lower() or actual_search in (note.description or "").lower())
        
        passes_tags = (not tags) or any(tag in note.tags for tag in tags)
        
        if passes_search and passes_tags:
            list_notes.append(note)
    
    if sort_by in Note.model_fields:
        sorted_notes = sorted(list_notes, key=lambda note: getattr(note, sort_by))    
        return sorted_notes[skip: skip+limit]
    
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Sort by Attribute {sort_by} is not defined."
        )
        
# a get note endpoint in which we can search , and also the skip and limit part which are greater than equal to 0 and also limit is 10 by default .... also a list of tags and also the sort_by property 



@app.get("/notes/{note_id}")
def get_note(note_id: int):
    existing_note = notes.get(note_id)
    
    if existing_note is None:
        raise NoteNotFound(note_id)
    
    return existing_note

@app.post("/notes", response_model=Note)
def create_note(note: NoteCreate):
    new_id = max(notes.keys()) + 1
    new_note = Note(
        id=new_id,
        title=note.title,
        description=note.description,
        tags=note.tags,
    )
    notes[new_id] = new_note
    return new_note


