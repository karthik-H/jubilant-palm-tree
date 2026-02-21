import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import App from '../../../frontend/src/App';
import { todoApi } from '../../../frontend/src/api';
import type { Todo } from '../../../frontend/src/types';

// Mock todoApi
jest.mock('../../../frontend/src/api', () => ({
  todoApi: {
    list: jest.fn(),
    get: jest.fn(),
    create: jest.fn(),
    update: jest.fn(),
    delete: jest.fn(),
  },
}));

// Helper to open TodoForm for creation
const openCreateForm = async () => {
  fireEvent.click(screen.getByText(/New todo/i));
  await waitFor(() => screen.getByText(/New todo/i));
};

// Helper to open TodoForm for editing
const openEditForm = async (todoTitle: string) => {
  fireEvent.click(screen.getAllByText(/Edit/i).find(btn =>
    btn.closest('li')?.querySelector('h3')?.textContent === todoTitle
  )!);
  await waitFor(() => screen.getByText(/Edit todo/i));
};

describe('App Component', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  // Test Case 1: List todos on mount
  test('List todos on mount', async () => {
    (todoApi.list as jest.Mock).mockResolvedValueOnce([
      {
        id: 1,
        title: 'Buy milk',
        description: 'Grocery',
        notes: null,
        expiry_date: '2024-07-01',
      },
    ]);
    render(<App />);
    expect(todoApi.list).toHaveBeenCalledTimes(1);
    await waitFor(() => screen.getByText('Buy milk'));
    expect(screen.getByText('Buy milk')).toBeInTheDocument();
    expect(screen.getByText('Grocery')).toBeInTheDocument();
    expect(screen.getByText('2024-07-01')).toBeInTheDocument();
    expect(screen.getByText(/Edit/i)).toBeInTheDocument();
    expect(screen.getByText(/Delete/i)).toBeInTheDocument();
    expect(screen.queryByText('null')).not.toBeInTheDocument();
  });

  // Test Case 2: Create todo with all fields successfully
  test('Create todo with all fields successfully', async () => {
    (todoApi.list as jest.Mock).mockResolvedValueOnce([]);
    (todoApi.create as jest.Mock).mockResolvedValueOnce({
      id: 10,
      title: 'Task',
      description: 'My desc',
      notes: 'Important',
      expiry_date: '2024-08-15',
    });
    render(<App />);
    await openCreateForm();
    fireEvent.change(screen.getByLabelText(/Title/i), { target: { value: 'Task' } });
    fireEvent.change(screen.getByLabelText(/Description/i), { target: { value: 'My desc' } });
    fireEvent.change(screen.getByLabelText(/Notes/i), { target: { value: 'Important' } });
    fireEvent.change(screen.getByLabelText(/Expiry date/i), { target: { value: '2024-08-15' } });
    fireEvent.click(screen.getByText(/Save/i));
    await waitFor(() => expect(todoApi.create).toHaveBeenCalledWith({
      title: 'Task',
      description: 'My desc',
      notes: 'Important',
      expiry_date: '2024-08-15',
    }));
    await waitFor(() => screen.getByText('Task'));
    expect(screen.getByText('My desc')).toBeInTheDocument();
    expect(screen.getByText('Important')).toBeInTheDocument();
    expect(screen.getByText('2024-08-15')).toBeInTheDocument();
  });

  // Test Case 3: Create todo with only title (required field)
  test('Create todo with only title (required field)', async () => {
    (todoApi.list as jest.Mock).mockResolvedValueOnce([]);
    (todoApi.create as jest.Mock).mockResolvedValueOnce({
      id: 11,
      title: 'Read book',
      description: null,
      notes: null,
      expiry_date: null,
    });
    render(<App />);
    await openCreateForm();
    fireEvent.change(screen.getByLabelText(/Title/i), { target: { value: 'Read book' } });
    fireEvent.click(screen.getByText(/Save/i));
    await waitFor(() => expect(todoApi.create).toHaveBeenCalledWith({
      title: 'Read book',
      description: null,
      notes: null,
      expiry_date: null,
    }));
    await waitFor(() => screen.getByText('Read book'));
    expect(screen.queryByText('My desc')).not.toBeInTheDocument();
    expect(screen.queryByText('Important')).not.toBeInTheDocument();
    expect(screen.queryByText('2024-08-15')).not.toBeInTheDocument();
  });

  // Test Case 4: Fail to create todo with missing title
  test('Fail to create todo with missing title', async () => {
    (todoApi.list as jest.Mock).mockResolvedValueOnce([]);
    render(<App />);
    await openCreateForm();
    fireEvent.change(screen.getByLabelText(/Title/i), { target: { value: '' } });
    fireEvent.click(screen.getByText(/Save/i));
    expect(await screen.findByText(/Title is required/i)).toBeInTheDocument();
    expect(todoApi.create).not.toHaveBeenCalled();
  });

  // Test Case 5: Fail to create todo with empty title
  test('Fail to create todo with empty title', async () => {
    (todoApi.list as jest.Mock).mockResolvedValueOnce([]);
    render(<App />);
    await openCreateForm();
    fireEvent.change(screen.getByLabelText(/Title/i), { target: { value: '   ' } });
    fireEvent.click(screen.getByText(/Save/i));
    expect(await screen.findByText(/Title is required/i)).toBeInTheDocument();
    expect(todoApi.create).not.toHaveBeenCalled();
  });

  // Test Case 6: Fail to create todo with invalid expiry_date format
  test('Fail to create todo with invalid expiry_date format', async () => {
    (todoApi.list as jest.Mock).mockResolvedValueOnce([]);
    render(<App />);
    await openCreateForm();
    fireEvent.change(screen.getByLabelText(/Title/i), { target: { value: 'Test' } });
    fireEvent.change(screen.getByLabelText(/Expiry date/i), { target: { value: '15/07/2024' } });
    fireEvent.click(screen.getByText(/Save/i));
    expect(await screen.findByText(/Invalid expiry_date format/i)).toBeInTheDocument();
    expect(todoApi.create).not.toHaveBeenCalled();
  });

  // Test Case 7: Edit todo successfully
  test('Edit todo successfully', async () => {
    (todoApi.list as jest.Mock).mockResolvedValueOnce([
      {
        id: 1,
        title: 'Old title',
        description: 'desc',
        notes: '',
        expiry_date: '2024-07-01',
      },
    ]);
    (todoApi.update as jest.Mock).mockResolvedValueOnce({
      id: 1,
      title: 'New title',
      description: 'desc',
      notes: '',
      expiry_date: '2024-07-01',
    });
    render(<App />);
    await waitFor(() => screen.getByText('Old title'));
    await openEditForm('Old title');
    fireEvent.change(screen.getByLabelText(/Title/i), { target: { value: 'New title' } });
    fireEvent.click(screen.getByText(/Save/i));
    await waitFor(() => expect(todoApi.update).toHaveBeenCalledWith(1, expect.objectContaining({ title: 'New title' })));
    await waitFor(() => screen.getByText('New title'));
    expect(screen.getByText('desc')).toBeInTheDocument();
    expect(screen.getByText('2024-07-01')).toBeInTheDocument();
  });

  // Test Case 8: Edit only some fields of a todo
  test('Edit only some fields of a todo', async () => {
    (todoApi.list as jest.Mock).mockResolvedValueOnce([
      {
        id: 2,
        title: 'Laundry',
        description: 'clothes',
        notes: null,
        expiry_date: null,
      },
    ]);
    (todoApi.update as jest.Mock).mockResolvedValueOnce({
      id: 2,
      title: 'Laundry',
      description: 'clothes',
      notes: 'Use gentle cycle',
      expiry_date: null,
    });
    render(<App />);
    await waitFor(() => screen.getByText('Laundry'));
    await openEditForm('Laundry');
    fireEvent.change(screen.getByLabelText(/Notes/i), { target: { value: 'Use gentle cycle' } });
    fireEvent.click(screen.getByText(/Save/i));
    await waitFor(() => expect(todoApi.update).toHaveBeenCalledWith(2, expect.objectContaining({ notes: 'Use gentle cycle' })));
    await waitFor(() => screen.getByText('Use gentle cycle'));
    expect(screen.getByText('clothes')).toBeInTheDocument();
    expect(screen.queryByText(/Expiry date/i)).not.toBeInTheDocument();
  });

  // Test Case 9: Fail to edit todo with invalid expiry_date format
  test('Fail to edit todo with invalid expiry_date format', async () => {
    (todoApi.list as jest.Mock).mockResolvedValueOnce([
      {
        id: 3,
        title: 'Submit report',
        description: 'Work',
        notes: null,
        expiry_date: '2024-09-01',
      },
    ]);
    render(<App />);
    await waitFor(() => screen.getByText('Submit report'));
    await openEditForm('Submit report');
    fireEvent.change(screen.getByLabelText(/Expiry date/i), { target: { value: '1st Sep 2024' } });
    fireEvent.click(screen.getByText(/Save/i));
    expect(await screen.findByText(/Invalid expiry_date format/i)).toBeInTheDocument();
    expect(todoApi.update).not.toHaveBeenCalled();
  });

  // Test Case 10: Fail to edit todo by removing title
  test('Fail to edit todo by removing title', async () => {
    (todoApi.list as jest.Mock).mockResolvedValueOnce([
      {
        id: 4,
        title: 'Meet John',
        description: '',
        notes: null,
        expiry_date: null,
      },
    ]);
    render(<App />);
    await waitFor(() => screen.getByText('Meet John'));
    await openEditForm('Meet John');
    fireEvent.change(screen.getByLabelText(/Title/i), { target: { value: '' } });
    fireEvent.click(screen.getByText(/Save/i));
    expect(await screen.findByText(/Title is required/i)).toBeInTheDocument();
    expect(todoApi.update).not.toHaveBeenCalled();
  });

  // Test Case 11: Delete todo successfully
  test('Delete todo successfully', async () => {
    (todoApi.list as jest.Mock).mockResolvedValueOnce([
      { id: 5, title: 'Todo 5', description: '', notes: null, expiry_date: null },
      { id: 6, title: 'Todo 6', description: '', notes: null, expiry_date: null },
    ]);
    (todoApi.delete as jest.Mock).mockResolvedValueOnce(undefined);
    window.confirm = jest.fn(() => true);
    render(<App />);
    await waitFor(() => screen.getByText('Todo 5'));
    fireEvent.click(screen.getAllByText(/Delete/i)[0]);
    await waitFor(() => expect(todoApi.delete).toHaveBeenCalledWith(5));
    (todoApi.list as jest.Mock).mockResolvedValueOnce([
      { id: 6, title: 'Todo 6', description: '', notes: null, expiry_date: null },
    ]);
    await waitFor(() => screen.getByText('Todo 6'));
    expect(screen.queryByText('Todo 5')).not.toBeInTheDocument();
  });

  // Test Case 12: Fail to delete a nonexistent todo
  test('Fail to delete a nonexistent todo', async () => {
    (todoApi.list as jest.Mock).mockResolvedValueOnce([
      { id: 7, title: 'Todo 7', description: '', notes: null, expiry_date: null },
    ]);
    (todoApi.delete as jest.Mock).mockRejectedValueOnce(new Error('Todo not found'));
    window.confirm = jest.fn(() => true);
    render(<App />);
    await waitFor(() => screen.getByText('Todo 7'));
    fireEvent.click(screen.getAllByText(/Delete/i)[0]);
    expect(await screen.findByText(/Todo not found/i)).toBeInTheDocument();
    expect(todoApi.delete).toHaveBeenCalledWith(7);
    expect(screen.getByText('Todo 7')).toBeInTheDocument();
  });

  // Test Case 13: View details of a todo
  test('View details of a todo', async () => {
    (todoApi.list as jest.Mock).mockResolvedValueOnce([
      { id: 8, title: 'Detail Todo', description: 'desc', notes: 'note', expiry_date: '2024-10-10' },
    ]);
    (todoApi.get as jest.Mock).mockResolvedValueOnce({
      id: 8,
      title: 'Detail Todo',
      description: 'desc',
      notes: 'note',
      expiry_date: '2024-10-10',
    });
    render(<App />);
    await waitFor(() => screen.getByText('Detail Todo'));
    fireEvent.click(screen.getByText('Detail Todo'));
    await waitFor(() => expect(todoApi.get).toHaveBeenCalledWith(8));
    expect(screen.getByText('Detail Todo')).toBeInTheDocument();
    expect(screen.getByText('desc')).toBeInTheDocument();
    expect(screen.getByText('note')).toBeInTheDocument();
    expect(screen.getByText('2024-10-10')).toBeInTheDocument();
  });

  // Test Case 14: Fail to get a nonexistent todo
  test('Fail to get a nonexistent todo', async () => {
    (todoApi.list as jest.Mock).mockResolvedValueOnce([]);
    (todoApi.get as jest.Mock).mockRejectedValueOnce(new Error('Todo not found'));
    render(<App />);
    fireEvent.click(screen.getByText(/New todo/i));
    fireEvent.click(screen.getByText(/View details/i));
    expect(await screen.findByText(/Todo not found/i)).toBeInTheDocument();
  });

  // Test Case 15: expiry_date is optional on create
  test('expiry_date is optional on create', async () => {
    (todoApi.list as jest.Mock).mockResolvedValueOnce([]);
    (todoApi.create as jest.Mock).mockResolvedValueOnce({
      id: 12,
      title: 'No deadline',
      description: null,
      notes: null,
      expiry_date: null,
    });
    render(<App />);
    await openCreateForm();
    fireEvent.change(screen.getByLabelText(/Title/i), { target: { value: 'No deadline' } });
    fireEvent.click(screen.getByText(/Save/i));
    await waitFor(() => expect(todoApi.create).toHaveBeenCalledWith({
      title: 'No deadline',
      description: null,
      notes: null,
      expiry_date: null,
    }));
    await waitFor(() => screen.getByText('No deadline'));
    expect(screen.queryByText('null')).not.toBeInTheDocument();
  });

  // Test Case 16: Create todo with maximum reasonable length fields
  test('Create todo with maximum reasonable length fields', async () => {
    const maxTitle = 'a'.repeat(255);
    const maxDesc = 'b'.repeat(255);
    const maxNotes = 'c'.repeat(255);
    (todoApi.list as jest.Mock).mockResolvedValueOnce([]);
    (todoApi.create as jest.Mock).mockResolvedValueOnce({
      id: 13,
      title: maxTitle,
      description: maxDesc,
      notes: maxNotes,
      expiry_date: '2024-12-31',
    });
    render(<App />);
    await openCreateForm();
    fireEvent.change(screen.getByLabelText(/Title/i), { target: { value: maxTitle } });
    fireEvent.change(screen.getByLabelText(/Description/i), { target: { value: maxDesc } });
    fireEvent.change(screen.getByLabelText(/Notes/i), { target: { value: maxNotes } });
    fireEvent.change(screen.getByLabelText(/Expiry date/i), { target: { value: '2024-12-31' } });
    fireEvent.click(screen.getByText(/Save/i));
    await waitFor(() => expect(todoApi.create).toHaveBeenCalledWith({
      title: maxTitle,
      description: maxDesc,
      notes: maxNotes,
      expiry_date: '2024-12-31',
    }));
    await waitFor(() => screen.getByText(maxTitle));
    expect(screen.getByText(maxDesc)).toBeInTheDocument();
    expect(screen.getByText(maxNotes)).toBeInTheDocument();
    expect(screen.getByText('2024-12-31')).toBeInTheDocument();
  });

  // Test Case 17: Multiple todos are listed in order
  test('Multiple todos are listed in order', async () => {
    const todos = [
      { id: 21, title: 'First', description: 'desc1', notes: 'note1', expiry_date: '2024-06-01' },
      { id: 22, title: 'Second', description: 'desc2', notes: 'note2', expiry_date: '2024-07-01' },
      { id: 23, title: 'Third', description: 'desc3', notes: 'note3', expiry_date: '2024-08-01' },
    ];
    (todoApi.list as jest.Mock).mockResolvedValueOnce(todos);
    render(<App />);
    await waitFor(() => screen.getByText('First'));
    const todoTitles = screen.getAllByRole('heading').map(h => h.textContent);
    expect(todoTitles).toEqual(['First', 'Second', 'Third']);
  });

  // Test Case 18: User can cancel todo creation or editing
  test('User can cancel todo creation or editing', async () => {
    (todoApi.list as jest.Mock).mockResolvedValueOnce([]);
    render(<App />);
    await openCreateForm();
    fireEvent.click(screen.getByText(/Cancel/i));
    expect(screen.queryByLabelText(/Title/i)).not.toBeInTheDocument();
    expect(todoApi.create).not.toHaveBeenCalled();

    (todoApi.list as jest.Mock).mockResolvedValueOnce([
      { id: 30, title: 'EditMe', description: '', notes: null, expiry_date: null },
    ]);
    render(<App />);
    await waitFor(() => screen.getByText('EditMe'));
    await openEditForm('EditMe');
    fireEvent.click(screen.getByText(/Cancel/i));
    expect(screen.queryByLabelText(/Title/i)).not.toBeInTheDocument();
    expect(todoApi.update).not.toHaveBeenCalled();
  });

  // Test Case 19: Cancelling delete does not remove todo
  test('Cancelling delete does not remove todo', async () => {
    (todoApi.list as jest.Mock).mockResolvedValueOnce([
      { id: 10, title: 'CancelDelete', description: '', notes: null, expiry_date: null },
    ]);
    window.confirm = jest.fn(() => false);
    render(<App />);
    await waitFor(() => screen.getByText('CancelDelete'));
    fireEvent.click(screen.getAllByText(/Delete/i)[0]);
    expect(todoApi.delete).not.toHaveBeenCalled();
    expect(screen.getByText('CancelDelete')).toBeInTheDocument();
  });
});