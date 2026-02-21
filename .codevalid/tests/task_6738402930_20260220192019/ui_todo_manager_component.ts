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
  fireEvent.click(
    screen.getAllByText(/Edit/i).find(btn =>
      btn.closest('li')?.querySelector('h3')?.textContent === todoTitle
    )!
  );
  await waitFor(() => screen.getByText(/Edit todo/i));
};

describe('App Component', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  // Test Case 1: Fetch and render todos on mount
  test('Fetch and render todos on mount', async () => {
    (todoApi.list as jest.Mock).mockResolvedValueOnce(mockTodos);
    render(<App />);
    expect(todoApi.list).toHaveBeenCalledTimes(1);
    await waitFor(() => screen.getByText('Test Todo'));
    expect(screen.getByText('Test Todo')).toBeInTheDocument();
    expect(screen.getByText('Second Todo')).toBeInTheDocument();
    expect(screen.getByText('Test Description')).toBeInTheDocument();
    expect(screen.getByText('Test Notes')).toBeInTheDocument();
    expect(screen.getByText(/Expires:/)).toBeInTheDocument();
    // Optional fields blank/omitted
    expect(screen.getByText('Second Todo')).toBeInTheDocument();
  });

  // Test Case 2: Create todo with all fields
  test('Create todo with all fields', async () => {
    (todoApi.list as jest.Mock).mockResolvedValueOnce(mockTodos);
    (todoApi.create as jest.Mock).mockResolvedValueOnce({
      id: 3,
      title: 'New Todo',
      description: 'Desc',
      notes: 'Note',
      expiry_date: '2024-12-31',
    });
    render(<App />);
    await waitFor(() => screen.getByText('Test Todo'));
    await openCreateForm();
    fireEvent.change(screen.getByLabelText(/Title/i), { target: { value: 'New Todo' } });
    fireEvent.change(screen.getByLabelText(/Description/i), { target: { value: 'Desc' } });
    fireEvent.change(screen.getByLabelText(/Notes/i), { target: { value: 'Note' } });
    fireEvent.change(screen.getByLabelText(/Expiry date/i), { target: { value: '2024-12-31' } });
    fireEvent.click(screen.getByText(/Save/i));
    await waitFor(() =>
      expect(todoApi.create).toHaveBeenCalledWith({
        title: 'New Todo',
        description: 'Desc',
        notes: 'Note',
        expiry_date: '2024-12-31',
      })
    );
    await waitFor(() => screen.getByText('New Todo'));
    expect(screen.getByText('Desc')).toBeInTheDocument();
    expect(screen.getByText('Note')).toBeInTheDocument();
    expect(screen.getByText(/2024-12-31/)).toBeInTheDocument();
  });

  // Test Case 3: Create todo with title only
  test('Create todo with title only', async () => {
    (todoApi.list as jest.Mock).mockResolvedValueOnce(mockTodos);
    (todoApi.create as jest.Mock).mockResolvedValueOnce({
      id: 4,
      title: 'Title Only',
      description: undefined,
      notes: undefined,
      expiry_date: null,
    });
    render(<App />);
    await waitFor(() => screen.getByText('Test Todo'));
    await openCreateForm();
    fireEvent.change(screen.getByLabelText(/Title/i), { target: { value: 'Title Only' } });
    fireEvent.click(screen.getByText(/Save/i));
    await waitFor(() =>
      expect(todoApi.create).toHaveBeenCalledWith({
        title: 'Title Only',
        description: undefined,
        notes: undefined,
        expiry_date: null,
      })
    );
    await waitFor(() => screen.getByText('Title Only'));
    expect(screen.getByText('Title Only')).toBeInTheDocument();
    // Optional fields not rendered
    expect(screen.queryByText(/Desc/)).not.toBeInTheDocument();
    expect(screen.queryByText(/Note/)).not.toBeInTheDocument();
    expect(screen.queryByText(/Expires:/)).not.toBeInTheDocument();
  });

  // Test Case 4: Create todo missing required title
  test('Create todo missing required title', async () => {
    (todoApi.list as jest.Mock).mockResolvedValueOnce(mockTodos);
    render(<App />);
    await waitFor(() => screen.getByText('Test Todo'));
    await openCreateForm();
    fireEvent.change(screen.getByLabelText(/Title/i), { target: { value: '' } });
    fireEvent.click(screen.getByText(/Save/i));
    expect(await screen.findByText(/Title is required/i)).toBeInTheDocument();
    expect(todoApi.create).not.toHaveBeenCalled();
  });

  // Test Case 5: Create todo with empty title
  test('Create todo with empty title', async () => {
    (todoApi.list as jest.Mock).mockResolvedValueOnce(mockTodos);
    render(<App />);
    await waitFor(() => screen.getByText('Test Todo'));
    await openCreateForm();
    fireEvent.change(screen.getByLabelText(/Title/i), { target: { value: '' } });
    fireEvent.click(screen.getByText(/Save/i));
    expect(await screen.findByText(/Title is required/i)).toBeInTheDocument();
    expect(todoApi.create).not.toHaveBeenCalled();
  });

  // Test Case 6: Create todo with invalid expiry_date format
  test('Create todo with invalid expiry_date format', async () => {
    (todoApi.list as jest.Mock).mockResolvedValueOnce(mockTodos);
    render(<App />);
    await waitFor(() => screen.getByText('Test Todo'));
    await openCreateForm();
    fireEvent.change(screen.getByLabelText(/Title/i), { target: { value: 'Invalid Date Todo' } });
    fireEvent.change(screen.getByLabelText(/Expiry date/i), { target: { value: '31-12-2024' } });
    (todoApi.create as jest.Mock).mockRejectedValueOnce(new Error('Invalid date format'));
    fireEvent.click(screen.getByText(/Save/i));
    expect(await screen.findByText(/Invalid date format/i)).toBeInTheDocument();
    expect(todoApi.create).toHaveBeenCalled();
  });

  // Test Case 7: Edit todo to update some fields
  test('Edit todo to update some fields', async () => {
    (todoApi.list as jest.Mock).mockResolvedValueOnce(mockTodos);
    (todoApi.update as jest.Mock).mockResolvedValueOnce({
      ...mockTodos[0],
      description: 'Updated Desc',
      notes: 'Updated Note',
    });
    render(<App />);
    await waitFor(() => screen.getByText('Test Todo'));
    await openEditForm('Test Todo');
    fireEvent.change(screen.getByLabelText(/Description/i), { target: { value: 'Updated Desc' } });
    fireEvent.change(screen.getByLabelText(/Notes/i), { target: { value: 'Updated Note' } });
    fireEvent.click(screen.getByText(/Save/i));
    await waitFor(() =>
      expect(todoApi.update).toHaveBeenCalledWith(1, expect.objectContaining({
        description: 'Updated Desc',
        notes: 'Updated Note',
      }))
    );
    await waitFor(() => screen.getByText('Updated Desc'));
    expect(screen.getByText('Updated Note')).toBeInTheDocument();
    expect(screen.getByText('Test Todo')).toBeInTheDocument();
  });

  // Test Case 8: Edit todo with invalid expiry_date format
  test('Edit todo with invalid expiry_date format', async () => {
    (todoApi.list as jest.Mock).mockResolvedValueOnce(mockTodos);
    render(<App />);
    await waitFor(() => screen.getByText('Test Todo'));
    await openEditForm('Test Todo');
    fireEvent.change(screen.getByLabelText(/Expiry date/i), { target: { value: '12/31/2024' } });
    (todoApi.update as jest.Mock).mockRejectedValueOnce(new Error('Invalid date format'));
    fireEvent.click(screen.getByText(/Save/i));
    expect(await screen.findByText(/Invalid date format/i)).toBeInTheDocument();
    expect(todoApi.update).toHaveBeenCalled();
  });

  // Test Case 9: Edit todo to remove optional fields
  test('Edit todo to remove optional fields', async () => {
    (todoApi.list as jest.Mock).mockResolvedValueOnce([
      {
        id: 1,
        title: 'Full Todo',
        description: 'Desc',
        notes: 'Note',
        expiry_date: '2026-12-31',
      },
    ]);
    (todoApi.update as jest.Mock).mockResolvedValueOnce({
      id: 1,
      title: 'Full Todo',
      description: undefined,
      notes: undefined,
      expiry_date: null,
    });
    render(<App />);
    await waitFor(() => screen.getByText('Full Todo'));
    await openEditForm('Full Todo');
    fireEvent.change(screen.getByLabelText(/Description/i), { target: { value: '' } });
    fireEvent.change(screen.getByLabelText(/Notes/i), { target: { value: '' } });
    fireEvent.change(screen.getByLabelText(/Expiry date/i), { target: { value: '' } });
    fireEvent.click(screen.getByText(/Save/i));
    await waitFor(() =>
      expect(todoApi.update).toHaveBeenCalledWith(1, expect.objectContaining({
        description: undefined,
        notes: undefined,
        expiry_date: null,
      }))
    );
    await waitFor(() => screen.getByText('Full Todo'));
    expect(screen.queryByText('Desc')).not.toBeInTheDocument();
    expect(screen.queryByText('Note')).not.toBeInTheDocument();
    expect(screen.queryByText(/Expires:/)).not.toBeInTheDocument();
  });

  // Test Case 10: Delete todo with confirmation
  test('Delete todo with confirmation', async () => {
    (todoApi.list as jest.Mock).mockResolvedValueOnce(mockTodos);
    (todoApi.delete as jest.Mock).mockResolvedValueOnce(undefined);
    window.confirm = jest.fn(() => true);
    render(<App />);
    await waitFor(() => screen.getByText('Test Todo'));
    fireEvent.click(screen.getAllByText(/Delete/i)[0]);
    await waitFor(() => expect(todoApi.delete).toHaveBeenCalledWith(1));
    await waitFor(() => expect(screen.queryByText('Test Todo')).not.toBeInTheDocument());
  });

  // Test Case 11: Delete todo and cancel
  test('Delete todo and cancel', async () => {
    (todoApi.list as jest.Mock).mockResolvedValueOnce(mockTodos);
    window.confirm = jest.fn(() => false);
    render(<App />);
    await waitFor(() => screen.getByText('Test Todo'));
    fireEvent.click(screen.getAllByText(/Delete/i)[0]);
    expect(todoApi.delete).not.toHaveBeenCalled();
    expect(screen.getByText('Test Todo')).toBeInTheDocument();
  });

  // Test Case 12: Delete nonexistent todo
  test('Delete nonexistent todo', async () => {
    (todoApi.list as jest.Mock).mockResolvedValueOnce([
      {
        id: 99,
        title: 'Stale Todo',
        description: '',
        notes: '',
        expiry_date: null,
      },
    ]);
    (todoApi.delete as jest.Mock).mockRejectedValueOnce(new Error('Todo not found'));
    window.confirm = jest.fn(() => true);
    render(<App />);
    await waitFor(() => screen.getByText('Stale Todo'));
    fireEvent.click(screen.getAllByText(/Delete/i)[0]);
    expect(await screen.findByText(/Todo not found/i)).toBeInTheDocument();
    expect(todoApi.delete).toHaveBeenCalledWith(99);
    await waitFor(() => expect(screen.queryByText('Stale Todo')).not.toBeInTheDocument());
  });

  // Test Case 13: Get one todo renders edit form with correct data
  test('Get one todo renders edit form with correct data', async () => {
    (todoApi.list as jest.Mock).mockResolvedValueOnce([
      {
        id: 1,
        title: 'Edit Me',
        description: 'Edit Desc',
        notes: 'Edit Notes',
        expiry_date: '2024-02-29',
      },
      {
        id: 2,
        title: 'Other Todo',
        description: '',
        notes: '',
        expiry_date: null,
      },
    ]);
    render(<App />);
    await waitFor(() => screen.getByText('Edit Me'));
    await openEditForm('Edit Me');
    expect(screen.getByLabelText(/Title/i)).toHaveValue('Edit Me');
    expect(screen.getByLabelText(/Description/i)).toHaveValue('Edit Desc');
    expect(screen.getByLabelText(/Notes/i)).toHaveValue('Edit Notes');
    expect(screen.getByLabelText(/Expiry date/i)).toHaveValue('2024-02-29');
  });

  // Test Case 14: Edit nonexistent todo
  test('Edit nonexistent todo', async () => {
    (todoApi.list as jest.Mock).mockResolvedValueOnce(mockTodos);
    (todoApi.update as jest.Mock).mockRejectedValueOnce(new Error('Todo not found'));
    render(<App />);
    await waitFor(() => screen.getByText('Test Todo'));
    await openEditForm('Test Todo');
    fireEvent.click(screen.getByText(/Save/i));
    expect(await screen.findByText(/Todo not found/i)).toBeInTheDocument();
    expect(todoApi.update).toHaveBeenCalled();
  });

  // Test Case 15: List reflects all CRUD operations
  test('List reflects all CRUD operations', async () => {
    // Initial list
    (todoApi.list as jest.Mock).mockResolvedValueOnce([]);
    render(<App />);
    await waitFor(() => screen.getByText(/No todos yet/i));
    // Create
    await openCreateForm();
    fireEvent.change(screen.getByLabelText(/Title/i), { target: { value: 'CRUD Todo' } });
    (todoApi.create as jest.Mock).mockResolvedValueOnce({
      id: 10,
      title: 'CRUD Todo',
      description: 'CRUD Desc',
      notes: 'CRUD Notes',
      expiry_date: '2026-12-31',
    });
    fireEvent.change(screen.getByLabelText(/Description/i), { target: { value: 'CRUD Desc' } });
    fireEvent.change(screen.getByLabelText(/Notes/i), { target: { value: 'CRUD Notes' } });
    fireEvent.change(screen.getByLabelText(/Expiry date/i), { target: { value: '2026-12-31' } });
    fireEvent.click(screen.getByText(/Save/i));
    await waitFor(() => screen.getByText('CRUD Todo'));
    // Edit
    await openEditForm('CRUD Todo');
    fireEvent.change(screen.getByLabelText(/Description/i), { target: { value: 'Updated Desc' } });
    (todoApi.update as jest.Mock).mockResolvedValueOnce({
      id: 10,
      title: 'CRUD Todo',
      description: 'Updated Desc',
      notes: 'CRUD Notes',
      expiry_date: '2026-12-31',
    });
    fireEvent.click(screen.getByText(/Save/i));
    await waitFor(() => screen.getByText('Updated Desc'));
    // Delete
    window.confirm = jest.fn(() => true);
    (todoApi.delete as jest.Mock).mockResolvedValueOnce(undefined);
    fireEvent.click(screen.getAllByText(/Delete/i)[0]);
    await waitFor(() => expect(todoApi.delete).toHaveBeenCalledWith(10));
    await waitFor(() => expect(screen.queryByText('CRUD Todo')).not.toBeInTheDocument());
  });

  // Test Case 16: Create todo with maximum allowed title length
  test('Create todo with maximum allowed title length', async () => {
    const maxTitle = 'T'.repeat(255);
    (todoApi.list as jest.Mock).mockResolvedValueOnce(mockTodos);
    (todoApi.create as jest.Mock).mockResolvedValueOnce({
      id: 11,
      title: maxTitle,
      description: 'Desc',
      notes: 'Notes',
      expiry_date: '2026-12-31',
    });
    render(<App />);
    await waitFor(() => screen.getByText('Test Todo'));
    await openCreateForm();
    fireEvent.change(screen.getByLabelText(/Title/i), { target: { value: maxTitle } });
    fireEvent.change(screen.getByLabelText(/Description/i), { target: { value: 'Desc' } });
    fireEvent.change(screen.getByLabelText(/Notes/i), { target: { value: 'Notes' } });
    fireEvent.change(screen.getByLabelText(/Expiry date/i), { target: { value: '2026-12-31' } });
    fireEvent.click(screen.getByText(/Save/i));
    await waitFor(() =>
      expect(todoApi.create).toHaveBeenCalledWith({
        title: maxTitle,
        description: 'Desc',
        notes: 'Notes',
        expiry_date: '2026-12-31',
      })
    );
    await waitFor(() => screen.getByText(maxTitle));
    expect(screen.getByText(maxTitle)).toBeInTheDocument();
  });

  // Test Case 17: Create todo with expiry_date on leap day
  test('Create todo with expiry_date on leap day', async () => {
    (todoApi.list as jest.Mock).mockResolvedValueOnce(mockTodos);
    (todoApi.create as jest.Mock).mockResolvedValueOnce({
      id: 12,
      title: 'Leap Day Todo',
      description: 'Leap Desc',
      notes: 'Leap Notes',
      expiry_date: '2024-02-29',
    });
    render(<App />);
    await waitFor(() => screen.getByText('Test Todo'));
    await openCreateForm();
    fireEvent.change(screen.getByLabelText(/Title/i), { target: { value: 'Leap Day Todo' } });
    fireEvent.change(screen.getByLabelText(/Description/i), { target: { value: 'Leap Desc' } });
    fireEvent.change(screen.getByLabelText(/Notes/i), { target: { value: 'Leap Notes' } });
    fireEvent.change(screen.getByLabelText(/Expiry date/i), { target: { value: '2024-02-29' } });
    fireEvent.click(screen.getByText(/Save/i));
    await waitFor(() =>
      expect(todoApi.create).toHaveBeenCalledWith({
        title: 'Leap Day Todo',
        description: 'Leap Desc',
        notes: 'Leap Notes',
        expiry_date: '2024-02-29',
      })
    );
    await waitFor(() => screen.getByText('Leap Day Todo'));
    expect(screen.getByText(/2024-02-29/)).toBeInTheDocument();
  });

  // Test Case 18: Edit todo and set title to empty
  test('Edit todo and set title to empty', async () => {
    (todoApi.list as jest.Mock).mockResolvedValueOnce(mockTodos);
    render(<App />);
    await waitFor(() => screen.getByText('Test Todo'));
    await openEditForm('Test Todo');
    fireEvent.change(screen.getByLabelText(/Title/i), { target: { value: '' } });
    fireEvent.click(screen.getByText(/Save/i));
    expect(await screen.findByText(/Title is required/i)).toBeInTheDocument();
    expect(todoApi.update).not.toHaveBeenCalled();
  });

  // Test Case 19: Handle network error on API calls
  test('Handle network error on API calls', async () => {
    (todoApi.list as jest.Mock).mockRejectedValueOnce(new Error('Network error'));
    render(<App />);
    expect(await screen.findByText(/Network error/i)).toBeInTheDocument();

    // Create
    (todoApi.list as jest.Mock).mockResolvedValueOnce(mockTodos);
    render(<App />);
    await waitFor(() => screen.getByText('Test Todo'));
    await openCreateForm();
    fireEvent.change(screen.getByLabelText(/Title/i), { target: { value: 'NetErr Todo' } });
    (todoApi.create as jest.Mock).mockRejectedValueOnce(new Error('Network error'));
    fireEvent.click(screen.getByText(/Save/i));
    expect(await screen.findByText(/Network error/i)).toBeInTheDocument();

    // Edit
    await openEditForm('Test Todo');
    (todoApi.update as jest.Mock).mockRejectedValueOnce(new Error('Network error'));
    fireEvent.click(screen.getByText(/Save/i));
    expect(await screen.findByText(/Network error/i)).toBeInTheDocument();

    // Delete
    window.confirm = jest.fn(() => true);
    (todoApi.delete as jest.Mock).mockRejectedValueOnce(new Error('Network error'));
    fireEvent.click(screen.getAllByText(/Delete/i)[0]);
    expect(await screen.findByText(/Network error/i)).toBeInTheDocument();
  });
});