'use client';

import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Pencil, Trash2, Repeat } from 'lucide-react';
import type { Task } from '@/types/task';
import { PriorityBadge, TagBadge } from '@/components/ui/Badge';
import { getRelativeDate, formatTime, checkIsToday, checkIsOverdue } from '@/lib/utils/date';

interface TaskCardProps {
  task: Task;
  onComplete: (id: string) => void;
  onIncomplete: (id: string) => void;
  onEdit: (task: Task) => void;
  onDelete: (id: string) => void;
  onTagClick?: (tag: string) => void;
}

export function TaskCard({
  task,
  onComplete,
  onIncomplete,
  onEdit,
  onDelete,
  onTagClick,
}: TaskCardProps) {
  const [showDeleteConfirm, setShowDeleteConfirm] = useState(false);
  const [isCompleting, setIsCompleting] = useState(false);

  const isToday = checkIsToday(task.dueDate);
  const isOverdue = !task.completed && checkIsOverdue(task.dueDate);

  const handleToggleComplete = () => {
    setIsCompleting(true);
    setTimeout(() => {
      if (task.completed) {
        onIncomplete(task.id);
      } else {
        onComplete(task.id);
      }
      setIsCompleting(false);
    }, 300);
  };

  return (
    <motion.div
      whileHover={{ y: -1, boxShadow: '0 4px 12px rgba(0,0,0,0.06)' }}
      transition={{ duration: 0.15 }}
      animate={{ scale: isCompleting ? 1.01 : 1 }}
      className={`relative group bg-white dark:bg-gray-800 rounded-xl border p-4 transition-colors ${
        task.completed
          ? 'border-gray-100 dark:border-gray-700/50 opacity-75'
          : isOverdue
          ? 'border-red-200 dark:border-red-900/50'
          : 'border-gray-100 dark:border-gray-700'
      }`}
    >
      <div className="flex items-start gap-3">
        {/* Checkbox */}
        <motion.button
          whileTap={{ scale: 0.85 }}
          onClick={handleToggleComplete}
          className={`flex-shrink-0 w-5 h-5 mt-0.5 rounded-full border-2 transition-all flex items-center justify-center ${
            task.completed
              ? 'bg-sage-500 border-sage-500'
              : 'border-gray-300 dark:border-gray-600 hover:border-sage-400 dark:hover:border-sage-500'
          }`}
          aria-label={task.completed ? 'Mark incomplete' : 'Mark complete'}
        >
          {task.completed && (
            <motion.svg
              initial={{ scale: 0 }}
              animate={{ scale: 1 }}
              transition={{ duration: 0.15 }}
              className="w-3 h-3 text-white"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={3} d="M5 13l4 4L19 7" />
            </motion.svg>
          )}
        </motion.button>

        {/* Content */}
        <div className="flex-1 min-w-0">
          <motion.p
            animate={{ opacity: task.completed ? 0.45 : 1 }}
            className={`text-sm font-medium leading-snug ${
              task.completed
                ? 'text-gray-500 dark:text-gray-400 line-through'
                : 'text-gray-900 dark:text-white'
            }`}
          >
            {task.description}
          </motion.p>

          {/* Meta row */}
          <div className="flex flex-wrap items-center gap-1.5 mt-2">
            <PriorityBadge priority={task.priority} />

            {task.tags.map((tag) => (
              <TagBadge
                key={tag}
                tag={tag}
                onClick={onTagClick ? () => onTagClick(tag) : undefined}
              />
            ))}

            {task.dueDate && (
              <span
                className={`text-xs px-2 py-0.5 rounded-full font-medium ${
                  isOverdue
                    ? 'bg-red-50 dark:bg-red-900/20 text-red-600 dark:text-red-400'
                    : isToday
                    ? 'bg-sage-50 dark:bg-sage-900/20 text-sage-600 dark:text-sage-400'
                    : 'bg-gray-100 dark:bg-gray-700 text-gray-500 dark:text-gray-400'
                }`}
              >
                {getRelativeDate(task.dueDate)}
                {task.dueTime && ` · ${formatTime(task.dueTime)}`}
              </span>
            )}

            {task.recurrence !== 'none' && (
              <span className="flex items-center gap-0.5 text-xs text-gray-400 dark:text-gray-500">
                <Repeat className="w-3 h-3" />
                {task.recurrence}
              </span>
            )}
          </div>
        </div>

        {/* Action buttons — appear on hover */}
        <div className="flex items-center gap-1 opacity-0 group-hover:opacity-100 transition-opacity duration-150">
          <button
            onClick={() => onEdit(task)}
            className="p-1.5 text-gray-400 hover:text-gray-600 dark:hover:text-gray-300 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors"
            aria-label="Edit task"
          >
            <Pencil className="w-3.5 h-3.5" />
          </button>
          <button
            onClick={() => setShowDeleteConfirm(true)}
            className="p-1.5 text-gray-400 hover:text-red-500 dark:hover:text-red-400 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors"
            aria-label="Delete task"
          >
            <Trash2 className="w-3.5 h-3.5" />
          </button>
        </div>
      </div>

      {/* Delete confirmation overlay */}
      <AnimatePresence>
        {showDeleteConfirm && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            transition={{ duration: 0.15 }}
            className="absolute inset-0 bg-white/95 dark:bg-gray-800/95 backdrop-blur-sm rounded-xl border border-red-200 dark:border-red-900/50 flex flex-col items-center justify-center gap-3 z-10 p-4"
          >
            <p className="text-sm font-medium text-gray-900 dark:text-white">Delete this task?</p>
            <div className="flex gap-2">
              <button
                onClick={() => setShowDeleteConfirm(false)}
                className="px-3 py-1.5 text-xs font-medium text-gray-600 dark:text-gray-300 bg-gray-100 dark:bg-gray-700 hover:bg-gray-200 dark:hover:bg-gray-600 rounded-lg transition-colors"
              >
                Cancel
              </button>
              <button
                onClick={() => { onDelete(task.id); setShowDeleteConfirm(false); }}
                className="px-3 py-1.5 text-xs font-medium text-white bg-red-500 hover:bg-red-600 rounded-lg transition-colors"
              >
                Delete
              </button>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </motion.div>
  );
}
