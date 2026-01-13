// API Request and Response types for Todo App Frontend Dashboard

import { User, Task, Priority, Recurrence } from './task';

// Authentication
export interface SignUpRequest {
  email: string;
  password: string;
  name?: string;
}

export interface SignInRequest {
  email: string;
  password: string;
}

export interface AuthResponse {
  user: User;
}

export interface AuthError {
  code: string;
  message: string;
}

// Task CRUD
export interface CreateTaskRequest {
  description: string;
  priority?: Priority;
  tags?: string[];
  dueDate?: string;
  dueTime?: string;
  reminderTime?: string;
  recurrence?: Recurrence;
}

export interface CreateTaskResponse {
  task: Task;
}

export interface UpdateTaskRequest {
  description?: string;
  completed?: boolean;
  priority?: Priority;
  tags?: string[];
  dueDate?: string | null;
  dueTime?: string | null;
  reminderTime?: string | null;
  recurrence?: Recurrence;
}

export interface UpdateTaskResponse {
  task: Task;
}

export interface ListTasksRequest {
  search?: string;
  completed?: boolean;
  priority?: Priority;
  tag?: string;
  startDate?: string;
  endDate?: string;
  sortBy?: 'dueDate' | 'priority' | 'createdAt';
  sortOrder?: 'asc' | 'desc';
  limit?: number;
  offset?: number;
}

export interface ListTasksResponse {
  tasks: Task[];
  total: number;
  hasMore: boolean;
}

export interface CompleteTaskResponse {
  task: Task;
  nextOccurrence: Task | null;
}

// Error Response
export interface ApiErrorResponse {
  code: string;
  message: string;
  details?: {
    field?: string;
    constraint?: string;
  };
}

// API Error class
export class ApiError extends Error {
  constructor(
    public status: number,
    message: string,
    public code?: string
  ) {
    super(message);
    this.name = 'ApiError';
  }
}
