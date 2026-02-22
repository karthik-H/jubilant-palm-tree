import { todoApi } from '../../../frontend/src/api';

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

  // Test Case 1: List all todos - positive
  it('List all todos - positive', async () => {
    const todos = [
      {
        description: 'Milk, eggs, bread',
        expiry_date: '2024-07-01',
        id: 'auto-generated-id-1',
        notes: null,
        title: 'Buy groceries',
      },
      {
        description: null,
        expiry_date: null,
        id: 'auto-generated-id-2',
        notes: 'Start with chapter 1',
        title: 'Read book',
      },
    ];
    mockFetch(todos, 200);
    const result = await todoApi.list();
    expect(result).toEqual(todos);
  });

  // Test Case 2: Get todo by valid ID
  it('Get todo by valid ID', async () => {
    const todo = {
      description: 'Math homework',
      expiry_date: '2024-12-31',
      id: 'abc123',
      notes: 'Due Monday',
      title: 'Finish assignment',
    };
    mockFetch(todo, 200);
    const result = await todoApi.get('abc123');
    expect(result).toEqual(todo);
  });

  // Test Case 3: Get todo by invalid/nonexistent ID
  it('Get todo by invalid/nonexistent ID', async () => {
    mockFetch({ error: 'Todo not found' }, 404);
    await expect(todoApi.get('zzzz')).rejects.toThrow('Todo not found');
  });

  // Test Case 4: Create todo with only required field
  it('Create todo with only required field', async () => {
    const requestBody = { title: 'Walk dog' };
    const persisted = {
      description: null,
      expiry_date: null,
      id: 'auto-generated-id',
      notes: null,
      title: 'Walk dog',
    };
    mockFetch(persisted, 201);
    const result = await todoApi.create(requestBody);
    expect(result).toEqual(persisted);
  });

  // Test Case 5: Create todo with all fields
  it('Create todo with all fields', async () => {
    const requestBody = {
      title: 'Plan trip',
      description: 'Book flights',
      notes: 'Check passport',
      expiry_date: '2025-01-15',
    };
    const persisted = {
      description: 'Book flights',
      expiry_date: '2025-01-15',
      id: 'auto-generated-id',
      notes: 'Check passport',
      title: 'Plan trip',
    };
    mockFetch(persisted, 201);
    const result = await todoApi.create(requestBody);
    expect(result).toEqual(persisted);
  });

  // Test Case 6: Create todo missing required title
  it('Create todo missing required title', async () => {
    const requestBody = { description: 'No title' };
    mockFetch({ error: 'Title is required' }, 400);
    await expect(todoApi.create(requestBody)).rejects.toThrow('Title is required');
  });

  // Test Case 7: Create todo with empty title
  it('Create todo with empty title', async () => {
    const requestBody = { title: '', description: 'No title' };
    mockFetch({ error: 'Title is required' }, 400);
    await expect(todoApi.create(requestBody)).rejects.toThrow('Title is required');
  });

  // Test Case 8: Create todo with invalid expiry_date format
  it("Create todo with invalid expiry_date format", async () => {
    const requestBody = { title: "Renew license", expiry_date: "2024/07/01" };
    mockFetch({ error: "expiry_date must be in 'YYYY-MM-DD' format" }, 400);
    await expect(todoApi.create(requestBody)).rejects.toThrow("expiry_date must be in 'YYYY-MM-DD' format");
  });

  // Test Case 9: Create todo with null optional fields
  it('Create todo with null optional fields', async () => {
    const requestBody = {
      title: 'Test nulls',
      description: null,
      notes: null,
      expiry_date: null,
    };
    const persisted = {
      description: null,
      expiry_date: null,
      id: 'auto-generated-id',
      notes: null,
      title: 'Test nulls',
    };
    mockFetch(persisted, 201);
    const result = await todoApi.create(requestBody);
    expect(result).toEqual(persisted);
  });

  // Test Case 10: Update todo with some fields
  it('Update todo with some fields', async () => {
    const update = {
      description: 'Updated desc',
      expiry_date: '2025-06-01',
    };
    const updated = {
      description: 'Updated desc',
      expiry_date: '2025-06-01',
      id: 'xyz1',
      notes: 'Note',
      title: 'Old',
    };
    mockFetch(updated, 200);
    const result = await todoApi.update('xyz1', update);
    expect(result).toEqual(updated);
  });

  // Test Case 11: Update todo title only
  it('Update todo title only', async () => {
    const update = { title: 'New Title' };
    const updated = {
      description: 'Desc',
      expiry_date: '2025-01-01',
      id: 'xyz2',
      notes: null,
      title: 'New Title',
    };
    mockFetch(updated, 200);
    const result = await todoApi.update('xyz2', update);
    expect(result).toEqual(updated);
  });

  // Test Case 12: Update todo with invalid expiry_date
  it('Update todo with invalid expiry_date', async () => {
    const update = { expiry_date: '01-01-2025' };
    mockFetch({ error: "expiry_date must be in 'YYYY-MM-DD' format" }, 400);
    await expect(todoApi.update('xyz3', update)).rejects.toThrow("expiry_date must be in 'YYYY-MM-DD' format");
  });

  // Test Case 13: Update todo with nonexistent ID
  it('Update todo with nonexistent ID', async () => {
    const update = { title: 'Should fail' };
    mockFetch({ error: 'Todo not found' }, 404);
    await expect(todoApi.update('no-such-id', update)).rejects.toThrow('Todo not found');
  });

  // Test Case 14: Delete existing todo
  it('Delete existing todo', async () => {
    mockFetchNoContent(204);
    const result = await todoApi.delete('del1');
    expect(result).toBeUndefined();
  });

  // Test Case 15: Delete todo with nonexistent ID
  it('Delete todo with nonexistent ID', async () => {
    mockFetch({ error: 'Todo not found' }, 404);
    await expect(todoApi.delete('notfound')).rejects.toThrow('Todo not found');
  });

  // Test Case 16: List after deletion
  it('List after deletion', async () => {
    const todos = [
      {
        description: null,
        expiry_date: null,
        id: 'other-existing-id',
        notes: null,
        title: 'Other item',
      },
    ];
    mockFetch(todos, 200);
    const result = await todoApi.list();
    expect(result).toEqual(todos);
  });

  // Test Case 17: Get after deletion
  it('Get after deletion', async () => {
    mockFetch({ error: 'Todo not found' }, 404);
    await expect(todoApi.get('del2')).rejects.toThrow('Todo not found');
  });

  // Test Case 18: Create todo with long title
  it('Create todo with long title', async () => {
    const longTitle = 'T'.repeat(255);
    const requestBody = { title: longTitle };
    const persisted = {
      description: null,
      expiry_date: null,
      id: 'auto-generated-id',
      notes: null,
      title: longTitle,
    };
    mockFetch(persisted, 201);
    const result = await todoApi.create(requestBody);
    expect(result).toEqual(persisted);
  });

  // Test Case 19: Update all optional fields to null
  it('Update all optional fields to null', async () => {
    const update = {
      description: null,
      notes: null,
      expiry_date: null,
    };
    const updated = {
      description: null,
      expiry_date: null,
      id: 'nulltest',
      notes: null,
      title: 'Some title',
    };
    mockFetch(updated, 200);
    const result = await todoApi.update('nulltest', update);
    expect(result).toEqual(updated);
  });
});