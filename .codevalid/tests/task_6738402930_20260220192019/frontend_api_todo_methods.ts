import { todoApi } from '../../../frontend/src/api';
import type { Todo, TodoCreate, TodoUpdate } from '../../../frontend/src/types';

describe('frontend_api_todo_methods', () => {
  beforeEach(() => {
    jest.restoreAllMocks();
  });

  // Helper to mock fetch
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

  // Helper to mock fetch for 204 No Content
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

  // Test Case 1: Create Todo with All Fields Valid
  it('Create Todo with All Fields Valid', async () => {
    const requestBody: TodoCreate = {
      title: 'Buy groceries',
      description: 'Milk, eggs, bread',
      notes: 'Buy organic if possible',
      expiry_date: '2024-12-31',
    };
    const persisted: Todo = {
      id: 1,
      title: 'Buy groceries',
      description: 'Milk, eggs, bread',
      notes: 'Buy organic if possible',
      expiry_date: '2024-12-31',
    };
    mockFetch(persisted, 201);
    const result = await todoApi.create(requestBody);
    expect(result).toEqual(persisted);
  });

  // Test Case 2: Create Todo with Missing Title
  it('Create Todo with Missing Title', async () => {
    const requestBody = {
      description: 'No title here',
      notes: 'Should fail',
    };
    mockFetch({ error: 'Title is required' }, 400);
    await expect(todoApi.create(requestBody as any)).rejects.toThrow('Title is required');
  });

  // Test Case 3: Create Todo with Empty Title
  it('Create Todo with Empty Title', async () => {
    const requestBody = {
      title: '',
      description: 'Empty title',
      notes: 'Should fail',
    };
    mockFetch({ error: 'Title cannot be empty' }, 400);
    await expect(todoApi.create(requestBody as any)).rejects.toThrow('Title cannot be empty');
  });

  // Test Case 4: Create Todo with Only Title
  it('Create Todo with Only Title', async () => {
    const requestBody: TodoCreate = { title: 'Write report' };
    const persisted: Todo = {
      id: 2,
      title: 'Write report',
      description: null as any,
      notes: null as any,
      expiry_date: null,
    };
    mockFetch(persisted, 201);
    const result = await todoApi.create(requestBody);
    expect(result).toEqual(persisted);
  });

  // Test Case 5: Create Todo with Invalid Expiry Date Format
  it('Create Todo with Invalid Expiry Date Format', async () => {
    const requestBody = {
      title: 'Call mom',
      expiry_date: '12-31-2024',
    };
    mockFetch({ error: "expiry_date must be in 'YYYY-MM-DD' format" }, 400);
    await expect(todoApi.create(requestBody as any)).rejects.toThrow("expiry_date must be in 'YYYY-MM-DD' format");
  });

  // Test Case 6: List Todos with Multiple Items
  it('List Todos with Multiple Items', async () => {
    const todos: Todo[] = [
      {
        id: 1,
        title: 'Buy groceries',
        description: 'Milk, eggs, bread',
        notes: 'Buy organic if possible',
        expiry_date: '2024-12-31',
      },
      {
        id: 2,
        title: 'Write report',
        description: null as any,
        notes: null as any,
        expiry_date: null,
      },
    ];
    mockFetch(todos, 200);
    const result = await todoApi.list();
    expect(result).toEqual(todos);
  });

  // Test Case 7: List Todos When None Exist
  it('List Todos When None Exist', async () => {
    mockFetch([], 200);
    const result = await todoApi.list();
    expect(result).toEqual([]);
  });

  // Test Case 8: Get Todo with Valid ID
  it('Get Todo with Valid ID', async () => {
    const todo: Todo = {
      id: 1,
      title: 'Buy groceries',
      description: 'Milk, eggs, bread',
      notes: 'Buy organic if possible',
      expiry_date: '2024-12-31',
    };
    mockFetch(todo, 200);
    const result = await todoApi.get(1);
    expect(result).toEqual(todo);
  });

  // Test Case 9: Get Todo with Nonexistent ID
  it('Get Todo with Nonexistent ID', async () => {
    mockFetch({ error: 'Todo not found' }, 404);
    await expect(todoApi.get(999)).rejects.toThrow('Todo not found');
  });

  // Test Case 10: Update Todo with Some Fields
  it('Update Todo with Some Fields', async () => {
    const update: TodoUpdate = {
      description: 'Milk, eggs, bread, cheese',
      notes: 'Add cheese',
    };
    const updated: Todo = {
      id: 1,
      title: 'Buy groceries',
      description: 'Milk, eggs, bread, cheese',
      notes: 'Add cheese',
      expiry_date: '2024-12-31',
    };
    mockFetch(updated, 200);
    const result = await todoApi.update(1, update);
    expect(result).toEqual(updated);
  });

  // Test Case 11: Update Todo with All Fields
  it('Update Todo with All Fields', async () => {
    const update: TodoUpdate = {
      title: 'Write final report',
      description: 'Include summary',
      notes: 'Deadline tomorrow',
      expiry_date: '2024-07-01',
    };
    const updated: Todo = {
      id: 2,
      title: 'Write final report',
      description: 'Include summary',
      notes: 'Deadline tomorrow',
      expiry_date: '2024-07-01',
    };
    mockFetch(updated, 200);
    const result = await todoApi.update(2, update);
    expect(result).toEqual(updated);
  });

  // Test Case 12: Update Todo with Invalid Expiry Date
  it('Update Todo with Invalid Expiry Date', async () => {
    const update: TodoUpdate = {
      expiry_date: '01/07/2024',
    };
    mockFetch({ error: "expiry_date must be in 'YYYY-MM-DD' format" }, 400);
    await expect(todoApi.update(1, update)).rejects.toThrow("expiry_date must be in 'YYYY-MM-DD' format");
  });

  // Test Case 13: Update Todo with Nonexistent ID
  it('Update Todo with Nonexistent ID', async () => {
    const update: TodoUpdate = {
      title: 'Should not work',
    };
    mockFetch({ error: 'Todo not found' }, 404);
    await expect(todoApi.update(999, update)).rejects.toThrow('Todo not found');
  });

  // Test Case 14: Delete Todo with Valid ID
  it('Delete Todo with Valid ID', async () => {
    mockFetchNoContent(204);
    const result = await todoApi.delete(2);
    expect(result).toBeUndefined();

    // Postcondition: get returns 404, list does not include deleted todo
    mockFetch({ error: 'Todo not found' }, 404);
    await expect(todoApi.get(2)).rejects.toThrow('Todo not found');

    const todos: Todo[] = [
      {
        id: 1,
        title: 'Buy groceries',
        description: 'Milk, eggs, bread',
        notes: 'Buy organic if possible',
        expiry_date: '2024-12-31',
      },
    ];
    mockFetch(todos, 200);
    const listResult = await todoApi.list();
    expect(listResult.find(t => t.id === 2)).toBeUndefined();
  });

  // Test Case 15: Delete Todo with Nonexistent ID
  it('Delete Todo with Nonexistent ID', async () => {
    mockFetch({ error: 'Todo not found' }, 404);
    await expect(todoApi.delete(999)).rejects.toThrow('Todo not found');
  });

  // Test Case 16: Create Todo with Leap Year Expiry Date
  it('Create Todo with Leap Year Expiry Date', async () => {
    const requestBody: TodoCreate = {
      title: 'Leap Day Task',
      expiry_date: '2024-02-29',
    };
    const persisted: Todo = {
      id: 3,
      title: 'Leap Day Task',
      description: null as any,
      notes: null as any,
      expiry_date: '2024-02-29',
    };
    mockFetch(persisted, 201);
    const result = await todoApi.create(requestBody);
    expect(result).toEqual(persisted);
  });

  // Test Case 17: Create Todo with Invalid Leap Day Expiry Date
  it('Create Todo with Invalid Leap Day Expiry Date', async () => {
    const requestBody: TodoCreate = {
      title: 'Invalid Leap Day',
      expiry_date: '2023-02-29',
    };
    mockFetch({ error: 'expiry_date is not a valid calendar date' }, 400);
    await expect(todoApi.create(requestBody)).rejects.toThrow('expiry_date is not a valid calendar date');
  });

  // Test Case 18: Create Todo with Boundary Title Length (255 chars)
  it('Create Todo with Boundary Title Length (255 chars)', async () => {
    const longTitle = 'T'.repeat(255);
    const requestBody: TodoCreate = { title: longTitle };
    const persisted: Todo = {
      id: 4,
      title: longTitle,
      description: null as any,
      notes: null as any,
      expiry_date: null,
    };
    mockFetch(persisted, 201);
    const result = await todoApi.create(requestBody);
    expect(result).toEqual(persisted);
  });

  // Test Case 19: Create Todo with Title Length Exceeding Boundary (256 chars)
  it('Create Todo with Title Length Exceeding Boundary (256 chars)', async () => {
    const tooLongTitle = 'T'.repeat(256);
    const requestBody: TodoCreate = { title: tooLongTitle };
    mockFetch({ error: 'Title exceeds maximum length' }, 400);
    await expect(todoApi.create(requestBody)).rejects.toThrow('Title exceeds maximum length');
  });
});