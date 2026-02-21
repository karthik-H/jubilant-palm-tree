from datetime import date

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from database import db_cursor, init_db
from models import Todo, TodoCreate, TodoUpdate

app = FastAPI(title="Todo Manager API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def startup():
    init_db()


def row_to_todo(row) -> Todo:
    return Todo(
        id=row["id"],
        title=row["title"],
        description=row["description"] or "",
        notes=row["notes"] or "",
        expiry_date=date.fromisoformat(row["expiry_date"]) if row["expiry_date"] else None,
    )


@app.get("/todos", response_model=list[Todo])
def list_todos():
    with db_cursor() as cur:
        cur.execute(
            "SELECT id, title, description, notes, expiry_date FROM todos ORDER BY id"
        )
        return [row_to_todo(dict(r)) for r in cur.fetchall()]


@app.get("/todos/{todo_id}", response_model=Todo)
def get_todo(todo_id: int):
    with db_cursor() as cur:
        cur.execute(
            "SELECT id, title, description, notes, expiry_date FROM todos WHERE id = ?",
            (todo_id,),
        )
        row = cur.fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Todo not found")
        return row_to_todo(dict(row))


@app.post("/todos", response_model=Todo, status_code=201)
def create_todo(todo: TodoCreate):
    with db_cursor() as cur:
        cur.execute(
            """
            INSERT INTO todos (title, description, notes, expiry_date)
            VALUES (?, ?, ?, ?)
            """,
            (
                todo.title,
                todo.description,
                todo.notes,
                todo.expiry_date.isoformat() if todo.expiry_date else None,
            ),
        )
        row_id = cur.lastrowid
    return get_todo(row_id)


@app.put("/todos/{todo_id}", response_model=Todo)
def update_todo(todo_id: int, payload: TodoUpdate):
    with db_cursor() as cur:
        cur.execute("SELECT id FROM todos WHERE id = ?", (todo_id,))
        if not cur.fetchone():
            raise HTTPException(status_code=404, detail="Todo not found")

        updates = []
        args = []
        if payload.title is not None:
            updates.append("title = ?")
            args.append(payload.title)
        if payload.description is not None:
            updates.append("description = ?")
            args.append(payload.description)
        if payload.notes is not None:
            updates.append("notes = ?")
            args.append(payload.notes)
        if payload.expiry_date is not None:
            updates.append("expiry_date = ?")
            args.append(payload.expiry_date.isoformat())

        if not updates:
            return get_todo(todo_id)

        args.append(todo_id)
        cur.execute(
            f"UPDATE todos SET {', '.join(updates)} WHERE id = ?",
            args,
        )
    return get_todo(todo_id)


@app.delete("/todos/{todo_id}", status_code=204)
def delete_todo(todo_id: int):
    with db_cursor() as cur:
        cur.execute("DELETE FROM todos WHERE id = ?", (todo_id,))
        if cur.rowcount == 0:
            raise HTTPException(status_code=404, detail="Todo not found")
    return None
