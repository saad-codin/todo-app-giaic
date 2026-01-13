'use client';

import { useState, useCallback } from 'react';
import { useTasks } from '@/lib/hooks/useTasks';
import { TaskList } from '@/components/tasks/TaskList';
import { QuickAdd } from '@/components/tasks/QuickAdd';
import { TaskForm } from '@/components/tasks/TaskForm';
import { TaskFilters } from '@/components/tasks/TaskFilters';
import type { Task, TaskFilters as TaskFiltersType, TaskSort } from '@/types/task';
import type { TaskFormData } from '@/lib/utils/validation';

export default function DashboardPage() {
  const [filters, setFilters] = useState<TaskFiltersType>({
    search: '',
    status: 'all',
    priority: 'all',
    tag: null,
  });
  const [sort, setSort] = useState<TaskSort>({
    field: 'createdAt',
    direction: 'desc',
  });
  const [editingTask, setEditingTask] = useState<Task | null>(null);
  const [isFormOpen, setIsFormOpen] = useState(false);

  const {
    tasks,
    isLoading,
    createTask,
    updateTask,
    deleteTask,
    completeTask,
    incompleteTask,
    isCreating,
    isUpdating,
  } = useTasks(filters, sort);

  const handleQuickAdd = (description: string) => {
    createTask({ description });
  };

  const handleEdit = (task: Task) => {
    setEditingTask(task);
    setIsFormOpen(true);
  };

  const handleFormSubmit = (data: TaskFormData) => {
    // Transform empty strings to null/undefined for API
    const dueDate = data.dueDate && data.dueDate !== '' ? data.dueDate : null;
    const dueTime = data.dueTime && data.dueTime !== '' ? data.dueTime : null;

    if (editingTask) {
      updateTask(editingTask.id, {
        description: data.description,
        priority: data.priority,
        tags: data.tags,
        dueDate,
        dueTime,
        recurrence: data.recurrence,
      });
    } else {
      createTask({
        description: data.description,
        priority: data.priority,
        tags: data.tags,
        dueDate: dueDate || undefined,
        dueTime: dueTime || undefined,
        recurrence: data.recurrence,
      });
    }
    setIsFormOpen(false);
    setEditingTask(null);
  };

  const handleFormCancel = () => {
    setIsFormOpen(false);
    setEditingTask(null);
  };

  const handleTagClick = useCallback((tag: string) => {
    setFilters((prev) => ({ ...prev, tag }));
  }, []);

  const completedCount = tasks.filter((t) => t.completed).length;
  const totalCount = tasks.length;
  const progressPercent = totalCount > 0 ? Math.round((completedCount / totalCount) * 100) : 0;

  return (
    <div className="p-6 max-w-4xl mx-auto">
      {/* Header */}
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-gray-900">Dashboard</h1>
        <p className="text-gray-600 mt-1">
          {totalCount > 0
            ? `${completedCount} of ${totalCount} tasks completed (${progressPercent}%)`
            : 'No tasks yet. Add one below!'}
        </p>

        {/* Progress bar */}
        {totalCount > 0 && (
          <div className="mt-4 h-2 bg-gray-200 rounded-full overflow-hidden">
            <div
              className="h-full bg-green-500 rounded-full transition-all duration-300"
              style={{ width: `${progressPercent}%` }}
            />
          </div>
        )}
      </div>

      {/* Quick Add */}
      <div className="mb-4">
        <QuickAdd onAdd={handleQuickAdd} isLoading={isCreating} />
      </div>

      {/* Filters */}
      <TaskFilters
        filters={filters}
        sort={sort}
        tasks={tasks}
        onFiltersChange={setFilters}
        onSortChange={setSort}
      />

      {/* Task List */}
      <TaskList
        tasks={tasks}
        isLoading={isLoading}
        onComplete={completeTask}
        onIncomplete={incompleteTask}
        onEdit={handleEdit}
        onDelete={deleteTask}
        onTagClick={handleTagClick}
      />

      {/* Task Form Modal */}
      {isFormOpen && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-xl shadow-xl max-w-lg w-full p-6">
            <h2 className="text-xl font-bold text-gray-900 mb-4">
              {editingTask ? 'Edit Task' : 'Create Task'}
            </h2>
            <TaskForm
              task={editingTask || undefined}
              onSubmit={handleFormSubmit}
              onCancel={handleFormCancel}
              isSubmitting={isCreating || isUpdating}
            />
          </div>
        </div>
      )}
    </div>
  );
}
