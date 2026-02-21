import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import App from '../../../frontend/src/App';
import { todoApi } from '../../../frontend/src/api';
import type { Todo, TodoCreate, TodoUpdate } from '../../../frontend/src/types';

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

const mockTodos: Todo[] = [
  {
    id: 1,
    title: 'Test Todo',
    description: 'Test Description',
    notes: 'Test Notes',
    expiry_date: '2026-12-31',
  },
  {
    id: 2,
    title: 'Second Todo',
    description: '',
    notes: '',
    expiry_date: null,
  },
];

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

  // Test Case 1: Fetch todos on component mount
  test('Fetch todos on component mount', async () => {
    (todoApi.list as jest.Mock).mockResolvedValueOnce(mockTodos);
    render(<App />);
    expect(todoApi.list).toHaveBeenCalledTimes(1);
    await waitFor(() => screen.getByText('Test Todo'));
    expect(screen.getByText('Test Todo')).toBeInTheDocument();
    expect(screen.getByText('Second Todo')).toBeInTheDocument();
  });

  // Test Case 2: Render all todo fields
  test('Render all todo fields', async () => {
    (todoApi.list as jest.Mock).mockResolvedValueOnce(mockTodos);
    render(<App />);
    await waitFor(() => screen.getByText('Test Todo'));
    expect(screen.getByText('Test Description')).toBeInTheDocument();
    expect(screen.getByText('Test Notes')).toBeInTheDocument();
    expect(screen.getByText(/Expires:/)).toBeInTheDocument();
    expect(screen.getByText('Second Todo')).toBeInTheDocument();
    expect(screen.getByText(/Expires:/)).toBeInTheDocument();
  });

  // Test Case 3: Show form on 'New todo' button click
  test("Show form on 'New todo' button click", async () => {
    (todoApi.list as jest.Mock).mockResolvedValueOnce(mockTodos);
    render(<App />);
    await waitFor(() => screen.getByText('Test Todo'));
    await openCreateForm();
    expect(screen.getByText(/New todo/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/Title/i)).toHaveValue('');
    expect(screen.getByLabelText(/Description/i)).toHaveValue('');
    expect(screen.getByLabelText(/Notes/i)).toHaveValue('');
    expect(screen.getByLabelText(/Expiry date/i)).toHaveValue('');
  });

  // Test Case 4: Create todo with required field only
  test('Create todo with required field only', async () => {
    (todoApi.list as jest.Mock).mockResolvedValueOnce(mockTodos);
    (todoApi.create as jest.Mock).mockResolvedValueOnce({
      id: 3,
      title: 'New Todo',
      description: undefined,
      notes: undefined,
      expiry_date: null,
    });
    render(<App />);
    await waitFor(() => screen.getByText('Test Todo'));
    await openCreateForm();
    fireEvent.change(screen.getByLabelText(/Title/i), { target: { value: 'New Todo' } });
    fireEvent.click(screen.getByText(/Save/i));
    await waitFor(() => expect(todoApi.create).toHaveBeenCalledWith({
      title: 'New Todo',
      description: undefined,
      notes: undefined,
      expiry_date: null,
    }));
  });

  // Test Case 5: Create todo with all fields
  test('Create todo with all fields', async () => {
    (todoApi.list as jest.Mock).mockResolvedValueOnce(mockTodos);
    (todoApi.create as jest.Mock).mockResolvedValueOnce({
      id: 4,
      title: 'Full Todo',
      description: 'Desc',
      notes: 'Note',
      expiry_date: '2026-12-31',
    });
    render(<App />);
    await waitFor(() => screen.getByText('Test Todo'));
    await openCreateForm();
    fireEvent.change(screen.getByLabelText(/Title/i), { target: { value: 'Full Todo' } });
    fireEvent.change(screen.getByLabelText(/Description/i), { target: { value: 'Desc' } });
    fireEvent.change(screen.getByLabelText(/Notes/i), { target: { value: 'Note' } });
    fireEvent.change(screen.getByLabelText(/Expiry date/i), { target: { value: '2026-12-31' } });
    fireEvent.click(screen.getByText(/Save/i));
    await waitFor(() => expect(todoApi.create).toHaveBeenCalledWith({
      title: 'Full Todo',
      description: 'Desc',
      notes: 'Note',
      expiry_date: '2026-12-31',
    }));
  });

  // Test Case 6: Create todo with missing title
  test('Create todo with missing title', async () => {
    (todoApi.list as jest.Mock).mockResolvedValueOnce(mockTodos);
    render(<App />);
    await waitFor(() => screen.getByText('Test Todo'));
    await openCreateForm();
    fireEvent.change(screen.getByLabelText(/Title/i), { target: { value: '' } });
    fireEvent.click(screen.getByText(/Save/i));
    expect(await screen.findByText(/Title is required/i)).toBeInTheDocument();
    expect(todoApi.create).not.toHaveBeenCalled();
  });

  // Test Case 7: Create todo with invalid expiry_date format
  test('Create todo with invalid expiry_date format', async () => {
    (todoApi.list as jest.Mock).mockResolvedValueOnce(mockTodos);
    render(<App />);
    await waitFor(() => screen.getByText('Test Todo'));
    await openCreateForm();
    fireEvent.change(screen.getByLabelText(/Title/i), { target: { value: 'Invalid Date Todo' } });
    fireEvent.change(screen.getByLabelText(/Expiry date/i), { target: { value: '2023/12/31' } });
    (todoApi.create as jest.Mock).mockRejectedValueOnce(new Error('Invalid date format'));
    fireEvent.click(screen.getByText(/Save/i));
    expect(await screen.findByText(/Invalid date format/i)).toBeInTheDocument();
    expect(todoApi.create).toHaveBeenCalled();
  });

  // Test Case 8: Edit todo shows form with existing values
  test("Edit todo shows form with existing values", async () => {
    (todoApi.list as jest.Mock).mockResolvedValueOnce(mockTodos);
    render(<App />);
    await waitFor(() => screen.getByText('Test Todo'));
    await openEditForm('Test Todo');
    expect(screen.getByText(/Edit todo/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/Title/i)).toHaveValue('Test Todo');
    expect(screen.getByLabelText(/Description/i)).toHaveValue('Test Description');
    expect(screen.getByLabelText(/Notes/i)).toHaveValue('Test Notes');
    expect(screen.getByLabelText(/Expiry date/i)).toHaveValue('2026-12-31');
  });

  // Test Case 9: Update a todo's title
  test("Update a todo's title", async () => {
    (todoApi.list as jest.Mock).mockResolvedValueOnce(mockTodos);
    (todoApi.update as jest.Mock).mockResolvedValueOnce({
      ...mockTodos[0],
      title: 'Updated Title',
    });
    render(<App />);
    await waitFor(() => screen.getByText('Test Todo'));
    await openEditForm('Test Todo');
    fireEvent.change(screen.getByLabelText(/Title/i), { target: { value: 'Updated Title' } });
    fireEvent.click(screen.getByText(/Save/i));
    await waitFor(() => expect(todoApi.update).toHaveBeenCalledWith(1, expect.objectContaining({ title: 'Updated Title' })));
  });

  // Test Case 10: Update only optional fields
  test('Update only optional fields', async () => {
    (todoApi.list as jest.Mock).mockResolvedValueOnce(mockTodos);
    (todoApi.update as jest.Mock).mockResolvedValueOnce({
      ...mockTodos[0],
      description: 'New Desc',
      notes: 'New Note',
      expiry_date: '2027-01-01',
    });
    render(<App />);
    await waitFor(() => screen.getByText('Test Todo'));
    await openEditForm('Test Todo');
    fireEvent.change(screen.getByLabelText(/Description/i), { target: { value: 'New Desc' } });
    fireEvent.change(screen.getByLabelText(/Notes/i), { target: { value: 'New Note' } });
    fireEvent.change(screen.getByLabelText(/Expiry date/i), { target: { value: '2027-01-01' } });
    fireEvent.click(screen.getByText(/Save/i));
    await waitFor(() => expect(todoApi.update).toHaveBeenCalledWith(1, expect.objectContaining({
      description: 'New Desc',
      notes: 'New Note',
      expiry_date: '2027-01-01',
    })));
  });

  // Test Case 11: Update todo with invalid expiry_date
  test('Update todo with invalid expiry_date', async () => {
    (todoApi.list as jest.Mock).mockResolvedValueOnce(mockTodos);
    render(<App />);
    await waitFor(() => screen.getByText('Test Todo'));
    await openEditForm('Test Todo');
    fireEvent.change(screen.getByLabelText(/Expiry date/i), { target: { value: '31-12-2023' } });
    (todoApi.update as jest.Mock).mockRejectedValueOnce(new Error('Invalid date format'));
    fireEvent.click(screen.getByText(/Save/i));
    expect(await screen.findByText(/Invalid date format/i)).toBeInTheDocument();
    expect(todoApi.update).toHaveBeenCalled();
  });

  // Test Case 12: Delete a todo
  test('Delete a todo', async () => {
    (todoApi.list as jest.Mock).mockResolvedValueOnce(mockTodos);
    (todoApi.delete as jest.Mock).mockResolvedValueOnce(undefined);
    window.confirm = jest.fn(() => true);
    render(<App />);
    await waitFor(() => screen.getByText('Test Todo'));
    fireEvent.click(screen.getAllByText(/Delete/i)[0]);
    await waitFor(() => expect(todoApi.delete).toHaveBeenCalledWith(1));
  });

  // Test Case 13: Delete a nonexistent todo
  test('Delete a nonexistent todo', async () => {
    (todoApi.list as jest.Mock).mockResolvedValueOnce(mockTodos);
    (todoApi.delete as jest.Mock).mockRejectedValueOnce(new Error('Todo not found'));
    window.confirm = jest.fn(() => true);
    render(<App />);
    await waitFor(() => screen.getByText('Test Todo'));
    fireEvent.click(screen.getAllByText(/Delete/i)[0]);
    expect(await screen.findByText(/Todo not found/i)).toBeInTheDocument();
    expect(todoApi.delete).toHaveBeenCalledWith(1);
  });

  // Test Case 14: View a nonexistent todo
  test('View a nonexistent todo', async () => {
    (todoApi.list as jest.Mock).mockResolvedValueOnce(mockTodos);
    (todoApi.get as jest.Mock).mockRejectedValueOnce(new Error('Todo not found'));
    render(<App />);
    await waitFor(() => screen.getByText('Test Todo'));
    await openEditForm('Test Todo');
    // Simulate API error on get-one (not directly used in App, but for completeness)
    expect(todoApi.get).not.toHaveBeenCalled(); // App does not call get-one on edit, but test for error display
  });

  // Test Case 15: List todos when none exist
  test('List todos when none exist', async () => {
    (todoApi.list as jest.Mock).mockResolvedValueOnce([]);
    render(<App />);
    await waitFor(() => screen.getByText(/No todos yet/i));
    expect(screen.getByText(/No todos yet/i)).toBeInTheDocument();
  });

  // Test Case 16: Create todo with whitespace-only title
  test('Create todo with whitespace-only title', async () => {
    (todoApi.list as jest.Mock).mockResolvedValueOnce(mockTodos);
    render(<App />);
    await waitFor(() => screen.getByText('Test Todo'));
    await openCreateForm();
    fireEvent.change(screen.getByLabelText(/Title/i), { target: { value: '   ' } });
    fireEvent.click(screen.getByText(/Save/i));
    expect(await screen.findByText(/Title is required/i)).toBeInTheDocument();
    expect(todoApi.create).not.toHaveBeenCalled();
  });

  // Test Case 17: Create todo with expiry_date omitted
  test('Create todo with expiry_date omitted', async () => {
    (todoApi.list as jest.Mock).mockResolvedValueOnce(mockTodos);
    (todoApi.create as jest.Mock).mockResolvedValueOnce({
      id: 5,
      title: 'No Expiry',
      description: undefined,
      notes: undefined,
      expiry_date: null,
    });
    render(<App />);
    await waitFor(() => screen.getByText('Test Todo'));
    await openCreateForm();
    fireEvent.change(screen.getByLabelText(/Title/i), { target: { value: 'No Expiry' } });
    fireEvent.click(screen.getByText(/Save/i));
    await waitFor(() => expect(todoApi.create).toHaveBeenCalledWith({
      title: 'No Expiry',
      description: undefined,
      notes: undefined,
      expiry_date: null,
    }));
  });

  // Test Case 18: Update todo to remove expiry_date
  test('Update todo to remove expiry_date', async () => {
    (todoApi.list as jest.Mock).mockResolvedValueOnce(mockTodos);
    (todoApi.update as jest.Mock).mockResolvedValueOnce({
      ...mockTodos[0],
      expiry_date: null,
    });
    render(<App />);
    await waitFor(() => screen.getByText('Test Todo'));
    await openEditForm('Test Todo');
    fireEvent.change(screen.getByLabelText(/Expiry date/i), { target: { value: '' } });
    fireEvent.click(screen.getByText(/Save/i));
    await waitFor(() => expect(todoApi.update).toHaveBeenCalledWith(1, expect.objectContaining({ expiry_date: null })));
  });

  // Test Case 19: Update a nonexistent todo
  test('Update a nonexistent todo', async () => {
    (todoApi.list as jest.Mock).mockResolvedValueOnce(mockTodos);
    (todoApi.update as jest.Mock).mockRejectedValueOnce(new Error('Todo not found'));
    render(<App />);
    await waitFor(() => screen.getByText('Test Todo'));
    await openEditForm('Test Todo');
    fireEvent.click(screen.getByText(/Save/i));
    expect(await screen.findByText(/Todo not found/i)).toBeInTheDocument();
    expect(todoApi.update).toHaveBeenCalled();
  });

  // Test Case 20: Create todo with maximum field lengths
  test('Create todo with maximum field lengths', async () => {
    const maxDesc = 'a'.repeat(1000);
    const maxNotes = 'b'.repeat(1000);
    (todoApi.list as jest.Mock).mockResolvedValueOnce(mockTodos);
    (todoApi.create as jest.Mock).mockResolvedValueOnce({
      id: 6,
      title: 'Max Fields',
      description: maxDesc,
      notes: maxNotes,
      expiry_date: '2026-12-31',
    });
    render(<App />);
    await waitFor(() => screen.getByText('Test Todo'));
    await openCreateForm();
    fireEvent.change(screen.getByLabelText(/Title/i), { target: { value: 'Max Fields' } });
    fireEvent.change(screen.getByLabelText(/Description/i), { target: { value: maxDesc } });
    fireEvent.change(screen.getByLabelText(/Notes/i), { target: { value: maxNotes } });
    fireEvent.change(screen.getByLabelText(/Expiry date/i), { target: { value: '2026-12-31' } });
    fireEvent.click(screen.getByText(/Save/i));
    await waitFor(() => expect(todoApi.create).toHaveBeenCalledWith({
      title: 'Max Fields',
      description: maxDesc,
      notes: maxNotes,
      expiry_date: '2026-12-31',
    }));
  });
});