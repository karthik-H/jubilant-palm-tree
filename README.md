# Todo Manager

A full-stack todo app: **Python** (FastAPI) backend, **TypeScript** (React + Vite) frontend, **SQLite** database. Each todo has title, description, notes, and an optional expiry date. Full CRUD is supported.

## Features

- **Todo fields**: title, description, notes, expiry date
- **CRUD**: Create, list, get one, update, delete
- **Backend**: FastAPI, SQLite, CORS enabled for local frontend
- **Frontend**: React 18 + TypeScript, Vite, dark UI

## Quick start

### 1. Backend (Python)

```bash
cd backend
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

API: http://127.0.0.1:8000  
Docs: http://127.0.0.1:8000/docs  

### 2. Frontend (TypeScript)

In another terminal:

```bash
cd frontend
npm install
npm run dev
```

App: http://localhost:5173  

The frontend proxies `/api` to the backend, so both must be running.

### 3. Use the app

Open http://localhost:5173, add todos (title required; description, notes, expiry optional), edit or delete as needed. Expired todos are shown with a red left border.

## Project layout

```
backend/
  main.py       # FastAPI app, CRUD routes
  database.py   # SQLite connection and init
  models.py     # Pydantic request/response models
  requirements.txt
  todos.db      # created on first run

frontend/
  src/
    App.tsx     # List + form modal UI
    api.ts      # HTTP client for /api/todos
    types.ts    # Todo types
  index.html
  package.json
  vite.config.ts  # proxy /api -> backend
```

## API

| Method | Path         | Description        |
|--------|--------------|--------------------|
| GET    | /todos       | List all todos     |
| GET    | /todos/{id}  | Get one todo       |
| POST   | /todos       | Create todo        |
| PUT    | /todos/{id}  | Update todo        |
| DELETE | /todos/{id}  | Delete todo        |

Request body for create/update (all fields optional except title for create):

```json
{
  "title": "string",
  "description": "string",
  "notes": "string",
  "expiry_date": "YYYY-MM-DD"
}
```
