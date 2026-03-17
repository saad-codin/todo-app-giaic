'use client';

import { useState, useCallback } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Plus, X } from 'lucide-react';
import { useTasks } from '@/lib/hooks/useTasks';
import { useAuthContext } from '@/lib/auth';
import { useToast } from '@/components/ui/Toast';
import { TaskList } from '@/components/tasks/TaskList';
import { QuickAdd } from '@/components/tasks/QuickAdd';
import { TaskForm } from '@/components/tasks/TaskForm';
import { TaskFilters } from '@/components/tasks/TaskFilters';
import type { Task, TaskFilters as TaskFiltersType, TaskSort } from '@/types/task';
import type { TaskFormData } from '@/lib/utils/validation';

function getGreeting() {
  const hour = new Date().getHours();
  if (hour < 12) return 'Good morning';
  if (hour < 18) return 'Good afternoon';
  return 'Good evening';
}

function formatDate(date: Date) {
  return date.toLocaleDateString('en-US', { weekday: 'long', month: 'long', day: 'numeric' });
}

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

  const { user } = useAuthContext();
  const { addToast } = useToast();

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

  const firstName = user?.name?.split(' ')[0] || '';

  return (
    <div className="p-6 max-w-4xl mx-auto">
      {/* Greeting Header */}
      <div className="mb-6">
        <div className="flex items-start justify-between gap-4">
          <div>
            <h1 className="text-2xl font-bold text-gray-900 dark:text-white">
              {getGreeting()}{firstName ? `, ${firstName}` : ''}
            </h1>
            <p className="text-sm text-gray-500 dark:text-gray-400 mt-0.5">
              {formatDate(new Date())}
            </p>
          </div>

          <motion.button
            whileHover={{ scale: 1.02 }}
            whileTap={{ scale: 0.98 }}
            onClick={() => { setEditingTask(null); setIsFormOpen(true); }}
            className="flex-shrink-0 inline-flex items-center gap-2 px-4 py-2 text-sm font-semibold text-white bg-sage-500 hover:bg-sage-600 rounded-xl transition-colors shadow-sm shadow-sage-500/20"
          >
            <Plus className="w-4 h-4" />
            New Task
          </motion.button>
        </div>

        {/* Progress bar */}
        {totalCount > 0 && (
          <div className="mt-4">
            <div className="flex items-center justify-between mb-1.5">
              <span className="text-xs font-medium text-gray-500 dark:text-gray-400">
                {completedCount} of {totalCount} tasks completed
              </span>
              <span className="text-xs font-semibold text-sage-600 dark:text-sage-400">
                {progressPercent}%
              </span>
            </div>
            <div className="h-1.5 bg-gray-200 dark:bg-gray-700 rounded-full overflow-hidden">
              <motion.div
                className="h-full bg-sage-500 rounded-full"
                initial={{ width: 0 }}
                animate={{ width: `${progressPercent}%` }}
                transition={{ duration: 0.6, ease: 'easeOut' }}
              />
            </div>
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
        onAddTask={() => { setEditingTask(null); setIsFormOpen(true); }}
      />

      {/* Task Form Modal */}
      <AnimatePresence>
        {isFormOpen && (
          <>
            {/* Backdrop */}
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              transition={{ duration: 0.2 }}
              className="fixed inset-0 bg-black/50 dark:bg-black/70 z-50"
              onClick={handleFormCancel}
            />
            {/* Modal */}
            <motion.div
              initial={{ opacity: 0, scale: 0.95, y: 10 }}
              animate={{ opacity: 1, scale: 1, y: 0 }}
              exit={{ opacity: 0, scale: 0.95, y: 10 }}
              transition={{ duration: 0.2, ease: 'easeOut' }}
              className="fixed inset-0 z-50 flex items-center justify-center p-4 pointer-events-none"
            >
              <div
                className="bg-white dark:bg-gray-900 rounded-2xl shadow-2xl border border-gray-100 dark:border-gray-800 w-full max-w-lg pointer-events-auto"
                onClick={(e) => e.stopPropagation()}
              >
                <div className="flex items-center justify-between px-6 pt-5 pb-4 border-b border-gray-100 dark:border-gray-800">
                  <h2 className="text-lg font-bold text-gray-900 dark:text-white">
                    {editingTask ? 'Edit Task' : 'New Task'}
                  </h2>
                  <button
                    onClick={handleFormCancel}
                    className="p-1.5 rounded-lg text-gray-400 hover:text-gray-600 dark:hover:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors"
                    aria-label="Close"
                  >
                    <X className="w-4 h-4" />
                  </button>
                </div>
                <div className="p-6">
                  <TaskForm
                    task={editingTask || undefined}
                    onSubmit={handleFormSubmit}
                    onCancel={handleFormCancel}
                    isSubmitting={isCreating || isUpdating}
                  />
                </div>
              </div>
            </motion.div>
          </>
        )}
      </AnimatePresence>
    </div>
  );
}
