import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import TodoForm from '../../../frontend/src/App';

// Helper to get input fields
function getFields() {
  return {
    title: screen.getByLabelText(/title/i),
    description: screen.getByLabelText(/description/i),
    notes: screen.getByLabelText(/notes/i),
    expiry_date: screen.getByLabelText(/expiry_date|expiry date/i),
    saveBtn: screen.getByRole('button', { name: /submit|save/i }),
  };
}

describe('TodoForm Component', () => {
  // Test Case 1: Create todo with all valid fields
  test('Create todo with all valid fields', async () => {
    const onSave = jest.fn();
    render(
      <TodoForm
        initial={{ title: '', description: '', notes: '', expiry_date: '' }}
        onSave={onSave}
      />
    );
    const { title, description, notes, expiry_date, saveBtn } = getFields();
    fireEvent.change(title, { target: { value: 'Buy groceries' } });
    fireEvent.change(description, { target: { value: 'Weekly shopping' } });
    fireEvent.change(notes, { target: { value: 'Remember to use coupons' } });
    fireEvent.change(expiry_date, { target: { value: '2024-07-01' } });
    fireEvent.click(saveBtn);

    await waitFor(() =>
      expect(onSave).toHaveBeenCalledWith({
        title: 'Buy groceries',
        description: 'Weekly shopping',
        notes: 'Remember to use coupons',
        expiry_date: '2024-07-01',
      })
    );
    expect(screen.queryByText(/title is required/i)).not.toBeInTheDocument();
  });

  // Test Case 2: Create todo with only required title
  test('Create todo with only required title', async () => {
    const onSave = jest.fn();
    render(
      <TodoForm
        initial={{ title: '', description: '', notes: '', expiry_date: '' }}
        onSave={onSave}
      />
    );
    const { title, saveBtn } = getFields();
    fireEvent.change(title, { target: { value: 'Call mom' } });
    fireEvent.click(saveBtn);

    await waitFor(() =>
      expect(onSave).toHaveBeenCalledWith({
        title: 'Call mom',
        description: '',
        notes: '',
        expiry_date: '',
      })
    );
    expect(screen.queryByText(/title is required/i)).not.toBeInTheDocument();
  });

  // Test Case 3: Create todo missing required title
  test('Create todo missing required title', async () => {
    const onSave = jest.fn();
    render(
      <TodoForm
        initial={{ title: '', description: '', notes: '', expiry_date: '' }}
        onSave={onSave}
      />
    );
    const { description, notes, expiry_date, saveBtn } = getFields();
    fireEvent.change(description, { target: { value: 'Any desc' } });
    fireEvent.change(notes, { target: { value: 'Any notes' } });
    fireEvent.change(expiry_date, { target: { value: '2024-07-01' } });
    fireEvent.click(saveBtn);

    await waitFor(() =>
      expect(screen.getByText(/title is required/i)).toBeInTheDocument()
    );
    expect(onSave).not.toHaveBeenCalled();
  });

  // Test Case 4: Create todo with title as only spaces
  test('Create todo with title as only spaces', async () => {
    const onSave = jest.fn();
    render(
      <TodoForm
        initial={{ title: '', description: '', notes: '', expiry_date: '' }}
        onSave={onSave}
      />
    );
    const { title, saveBtn } = getFields();
    fireEvent.change(title, { target: { value: '   ' } });
    fireEvent.click(saveBtn);

    await waitFor(() =>
      expect(screen.getByText(/title is required/i)).toBeInTheDocument()
    );
    expect(onSave).not.toHaveBeenCalled();
  });

  // Test Case 5: Create todo with invalid expiry_date format
  test('Create todo with invalid expiry_date format', async () => {
    const onSave = jest.fn();
    render(
      <TodoForm
        initial={{ title: '', description: '', notes: '', expiry_date: '' }}
        onSave={onSave}
      />
    );
    const { title, expiry_date, saveBtn } = getFields();
    fireEvent.change(title, { target: { value: 'Buy milk' } });
    fireEvent.change(expiry_date, { target: { value: '07/01/2024' } });
    fireEvent.click(saveBtn);

    await waitFor(() =>
      expect(screen.getByText(/expiry_date format is invalid/i)).toBeInTheDocument()
    );
    expect(onSave).not.toHaveBeenCalled();
  });

  // Test Case 6: Create todo with empty expiry_date field
  test('Create todo with empty expiry_date field', async () => {
    const onSave = jest.fn();
    render(
      <TodoForm
        initial={{ title: '', description: '', notes: '', expiry_date: '' }}
        onSave={onSave}
      />
    );
    const { title, expiry_date, saveBtn } = getFields();
    fireEvent.change(title, { target: { value: 'Finish report' } });
    fireEvent.change(expiry_date, { target: { value: '' } });
    fireEvent.click(saveBtn);

    await waitFor(() =>
      expect(onSave).toHaveBeenCalledWith({
        title: 'Finish report',
        description: '',
        notes: '',
        expiry_date: '',
      })
    );
    expect(screen.queryByText(/title is required/i)).not.toBeInTheDocument();
  });

  // Test Case 7: Update todo with some fields changed
  test('Update todo with some fields changed', async () => {
    const onSave = jest.fn();
    render(
      <TodoForm
        initial={{
          title: 'Old title',
          description: 'Old desc',
          notes: 'Old notes',
          expiry_date: '2024-07-01',
        }}
        onSave={onSave}
      />
    );
    const { notes, expiry_date, saveBtn } = getFields();
    fireEvent.change(notes, { target: { value: 'Updated notes' } });
    fireEvent.change(expiry_date, { target: { value: '2024-07-10' } });
    fireEvent.click(saveBtn);

    await waitFor(() =>
      expect(onSave).toHaveBeenCalledWith({
        title: 'Old title',
        description: 'Old desc',
        notes: 'Updated notes',
        expiry_date: '2024-07-10',
      })
    );
  });

  // Test Case 8: Update todo with invalid expiry_date format
  test('Update todo with invalid expiry_date format', async () => {
    const onSave = jest.fn();
    render(
      <TodoForm
        initial={{
          title: 'Old title',
          description: 'Old desc',
          notes: 'Old notes',
          expiry_date: '2024-07-01',
        }}
        onSave={onSave}
      />
    );
    const { expiry_date, saveBtn } = getFields();
    fireEvent.change(expiry_date, { target: { value: '2024-7-10' } });
    fireEvent.click(saveBtn);

    await waitFor(() =>
      expect(screen.getByText(/expiry_date format is invalid/i)).toBeInTheDocument()
    );
    expect(onSave).not.toHaveBeenCalled();
  });

  // Test Case 9: Update todo to remove optional fields
  test('Update todo to remove optional fields', async () => {
    const onSave = jest.fn();
    render(
      <TodoForm
        initial={{
          title: 'Keep title',
          description: 'Some desc',
          notes: 'Some notes',
          expiry_date: '2024-07-01',
        }}
        onSave={onSave}
      />
    );
    const { description, notes, expiry_date, saveBtn } = getFields();
    fireEvent.change(description, { target: { value: '' } });
    fireEvent.change(notes, { target: { value: '' } });
    fireEvent.change(expiry_date, { target: { value: '' } });
    fireEvent.click(saveBtn);

    await waitFor(() =>
      expect(onSave).toHaveBeenCalledWith({
        title: 'Keep title',
        description: '',
        notes: '',
        expiry_date: '',
      })
    );
  });

  // Test Case 10: Render form fields and labels correctly
  test('Render form fields and labels correctly', () => {
    render(
      <TodoForm
        initial={{ title: '', description: '', notes: '', expiry_date: '' }}
        onSave={jest.fn()}
      />
    );
    expect(screen.getByLabelText(/title/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/description/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/notes/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/expiry_date|expiry date/i)).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /submit|save/i })).toBeInTheDocument();
  });

  // Test Case 11: Submit button disabled when no title
  test('Submit button disabled when no title', () => {
    render(
      <TodoForm
        initial={{ title: '', description: '', notes: '', expiry_date: '' }}
        onSave={jest.fn()}
      />
    );
    const { title, saveBtn } = getFields();
    fireEvent.change(title, { target: { value: '' } });
    expect(saveBtn).toBeDisabled();
    fireEvent.change(title, { target: { value: 'Valid title' } });
    expect(saveBtn).not.toBeDisabled();
  });

  // Test Case 12: Handle max length for notes and description fields
  test('Handle max length for notes and description fields', async () => {
    const onSave = jest.fn();
    render(
      <TodoForm
        initial={{ title: '', description: '', notes: '', expiry_date: '' }}
        onSave={onSave}
      />
    );
    const { title, description, notes, expiry_date, saveBtn } = getFields();
    const longText = 'T'.repeat(1000);
    fireEvent.change(title, { target: { value: 'Valid title' } });
    fireEvent.change(description, { target: { value: longText } });
    fireEvent.change(notes, { target: { value: longText } });
    fireEvent.change(expiry_date, { target: { value: '2024-07-01' } });
    fireEvent.click(saveBtn);

    await waitFor(() =>
      expect(onSave).toHaveBeenCalledWith({
        title: 'Valid title',
        description: longText,
        notes: longText,
        expiry_date: '2024-07-01',
      })
    );
  });

  // Test Case 13: Create todo with valid leap year expiry_date
  test('Create todo with valid leap year expiry_date', async () => {
    const onSave = jest.fn();
    render(
      <TodoForm
        initial={{ title: '', description: '', notes: '', expiry_date: '' }}
        onSave={onSave}
      />
    );
    const { title, expiry_date, saveBtn } = getFields();
    fireEvent.change(title, { target: { value: 'Leap year task' } });
    fireEvent.change(expiry_date, { target: { value: '2024-02-29' } });
    fireEvent.click(saveBtn);

    await waitFor(() =>
      expect(onSave).toHaveBeenCalledWith({
        title: 'Leap year task',
        description: '',
        notes: '',
        expiry_date: '2024-02-29',
      })
    );
    expect(screen.queryByText(/title is required/i)).not.toBeInTheDocument();
  });

  // Test Case 14: Create todo with invalid expiry_date month or day
  test('Create todo with invalid expiry_date month or day', async () => {
    const onSave = jest.fn();
    render(
      <TodoForm
        initial={{ title: '', description: '', notes: '', expiry_date: '' }}
        onSave={onSave}
      />
    );
    const { title, expiry_date, saveBtn } = getFields();
    fireEvent.change(title, { target: { value: 'Invalid date task' } });
    fireEvent.change(expiry_date, { target: { value: '2024-13-01' } });
    fireEvent.click(saveBtn);

    await waitFor(() =>
      expect(screen.getByText(/invalid expiry_date/i)).toBeInTheDocument()
    );
    expect(onSave).not.toHaveBeenCalled();

    fireEvent.change(expiry_date, { target: { value: '2024-01-32' } });
    fireEvent.click(saveBtn);

    await waitFor(() =>
      expect(screen.getByText(/invalid expiry_date/i)).toBeInTheDocument()
    );
    expect(onSave).not.toHaveBeenCalled();
  });
});