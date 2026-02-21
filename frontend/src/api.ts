import type { Todo, TodoCreate, TodoUpdate } from './types';

const BASE = '/api';

async function request<T>(
  path: string,
  options?: RequestInit & { body?: unknown }
): Promise<T> {
  const { body, ...init } = options ?? {};
  const res = await fetch(`${BASE}${path}`, {
    ...init,
    headers: {
      'Content-Type': 'application/json',
      ...init.headers,
    },
    body: body !== undefined ? JSON.stringify(body) : init.body,
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(Array.isArray(err.detail) ? err.detail[0]?.msg ?? res.statusText : err.detail ?? res.statusText);
  }
  if (res.status === 204) return undefined as T;
  return res.json();
}

export const todoApi = {
  list: () => request<Todo[]>('/todos'),
  get: (id: number) => request<Todo>(`/todos/${id}`),
  create: (data: TodoCreate) => request<Todo>('/todos', { method: 'POST', body: data }),
  update: (id: number, data: TodoUpdate) => request<Todo>(`/todos/${id}`, { method: 'PUT', body: data }),
  delete: (id: number) => request<void>(`/todos/${id}`, { method: 'DELETE' }),
};
