'use client';

import { motion, AnimatePresence } from 'framer-motion';
import { Plus } from 'lucide-react';
import { TaskCard } from './TaskCard';
import type { Task } from '@/types/task';

interface TaskListProps {
  tasks: Task[];
  isLoading?: boolean;
  onComplete: (id: string) => void;
  onIncomplete: (id: string) => void;
  onEdit: (task: Task) => void;
  onDelete: (id: string) => void;
  onTagClick?: (tag: string) => void;
  onAddTask?: () => void;
}

export function TaskList({
  tasks,
  isLoading,
  onComplete,
  onIncomplete,
  onEdit,
  onDelete,
  onTagClick,
  onAddTask,
}: TaskListProps) {
  if (isLoading) {
    return (
      <div className="space-y-3">
        {[1, 2, 3].map((i) => (
          <div
            key={i}
            className="bg-white dark:bg-gray-800 rounded-xl border border-gray-100 dark:border-gray-700 p-4 animate-pulse"
          >
            <div className="flex items-start gap-3">
              <div className="w-5 h-5 bg-gray-200 dark:bg-gray-700 rounded-full flex-shrink-0" />
              <div className="flex-1 space-y-2">
                <div className="h-4 bg-gray-200 dark:bg-gray-700 rounded w-3/4" />
                <div className="flex gap-2">
                  <div className="h-5 bg-gray-200 dark:bg-gray-700 rounded-full w-16" />
                  <div className="h-5 bg-gray-200 dark:bg-gray-700 rounded-full w-12" />
                </div>
              </div>
            </div>
          </div>
        ))}
      </div>
    );
  }

  if (tasks.length === 0) {
    return (
      <motion.div
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.3 }}
        className="text-center py-16"
      >
        <div className="inline-flex items-center justify-center w-16 h-16 rounded-2xl bg-gray-100 dark:bg-gray-800 mb-4">
          <svg
            className="w-8 h-8 text-gray-400 dark:text-gray-500"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={1.5}
              d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2"
            />
          </svg>
        </div>
        <h3 className="text-base font-semibold text-gray-900 dark:text-white mb-1">No tasks yet</h3>
        <p className="text-sm text-gray-500 dark:text-gray-400 mb-5">
          Create your first task to get started.
        </p>
        {onAddTask && (
          <motion.button
            whileHover={{ scale: 1.02 }}
            whileTap={{ scale: 0.98 }}
            onClick={onAddTask}
            className="inline-flex items-center gap-2 px-4 py-2 text-sm font-semibold text-white bg-sage-500 hover:bg-sage-600 rounded-xl transition-colors"
          >
            <Plus className="w-4 h-4" />
            Add your first task
          </motion.button>
        )}
      </motion.div>
    );
  }

  return (
    <motion.ul
      initial="hidden"
      animate="show"
      variants={{ show: { transition: { staggerChildren: 0.04 } } }}
      className="space-y-2"
    >
      <AnimatePresence mode="popLayout">
        {tasks.map((task) => (
          <motion.li
            key={task.id}
            variants={{
              hidden: { opacity: 0, y: 10 },
              show: { opacity: 1, y: 0, transition: { duration: 0.2 } },
            }}
            exit={{ opacity: 0, x: -20, transition: { duration: 0.15 } }}
            layout
          >
            <TaskCard
              task={task}
              onComplete={onComplete}
              onIncomplete={onIncomplete}
              onEdit={onEdit}
              onDelete={onDelete}
              onTagClick={onTagClick}
            />
          </motion.li>
        ))}
      </AnimatePresence>
    </motion.ul>
  );
}
