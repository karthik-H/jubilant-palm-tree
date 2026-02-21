import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import TodoForm from '../../../frontend/src/App';

// Helper to get input fields
function getFields() {
  return {
    title: screen.getByPlaceholderText('Todo title'),
    description: screen.getByPlaceholderText('Optional description'),
    notes: screen.getByPlaceholderText('Optional notes'),
    expiry_date: screen.getByLabelText('Expiry date'),
    saveBtn: screen.getByRole('button', { name: /save/i }),
    cancelBtn: screen.getByRole('button', { name: /cancel/i }),
  };
}

describe('TodoForm Component', () => {
  // Test Case 1: Render All Form Fields
  test('Render All Form Fields', () => {
    render(
      <TodoForm
        title="New todo"
        initial={{ title: '', description: '', notes: '', expiry_date: null }}
        onSave={jest.fn()}
        onCancel={jest.fn()}
      />
    );
    const { title, description, notes, expiry_date } = getFields();
    expect(title).toBeInTheDocument();
    expect(description).toBeInTheDocument();
    expect(notes).toBeInTheDocument();
    expect(expiry_date).toBeInTheDocument();
  });

  // Test Case 2: Submit Form with Empty Title
  test('Submit Form with Empty Title', async () => {
    const onSave = jest.fn();
    render(
      <TodoForm
        title="New todo"
        initial={{ title: '', description: '', notes: '', expiry_date: null }}
        onSave={onSave}
        onCancel={jest.fn()}
      />
    );
    const { saveBtn } = getFields();
    fireEvent.click(saveBtn);
    await waitFor(() =>
      expect(screen.getByText(/title.*required/i)).toBeInTheDocument()
    );
    expect(onSave).not.toHaveBeenCalled();
  });

  // Test Case 3: Submit Form with Only Title Filled
  test('Submit Form with Only Title Filled', async () => {
    const onSave = jest.fn();
    render(
      <TodoForm
        title="New todo"
        initial={{ title: '', description: '', notes: '', expiry_date: null }}
        onSave={onSave}
        onCancel={jest.fn()}
      />
    );
    const { title, saveBtn } = getFields();
    fireEvent.change(title, { target: { value: 'Buy milk' } });
    fireEvent.click(saveBtn);
    await waitFor(() =>
      expect(onSave).toHaveBeenCalledWith({
        title: 'Buy milk',
        description: null,
        notes: null,
        expiry_date: null,
      })
    );
  });

  // Test Case 4: Submit Form with All Fields Valid
  test('Submit Form with All Fields Valid', async () => {
    const onSave = jest.fn();
    render(
      <TodoForm
        title="New todo"
        initial={{ title: '', description: '', notes: '', expiry_date: null }}
        onSave={onSave}
        onCancel={jest.fn()}
      />
    );
    const { title, description, notes, expiry_date, saveBtn } = getFields();
    fireEvent.change(title, { target: { value: 'Task' } });
    fireEvent.change(description, { target: { value: 'Desc' } });
    fireEvent.change(notes, { target: { value: 'Notes' } });
    fireEvent.change(expiry_date, { target: { value: '2024-06-30' } });
    fireEvent.click(saveBtn);
    await waitFor(() =>
      expect(onSave).toHaveBeenCalledWith({
        title: 'Task',
        description: 'Desc',
        notes: 'Notes',
        expiry_date: '2024-06-30',
      })
    );
  });

  // Test Case 5: Submit Form with Invalid Expiry Date Format
  test('Submit Form with Invalid Expiry Date Format', async () => {
    const onSave = jest.fn();
    render(
      <TodoForm
        title="New todo"
        initial={{ title: '', description: '', notes: '', expiry_date: null }}
        onSave={onSave}
        onCancel={jest.fn()}
      />
    );
    const { title, expiry_date, saveBtn } = getFields();
    fireEvent.change(title, { target: { value: 'Task' } });
    fireEvent.change(expiry_date, { target: { value: '30/06/2024' } });
    fireEvent.click(saveBtn);
    await waitFor(() =>
      expect(screen.getByText(/expiry.*invalid/i)).toBeInTheDocument()
    );
    expect(onSave).not.toHaveBeenCalled();
  });

  // Test Case 6: Submit Form with Edge Case Expiry Date
  test('Submit Form with Edge Case Expiry Date', async () => {
    const onSave = jest.fn();
    render(
      <TodoForm
        title="New todo"
        initial={{ title: '', description: '', notes: '', expiry_date: null }}
        onSave={onSave}
        onCancel={jest.fn()}
      />
    );
    const { title, expiry_date, saveBtn } = getFields();
    fireEvent.change(title, { target: { value: 'Leap Year' } });
    fireEvent.change(expiry_date, { target: { value: '2024-02-29' } });
    fireEvent.click(saveBtn);
    await waitFor(() =>
      expect(onSave).toHaveBeenCalledWith({
        title: 'Leap Year',
        description: null,
        notes: null,
        expiry_date: '2024-02-29',
      })
    );
  });

  // Test Case 7: Submit Form with Empty Expiry Date
  test('Submit Form with Empty Expiry Date', async () => {
    const onSave = jest.fn();
    render(
      <TodoForm
        title="New todo"
        initial={{ title: '', description: '', notes: '', expiry_date: null }}
        onSave={onSave}
        onCancel={jest.fn()}
      />
    );
    const { title, expiry_date, saveBtn } = getFields();
    fireEvent.change(title, { target: { value: 'No Expiry' } });
    fireEvent.change(expiry_date, { target: { value: '' } });
    fireEvent.click(saveBtn);
    await waitFor(() =>
      expect(onSave).toHaveBeenCalledWith({
        title: 'No Expiry',
        description: null,
        notes: null,
        expiry_date: null,
      })
    );
  });

  // Test Case 8: Submit Form with Very Long Title
  test('Submit Form with Very Long Title', async () => {
    const onSave = jest.fn();
    const maxTitle = 'T'.repeat(255);
    render(
      <TodoForm
        title="New todo"
        initial={{ title: '', description: '', notes: '', expiry_date: null }}
        onSave={onSave}
        onCancel={jest.fn()}
      />
    );
    const { title, saveBtn } = getFields();
    fireEvent.change(title, { target: { value: maxTitle } });
    fireEvent.click(saveBtn);
    await waitFor(() =>
      expect(onSave).toHaveBeenCalledWith({
        title: maxTitle,
        description: null,
        notes: null,
        expiry_date: null,
      })
    );
  });

  // Test Case 9: Submit Form with Title of Only Whitespace
  test('Submit Form with Title of Only Whitespace', async () => {
    const onSave = jest.fn();
    render(
      <TodoForm
        title="New todo"
        initial={{ title: '', description: '', notes: '', expiry_date: null }}
        onSave={onSave}
        onCancel={jest.fn()}
      />
    );
    const { title, saveBtn } = getFields();
    fireEvent.change(title, { target: { value: '   ' } });
    fireEvent.click(saveBtn);
    await waitFor(() =>
      expect(screen.getByText(/title.*required/i)).toBeInTheDocument()
    );
    expect(onSave).not.toHaveBeenCalled();
  });

  // Test Case 10: Update Existing Todo with Partial Fields
  test('Update Existing Todo with Partial Fields', async () => {
    const onSave = jest.fn();
    render(
      <TodoForm
        title="Edit todo"
        initial={{
          title: 'Initial',
          description: 'Old',
          notes: 'Old',
          expiry_date: '2024-06-01',
        }}
        onSave={onSave}
        onCancel={jest.fn()}
      />
    );
    const { description, expiry_date, saveBtn } = getFields();
    fireEvent.change(description, { target: { value: 'New Desc' } });
    fireEvent.change(expiry_date, { target: { value: '2024-07-01' } });
    fireEvent.click(saveBtn);
    await waitFor(() =>
      expect(onSave).toHaveBeenCalledWith({
        title: 'Initial',
        description: 'New Desc',
        notes: 'Old',
        expiry_date: '2024-07-01',
      })
    );
  });

  // Test Case 11: Update Todo with Invalid Expiry Date
  test('Update Todo with Invalid Expiry Date', async () => {
    const onSave = jest.fn();
    render(
      <TodoForm
        title="Edit todo"
        initial={{
          title: 'Initial',
          description: 'Old',
          notes: 'Old',
          expiry_date: '2024-06-01',
        }}
        onSave={onSave}
        onCancel={jest.fn()}
      />
    );
    const { expiry_date, saveBtn } = getFields();
    fireEvent.change(expiry_date, { target: { value: '07-01-2024' } });
    fireEvent.click(saveBtn);
    await waitFor(() =>
      expect(screen.getByText(/expiry.*invalid/i)).toBeInTheDocument()
    );
    expect(onSave).not.toHaveBeenCalled();
  });

  // Test Case 12: Reset Form After Successful Submit
  test('Reset Form After Successful Submit', async () => {
    const onSave = jest.fn();
    render(
      <TodoForm
        title="New todo"
        initial={{ title: '', description: '', notes: '', expiry_date: null }}
        onSave={onSave}
        onCancel={jest.fn()}
      />
    );
    const { title, description, notes, expiry_date, saveBtn } = getFields();
    fireEvent.change(title, { target: { value: 'Task' } });
    fireEvent.change(description, { target: { value: 'Desc' } });
    fireEvent.change(notes, { target: { value: 'Notes' } });
    fireEvent.change(expiry_date, { target: { value: '2024-06-30' } });
    fireEvent.click(saveBtn);
    await waitFor(() =>
      expect(onSave).toHaveBeenCalled()
    );
    // After submit, fields should be reset
    expect(title).toHaveValue('');
    expect(description).toHaveValue('');
    expect(notes).toHaveValue('');
    expect(expiry_date).toHaveValue('');
  });

  // Test Case 13: Notes Field Optional
  test('Notes Field Optional', async () => {
    const onSave = jest.fn();
    render(
      <TodoForm
        title="New todo"
        initial={{ title: '', description: '', notes: '', expiry_date: null }}
        onSave={onSave}
        onCancel={jest.fn()}
      />
    );
    const { title, description, notes, saveBtn } = getFields();
    fireEvent.change(title, { target: { value: 'Task' } });
    fireEvent.change(description, { target: { value: 'Desc' } });
    fireEvent.change(notes, { target: { value: '' } });
    fireEvent.click(saveBtn);
    await waitFor(() =>
      expect(onSave).toHaveBeenCalledWith({
        title: 'Task',
        description: 'Desc',
        notes: null,
        expiry_date: null,
      })
    );
  });

  // Test Case 14: Description Field Optional
  test('Description Field Optional', async () => {
    const onSave = jest.fn();
    render(
      <TodoForm
        title="New todo"
        initial={{ title: '', description: '', notes: '', expiry_date: null }}
        onSave={onSave}
        onCancel={jest.fn()}
      />
    );
    const { title, notes, description, saveBtn } = getFields();
    fireEvent.change(title, { target: { value: 'Task' } });
    fireEvent.change(notes, { target: { value: 'Notes' } });
    fireEvent.change(description, { target: { value: '' } });
    fireEvent.click(saveBtn);
    await waitFor(() =>
      expect(onSave).toHaveBeenCalledWith({
        title: 'Task',
        description: null,
        notes: 'Notes',
        expiry_date: null,
      })
    );
  });

  // Test Case 15: Submit Form with Expiry Date Containing Invalid Characters
  test('Submit Form with Expiry Date Containing Invalid Characters', async () => {
    const onSave = jest.fn();
    render(
      <TodoForm
        title="New todo"
        initial={{ title: '', description: '', notes: '', expiry_date: null }}
        onSave={onSave}
        onCancel={jest.fn()}
      />
    );
    const { title, expiry_date, saveBtn } = getFields();
    fireEvent.change(title, { target: { value: 'Task' } });
    fireEvent.change(expiry_date, { target: { value: '2024-06-aa' } });
    fireEvent.click(saveBtn);
    await waitFor(() =>
      expect(screen.getByText(/expiry.*invalid/i)).toBeInTheDocument()
    );
    expect(onSave).not.toHaveBeenCalled();
  });

  // Test Case 16: Submit Form with Expiry Date Month Overflow
  test('Submit Form with Expiry Date Month Overflow', async () => {
    const onSave = jest.fn();
    render(
      <TodoForm
        title="New todo"
        initial={{ title: '', description: '', notes: '', expiry_date: null }}
        onSave={onSave}
        onCancel={jest.fn()}
      />
    );
    const { title, expiry_date, saveBtn } = getFields();
    fireEvent.change(title, { target: { value: 'Task' } });
    fireEvent.change(expiry_date, { target: { value: '2024-13-01' } });
    fireEvent.click(saveBtn);
    await waitFor(() =>
      expect(screen.getByText(/expiry.*invalid/i)).toBeInTheDocument()
    );
    expect(onSave).not.toHaveBeenCalled();
  });

  // Test Case 17: Submit Form with Expiry Date Day Underflow
  test('Submit Form with Expiry Date Day Underflow', async () => {
    const onSave = jest.fn();
    render(
      <TodoForm
        title="New todo"
        initial={{ title: '', description: '', notes: '', expiry_date: null }}
        onSave={onSave}
        onCancel={jest.fn()}
      />
    );
    const { title, expiry_date, saveBtn } = getFields();
    fireEvent.change(title, { target: { value: 'Task' } });
    fireEvent.change(expiry_date, { target: { value: '2024-06-00' } });
    fireEvent.click(saveBtn);
    await waitFor(() =>
      expect(screen.getByText(/expiry.*invalid/i)).toBeInTheDocument()
    );
    expect(onSave).not.toHaveBeenCalled();
  });

  // Test Case 18: Submit Form with Expiry Date Leading/Trailing Whitespace
  test('Submit Form with Expiry Date Leading/Trailing Whitespace', async () => {
    const onSave = jest.fn();
    render(
      <TodoForm
        title="New todo"
        initial={{ title: '', description: '', notes: '', expiry_date: null }}
        onSave={onSave}
        onCancel={jest.fn()}
      />
    );
    const { title, expiry_date, saveBtn } = getFields();
    fireEvent.change(title, { target: { value: 'Task' } });
    fireEvent.change(expiry_date, { target: { value: ' 2024-06-01 ' } });
    fireEvent.click(saveBtn);
    await waitFor(() =>
      expect(screen.getByText(/expiry.*invalid/i)).toBeInTheDocument()
    );
    expect(onSave).not.toHaveBeenCalled();
  });
});