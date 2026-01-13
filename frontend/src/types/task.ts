// Core entity types for Todo App Frontend Dashboard

export type Priority = 'high' | 'medium' | 'low';
export type Recurrence = 'none' | 'daily' | 'weekly' | 'monthly';

export interface User {
  id: string;
  email: string;
  name?: string;
  createdAt: string; // ISO 8601
}

export interface Task {
  id: string;
  userId: string;
  description: string;
  completed: boolean;
  priority: Priority;
  tags: string[];
  dueDate: string | null;      // ISO 8601 date (YYYY-MM-DD)
  dueTime: string | null;      // ISO 8601 time (HH:MM)
  reminderTime: string | null; // ISO 8601 datetime
  recurrence: Recurrence;
  createdAt: string;           // ISO 8601 datetime
  updatedAt: string;           // ISO 8601 datetime
}

export interface Tag {
  name: string;       // Normalized (lowercase, trimmed)
  count: number;      // Number of tasks with this tag
  color?: string;     // Optional color for display
}

// UI State Models
export interface AuthState {
  user: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;
}

export interface TaskFilters {
  search: string;
  status: 'all' | 'completed' | 'incomplete';
  priority: Priority | 'all';
  tag: string | null;
}

export interface TaskSort {
  field: 'dueDate' | 'priority' | 'alphabetical' | 'createdAt';
  direction: 'asc' | 'desc';
}

export interface TaskListState {
  tasks: Task[];
  filters: TaskFilters;
  sort: TaskSort;
  isLoading: boolean;
  error: string | null;
}

export type CalendarView = 'month' | 'week';

export interface CalendarState {
  view: CalendarView;
  currentDate: Date;           // Reference date for display
  selectedDate: Date | null;   // Date user clicked on
}

export interface DayTasks {
  date: string;               // YYYY-MM-DD
  tasks: Task[];
  completedCount: number;
  totalCount: number;
  progressPercent: number;
}

export interface SidebarState {
  isCollapsed: boolean;
  activeShortcut: string | null;
}

export type NotificationPermission = 'default' | 'granted' | 'denied';

export interface NotificationState {
  permission: NotificationPermission;
  scheduledReminders: Array<{
    taskId: string;
    reminderTime: string;
    timeoutId: number;
  }>;
}
