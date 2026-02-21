import { todoApi } from '../../../frontend/src/api';
import type { Todo, TodoCreate, TodoUpdate } from '../../../frontend/src/types';

describe('frontend_api_todo_methods', () => {
  beforeEach(() => {
    jest.restoreAllMocks();
  });

  function mockFetch(response: any, status = 200) {
    return jest.spyOn(global, 'fetch').mockImplementation(() =>
      Promise.resolve({
        ok: status >= 200 && status < 300,
        status,
        json: () => Promise.resolve(response),
        statusText: typeof response === 'object' && response.error ? response.error : '',
      } as any)
    );
  }

  function mockFetchNoContent(status = 204) {
    return jest.spyOn(global, 'fetch').mockImplementation(() =>
      Promise.resolve({
        ok: status >= 200 && status < 300,
        status,
        json: () => Promise.resolve(undefined),
        statusText: '',
      } as any)
    );
  }

  // Test Case 1: Create todo with minimal valid data
  it('Create todo with minimal valid data', async () => {
    const requestBody = { title: 'Buy groceries' };
    const responseBody = {
      description: null,
      expiry_date: null,
      id: 'generated_id',
      notes: null,
      title: 'Buy groceries',
    };
    mockFetch(responseBody, 201);
    const result = await todoApi.create(requestBody);
    expect(result).toEqual(responseBody);
  });

  // Test Case 2: Create todo with all valid fields
  it('Create todo with all valid fields', async () => {
    const requestBody = {
      description: "Read 'Clean Code'",
      expiry_date: '2024-12-31',
      notes: 'Start this weekend',
      title: 'Read book',
    };
    const responseBody = {
      description: "Read 'Clean Code'",
      expiry_date: '2024-12-31',
      id: 'generated_id',
      notes: 'Start this weekend',
      title: 'Read book',
    };
    mockFetch(responseBody, 201);
    const result = await todoApi.create(requestBody);
    expect(result).toEqual(responseBody);
  });

  // Test Case 3: Create todo with missing title
  it('Create todo with missing title', async () => {
    const requestBody = { description: 'No title provided' };
    mockFetch({ error: 'Title is required' }, 400);
    await expect(todoApi.create(requestBody as any)).rejects.toThrow('Title is required');
  });

  // Test Case 4: Create todo with empty title
  it('Create todo with empty title', async () => {
    const requestBody = { title: '' };
    mockFetch({ error: 'Title cannot be empty' }, 400);
    await expect(todoApi.create(requestBody as any)).rejects.toThrow('Title cannot be empty');
  });

  // Test Case 5: Create todo with invalid expiry_date format
  it("Create todo with invalid expiry_date format", async () => {
    const requestBody = { expiry_date: '31-12-2024', title: 'Test invalid expiry' };
    mockFetch({ error: "expiry_date must be in 'YYYY-MM-DD' format" }, 400);
    await expect(todoApi.create(requestBody as any)).rejects.toThrow("expiry_date must be in 'YYYY-MM-DD' format");
  });

  // Test Case 6: List todos when none exist
  it('List todos when none exist', async () => {
    mockFetch([], 200);
    const result = await todoApi.list();
    expect(result).toEqual([]);
  });

  // Test Case 7: List multiple existing todos
  it('List multiple existing todos', async () => {
    const todos = [
      {
        description: null,
        expiry_date: null,
        id: '1',
        notes: null,
        title: 'Buy groceries',
      },
      {
        description: "Read 'Clean Code'",
        expiry_date: '2024-12-31',
        id: '2',
        notes: 'Start this weekend',
        title: 'Read book',
      },
    ];
    mockFetch(todos, 200);
    const result = await todoApi.list();
    expect(result).toEqual(todos);
  });

  // Test Case 8: Get an existing todo by id
  it('Get an existing todo by id', async () => {
    const todo = {
      description: 'Complete by Friday',
      expiry_date: null,
      id: '5',
      notes: null,
      title: 'Finish project',
    };
    mockFetch(todo, 200);
    const result = await todoApi.get('5');
    expect(result).toEqual(todo);
  });

  // Test Case 9: Get a non-existent todo
  it('Get a non-existent todo', async () => {
    mockFetch({ error: 'Todo not found' }, 404);
    await expect(todoApi.get('999')).rejects.toThrow('Todo not found');
  });

  // Test Case 10: Update a single field of an existing todo
  it('Update a single field of an existing todo', async () => {
    const existingTodo = {
      description: null,
      expiry_date: null,
      id: '7',
      notes: null,
      title: 'Initial title',
    };
    const updateData = { description: 'New description' };
    const updatedTodo = {
      description: 'New description',
      expiry_date: null,
      id: '7',
      notes: null,
      title: 'Initial title',
    };
    mockFetch(updatedTodo, 200);
    const result = await todoApi.update('7', updateData);
    expect(result).toEqual(updatedTodo);
  });

  // Test Case 11: Update all fields of an existing todo
  it('Update all fields of an existing todo', async () => {
    const existingTodo = {
      description: 'Old description',
      expiry_date: null,
      id: '8',
      notes: null,
      title: 'Old title',
    };
    const updateData = {
      description: 'New description',
      expiry_date: '2025-01-01',
      notes: 'Updated notes',
      title: 'New title',
    };
    const updatedTodo = {
      description: 'New description',
      expiry_date: '2025-01-01',
      id: '8',
      notes: 'Updated notes',
      title: 'New title',
    };
    mockFetch(updatedTodo, 200);
    const result = await todoApi.update('8', updateData);
    expect(result).toEqual(updatedTodo);
  });

  // Test Case 12: Update todo with invalid expiry_date format
  it('Update todo with invalid expiry_date format', async () => {
    const existingTodo = {
      description: null,
      expiry_date: null,
      id: '9',
      notes: null,
      title: 'Task',
    };
    const updateData = { expiry_date: '2025/01/01' };
    mockFetch({ error: "expiry_date must be in 'YYYY-MM-DD' format" }, 400);
    await expect(todoApi.update('9', updateData)).rejects.toThrow("expiry_date must be in 'YYYY-MM-DD' format");
  });

  // Test Case 13: Update a non-existent todo
  it('Update a non-existent todo', async () => {
    const updateData = { title: 'Any title' };
    mockFetch({ error: 'Todo not found' }, 404);
    await expect(todoApi.update('999', updateData)).rejects.toThrow('Todo not found');
  });

  // Test Case 14: Delete an existing todo
  it('Delete an existing todo', async () => {
    const existingTodo = {
      description: null,
      expiry_date: null,
      id: '10',
      notes: null,
      title: 'To be deleted',
    };
    mockFetchNoContent(204);
    const deleteResult = await todoApi.delete('10');
    expect(deleteResult).toBeUndefined();

    mockFetch({ error: 'Todo not found' }, 404);
    await expect(todoApi.get('10')).rejects.toThrow('Todo not found');
  });

  // Test Case 15: Delete a non-existent todo
  it('Delete a non-existent todo', async () => {
    mockFetch({ error: 'Todo not found' }, 404);
    await expect(todoApi.delete('888')).rejects.toThrow('Todo not found');
  });

  // Test Case 16: Create todo with notes set to null
  it('Create todo with notes set to null', async () => {
    const requestBody = { notes: null, title: 'Null notes' };
    const responseBody = {
      description: null,
      expiry_date: null,
      id: 'generated_id',
      notes: null,
      title: 'Null notes',
    };
    mockFetch(responseBody, 201);
    const result = await todoApi.create(requestBody);
    expect(result).toEqual(responseBody);
  });

  // Test Case 17: Update todo to remove description
  it('Update todo to remove description', async () => {
    const existingTodo = {
      description: 'To be cleared',
      expiry_date: null,
      id: '12',
      notes: null,
      title: 'Task',
    };
    const updateData = { description: null };
    const updatedTodo = {
      description: null,
      expiry_date: null,
      id: '12',
      notes: null,
      title: 'Task',
    };
    mockFetch(updatedTodo, 200);
    const result = await todoApi.update('12', updateData);
    expect(result).toEqual(updatedTodo);
  });

  // Test Case 18: Create todo with expiry_date as empty string
  it('Create todo with expiry_date as empty string', async () => {
    const requestBody = { expiry_date: '', title: 'Expiry test' };
    mockFetch({ error: "expiry_date must be in 'YYYY-MM-DD' format" }, 400);
    await expect(todoApi.create(requestBody as any)).rejects.toThrow("expiry_date must be in 'YYYY-MM-DD' format");
  });
});