export interface Todo {
  id: number;
  title: string;
  description: string;
  notes: string;
  expiry_date: string | null;
}

export interface TodoCreate {
  title: string;
  description?: string;
  notes?: string;
  expiry_date?: string | null;
}

export interface TodoUpdate {
  title?: string;
  description?: string;
  notes?: string;
  expiry_date?: string | null;
}
