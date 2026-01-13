'use client';

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { api } from '@/lib/api';
import { useToast } from '@/components/ui/Toast';
import type { Task, TaskFilters, TaskSort } from '@/types/task';
import type { CreateTaskRequest, UpdateTaskRequest, ListTasksRequest, ListTasksResponse } from '@/types/api';

const TASKS_QUERY_KEY = ['tasks'];

export function useTasks(filters?: TaskFilters, sort?: TaskSort) {
  const queryClient = useQueryClient();
  const { addToast } = useToast();

  // Build query params from filters
  const queryParams: ListTasksRequest = {};
  if (filters) {
    if (filters.search) queryParams.search = filters.search;
    if (filters.status === 'completed') queryParams.completed = true;
    if (filters.status === 'incomplete') queryParams.completed = false;
    if (filters.priority && filters.priority !== 'all') queryParams.priority = filters.priority;
    if (filters.tag) queryParams.tag = filters.tag;
  }
  if (sort) {
    if (sort.field !== 'alphabetical') {
      queryParams.sortBy = sort.field;
    }
    queryParams.sortOrder = sort.direction;
  }

  // Fetch tasks
  const tasksQuery = useQuery({
    queryKey: [...TASKS_QUERY_KEY, queryParams],
    queryFn: () => api.getTasks(queryParams),
  });

  // Create task mutation
  const createTaskMutation = useMutation({
    mutationFn: (data: CreateTaskRequest) => api.createTask(data),
    onMutate: async (newTask) => {
      const queryKey = [...TASKS_QUERY_KEY, queryParams];
      await queryClient.cancelQueries({ queryKey });
      const previousTasks = queryClient.getQueryData<ListTasksResponse>(queryKey);

      // Optimistic update
      queryClient.setQueryData(queryKey, (old: ListTasksResponse | undefined) => {
        if (!old) return { tasks: [], total: 1, hasMore: false };
        const optimisticTask: Task = {
          id: `temp-${Date.now()}`,
          userId: '',
          description: newTask.description,
          completed: false,
          priority: newTask.priority || 'medium',
          tags: newTask.tags || [],
          dueDate: newTask.dueDate || null,
          dueTime: newTask.dueTime || null,
          reminderTime: newTask.reminderTime || null,
          recurrence: newTask.recurrence || 'none',
          createdAt: new Date().toISOString(),
          updatedAt: new Date().toISOString(),
        };
        return {
          ...old,
          tasks: [optimisticTask, ...old.tasks],
          total: old.total + 1,
        };
      });

      return { previousTasks, queryKey };
    },
    onError: (err, _newTask, context) => {
      if (context?.queryKey) {
        queryClient.setQueryData(context.queryKey, context.previousTasks);
      }
      addToast('error', 'Failed to create task. Please try again.');
    },
    onSuccess: () => {
      addToast('success', 'Task created successfully!');
    },
    onSettled: () => {
      queryClient.invalidateQueries({ queryKey: TASKS_QUERY_KEY });
    },
  });

  // Update task mutation
  const updateTaskMutation = useMutation({
    mutationFn: ({ id, data }: { id: string; data: UpdateTaskRequest }) =>
      api.updateTask(id, data),
    onMutate: async ({ id, data }) => {
      const queryKey = [...TASKS_QUERY_KEY, queryParams];
      await queryClient.cancelQueries({ queryKey });
      const previousTasks = queryClient.getQueryData<ListTasksResponse>(queryKey);

      queryClient.setQueryData(queryKey, (old: ListTasksResponse | undefined) => {
        if (!old) return old;
        return {
          ...old,
          tasks: old.tasks.map((task) =>
            task.id === id ? { ...task, ...data, updatedAt: new Date().toISOString() } : task
          ),
        };
      });

      return { previousTasks, queryKey };
    },
    onError: (err, _vars, context) => {
      if (context?.queryKey) {
        queryClient.setQueryData(context.queryKey, context.previousTasks);
      }
      addToast('error', 'Failed to update task. Please try again.');
    },
    onSuccess: () => {
      addToast('success', 'Task updated successfully!');
    },
    onSettled: () => {
      queryClient.invalidateQueries({ queryKey: TASKS_QUERY_KEY });
    },
  });

  // Delete task mutation
  const deleteTaskMutation = useMutation({
    mutationFn: (id: string) => api.deleteTask(id),
    onMutate: async (id) => {
      const queryKey = [...TASKS_QUERY_KEY, queryParams];
      await queryClient.cancelQueries({ queryKey });
      const previousTasks = queryClient.getQueryData<ListTasksResponse>(queryKey);

      queryClient.setQueryData(queryKey, (old: ListTasksResponse | undefined) => {
        if (!old) return old;
        return {
          ...old,
          tasks: old.tasks.filter((task) => task.id !== id),
          total: old.total - 1,
        };
      });

      return { previousTasks, queryKey };
    },
    onError: (err, _id, context) => {
      if (context?.queryKey) {
        queryClient.setQueryData(context.queryKey, context.previousTasks);
      }
      addToast('error', 'Failed to delete task. Please try again.');
    },
    onSuccess: () => {
      addToast('success', 'Task deleted successfully!');
    },
    onSettled: () => {
      queryClient.invalidateQueries({ queryKey: TASKS_QUERY_KEY });
    },
  });

  // Complete task mutation (handles recurring tasks)
  const completeTaskMutation = useMutation({
    mutationFn: (id: string) => api.completeTask(id),
    onMutate: async (id) => {
      const queryKey = [...TASKS_QUERY_KEY, queryParams];
      await queryClient.cancelQueries({ queryKey });
      const previousTasks = queryClient.getQueryData<ListTasksResponse>(queryKey);

      queryClient.setQueryData(queryKey, (old: ListTasksResponse | undefined) => {
        if (!old) return old;
        return {
          ...old,
          tasks: old.tasks.map((task) =>
            task.id === id ? { ...task, completed: true, updatedAt: new Date().toISOString() } : task
          ),
        };
      });

      return { previousTasks, queryKey };
    },
    onError: (err, _id, context) => {
      if (context?.queryKey) {
        queryClient.setQueryData(context.queryKey, context.previousTasks);
      }
      addToast('error', 'Failed to complete task. Please try again.');
    },
    onSuccess: (data) => {
      if (data.nextOccurrence) {
        addToast('success', 'Task completed! Next occurrence created.');
      } else {
        addToast('success', 'Task completed!');
      }
    },
    onSettled: () => {
      queryClient.invalidateQueries({ queryKey: TASKS_QUERY_KEY });
    },
  });

  // Incomplete task mutation
  const incompleteTaskMutation = useMutation({
    mutationFn: (id: string) => api.incompleteTask(id),
    onMutate: async (id) => {
      const queryKey = [...TASKS_QUERY_KEY, queryParams];
      await queryClient.cancelQueries({ queryKey });
      const previousTasks = queryClient.getQueryData<ListTasksResponse>(queryKey);

      queryClient.setQueryData(queryKey, (old: ListTasksResponse | undefined) => {
        if (!old) return old;
        return {
          ...old,
          tasks: old.tasks.map((task) =>
            task.id === id ? { ...task, completed: false, updatedAt: new Date().toISOString() } : task
          ),
        };
      });

      return { previousTasks, queryKey };
    },
    onError: (err, _id, context) => {
      if (context?.queryKey) {
        queryClient.setQueryData(context.queryKey, context.previousTasks);
      }
      addToast('error', 'Failed to update task. Please try again.');
    },
    onSettled: () => {
      queryClient.invalidateQueries({ queryKey: TASKS_QUERY_KEY });
    },
  });

  return {
    tasks: tasksQuery.data?.tasks || [],
    total: tasksQuery.data?.total || 0,
    isLoading: tasksQuery.isLoading,
    error: tasksQuery.error,
    refetch: tasksQuery.refetch,
    createTask: createTaskMutation.mutate,
    updateTask: (id: string, data: UpdateTaskRequest) =>
      updateTaskMutation.mutate({ id, data }),
    deleteTask: deleteTaskMutation.mutate,
    completeTask: completeTaskMutation.mutate,
    incompleteTask: incompleteTaskMutation.mutate,
    isCreating: createTaskMutation.isPending,
    isUpdating: updateTaskMutation.isPending,
    isDeleting: deleteTaskMutation.isPending,
  };
}
