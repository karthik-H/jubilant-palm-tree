import { useState, useEffect } from 'react';
import { todoApi } from './api';
import type { Todo, TodoCreate, TodoUpdate } from './types';
import './App.css';

function formatDate(s: string | null): string {
  if (!s) return '—';
  try {
    return new Date(s).toLocaleDateString(undefined, {
      dateStyle: 'medium',
    });
  } catch {
    return s;
  }
}

function isExpired(s: string | null): boolean {
  if (!s) return false;
  try {
    return new Date(s) < new Date();
  } catch {
    return false;
  }
}

export default function App() {
  const [todos, setTodos] = useState<Todo[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [editing, setEditing] = useState<Todo | null>(null);
  const [creating, setCreating] = useState(false);

  const load = async () => {
    setLoading(true);
    setError(null);
    try {
      const list = await todoApi.list();
      setTodos(list);
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Failed to load todos');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    load();
  }, []);

  const handleCreate = async (data: TodoCreate) => {
    await todoApi.create(data);
    setCreating(false);
    load();
  };

  const handleUpdate = async (id: number, data: TodoUpdate) => {
    await todoApi.update(id, data);
    setEditing(null);
    load();
  };

  const handleDelete = async (id: number) => {
    if (!confirm('Delete this todo?')) return;
    await todoApi.delete(id);
    setEditing(null);
    load();
  };

  if (loading) return <div className="loading">Loading…</div>;
  if (error) return <div className="error">Error: {error}</div>;

  return (
    <>
      <h1>Todo Manager</h1>
      <button className="btn-primary" onClick={() => setCreating(true)}>
        New todo
      </button>

      {todos.length === 0 ? (
        <div className="empty-state">
          <p>No todos yet. Create one to get started.</p>
          <button className="btn-primary" onClick={() => setCreating(true)}>
            Add todo
          </button>
        </div>
      ) : (
        <ul className="todo-list">
          {todos.map((t) => (
            <li
              key={t.id}
              className={`todo-card ${isExpired(t.expiry_date) ? 'expired' : ''}`}
            >
              <h3>{t.title}</h3>
              <div className="meta">
                Expires: {formatDate(t.expiry_date)}
              </div>
              {t.description && (
                <div className="description">{t.description}</div>
              )}
              <div className="actions">
                <button
                  className="btn-ghost"
                  onClick={() => setEditing(t)}
                >
                  Edit
                </button>
                <button
                  className="btn-danger"
                  onClick={() => handleDelete(t.id)}
                >
                  Delete
                </button>
              </div>
            </li>
          ))}
        </ul>
      )}

      {creating && (
        <TodoForm
          title="New todo"
          initial={{ title: '', description: '', notes: '', expiry_date: null }}
          onSave={handleCreate}
          onCancel={() => setCreating(false)}
        />
      )}
      {editing && (
        <TodoForm
          title="Edit todo"
          initial={{
            title: editing.title,
            description: editing.description,
            notes: editing.notes,
            expiry_date: editing.expiry_date,
          }}
          onSave={(data) => handleUpdate(editing.id, data)}
          onCancel={() => setEditing(null)}
        />
      )}
    </>
  );
}

interface TodoFormProps {
  title: string;
  initial: {
    title: string;
    description: string;
    notes: string;
    expiry_date: string | null;
  };
  onSave: (data: TodoCreate | TodoUpdate) => void;
  onCancel: () => void;
}

function TodoForm({ title, initial, onSave, onCancel }: TodoFormProps) {
  const [titleVal, setTitleVal] = useState(initial.title);
  const [description, setDescription] = useState(initial.description);
  const [notes, setNotes] = useState(initial.notes);
  const [expiryDate, setExpiryDate] = useState(
    initial.expiry_date?.slice(0, 10) ?? ''
  );
  const [saving, setSaving] = useState(false);
  const [err, setErr] = useState<string | null>(null);

  const submit = async (e: React.FormEvent) => {
    e.preventDefault();
    setErr(null);
    if (!titleVal.trim()) {
      setErr('Title is required');
      return;
    }
    setSaving(true);
    try {
      await onSave({
        title: titleVal.trim(),
        description: description.trim() || undefined,
        notes: notes.trim() || undefined,
        expiry_date: expiryDate ? expiryDate : null,
      });
    } catch (e) {
      setErr(e instanceof Error ? e.message : 'Failed to save');
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="modal-overlay" onClick={onCancel}>
      <div className="modal" onClick={(e) => e.stopPropagation()}>
        <h2>{title}</h2>
        <form onSubmit={submit}>
          <div className="form-group">
            <label>Title *</label>
            <input
              value={titleVal}
              onChange={(e) => setTitleVal(e.target.value)}
              placeholder="Todo title"
              autoFocus
            />
          </div>
          <div className="form-group">
            <label>Description</label>
            <textarea
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              placeholder="Optional description"
            />
          </div>
          <div className="form-group">
            <label>Notes</label>
            <textarea
              value={notes}
              onChange={(e) => setNotes(e.target.value)}
              placeholder="Optional notes"
            />
          </div>
          <div className="form-group">
            <label>Expiry date</label>
            <input
              type="date"
              value={expiryDate}
              onChange={(e) => setExpiryDate(e.target.value)}
            />
          </div>
          {err && <div className="error">{err}</div>}
          <div className="modal-actions">
            <button type="button" className="btn-ghost" onClick={onCancel}>
              Cancel
            </button>
            <button type="submit" className="btn-primary" disabled={saving}>
              {saving ? 'Saving…' : 'Save'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
