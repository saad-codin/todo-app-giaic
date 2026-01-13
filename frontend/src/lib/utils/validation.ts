import { z } from 'zod';

// Task validation schema
export const taskSchema = z.object({
  description: z.string().min(1, 'Description is required').max(500, 'Description too long'),
  priority: z.enum(['high', 'medium', 'low']).default('medium'),
  tags: z.array(z.string().min(1).max(50)).max(10).default([]),
  dueDate: z.string().nullable().optional(),
  dueTime: z.string().nullable().optional(),
  reminderTime: z.string().nullable().optional(),
  recurrence: z.enum(['none', 'daily', 'weekly', 'monthly']).default('none'),
});

export type TaskFormData = z.infer<typeof taskSchema>;

// Sign up validation schema
export const signUpSchema = z.object({
  email: z.string().email('Invalid email address'),
  password: z.string().min(8, 'Password must be at least 8 characters').max(100),
  name: z.string().min(1, 'Name is required').max(100).optional(),
});

export type SignUpFormData = z.infer<typeof signUpSchema>;

// Sign in validation schema
export const signInSchema = z.object({
  email: z.string().email('Invalid email address'),
  password: z.string().min(1, 'Password is required'),
});

export type SignInFormData = z.infer<typeof signInSchema>;

// Update task validation schema (partial)
export const updateTaskSchema = taskSchema.partial().extend({
  completed: z.boolean().optional(),
});

export type UpdateTaskFormData = z.infer<typeof updateTaskSchema>;

// Filter validation
export const taskFiltersSchema = z.object({
  search: z.string().default(''),
  status: z.enum(['all', 'completed', 'incomplete']).default('all'),
  priority: z.enum(['high', 'medium', 'low', 'all']).default('all'),
  tag: z.string().nullable().default(null),
});

export type TaskFiltersFormData = z.infer<typeof taskFiltersSchema>;

// Sort validation
export const taskSortSchema = z.object({
  field: z.enum(['dueDate', 'priority', 'alphabetical', 'createdAt']).default('createdAt'),
  direction: z.enum(['asc', 'desc']).default('desc'),
});

export type TaskSortFormData = z.infer<typeof taskSortSchema>;
