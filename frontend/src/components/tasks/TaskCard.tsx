'use client';

import { useState } from 'react';
import type { Task } from '@/types/task';
import { PriorityBadge, TagBadge } from '@/components/ui/Badge';
import { Button } from '@/components/ui/Button';
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

  const isToday = checkIsToday(task.dueDate);
  const isOverdue = !task.completed && checkIsOverdue(task.dueDate);

  const handleToggleComplete = () => {
    if (task.completed) {
      onIncomplete(task.id);
    } else {
      onComplete(task.id);
    }
  };

  const handleDelete = () => {
    setShowDeleteConfirm(true);
  };

  const confirmDelete = () => {
    onDelete(task.id);
    setShowDeleteConfirm(false);
  };

  return (
    <div
      className={`relative bg-white rounded-lg border p-4 transition-all ${
        task.completed ? 'border-gray-200 bg-gray-50' : 'border-gray-200 hover:border-gray-300'
      }`}
    >
      <div className="flex items-start gap-3">
        {/* Checkbox */}
        <button
          onClick={handleToggleComplete}
          className={`flex-shrink-0 w-5 h-5 mt-0.5 rounded border-2 transition-colors ${
            task.completed
              ? 'bg-green-500 border-green-500 text-white'
              : 'border-gray-300 hover:border-gray-400'
          }`}
          aria-label={task.completed ? 'Mark incomplete' : 'Mark complete'}
        >
          {task.completed && (
            <svg className="w-full h-full" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={3} d="M5 13l4 4L19 7" />
            </svg>
          )}
        </button>

        {/* Content */}
        <div className="flex-1 min-w-0">
          <p
            className={`text-sm font-medium ${
              task.completed ? 'text-gray-500 line-through' : 'text-gray-900'
            }`}
          >
            {task.description}
          </p>

          {/* Meta row */}
          <div className="flex flex-wrap items-center gap-2 mt-2">
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
                className={`text-xs ${
                  isOverdue
                    ? 'text-red-600 font-medium'
                    : isToday
                    ? 'text-blue-600 font-medium'
                    : 'text-gray-500'
                }`}
              >
                {getRelativeDate(task.dueDate)}
                {task.dueTime && ` at ${formatTime(task.dueTime)}`}
              </span>
            )}

            {task.recurrence !== 'none' && (
              <span className="text-xs text-gray-500 flex items-center gap-1">
                <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
                </svg>
                {task.recurrence}
              </span>
            )}
          </div>
        </div>

        {/* Actions */}
        <div className="flex items-center gap-1">
          <button
            onClick={() => onEdit(task)}
            className="p-1.5 text-gray-400 hover:text-gray-600 rounded hover:bg-gray-100 transition-colors"
            aria-label="Edit task"
          >
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
            </svg>
          </button>
          <button
            onClick={handleDelete}
            className="p-1.5 text-gray-400 hover:text-red-600 rounded hover:bg-gray-100 transition-colors"
            aria-label="Delete task"
          >
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
            </svg>
          </button>
        </div>
      </div>

      {/* Delete confirmation dialog */}
      {showDeleteConfirm && (
        <div className="absolute inset-0 bg-white rounded-lg border border-red-200 p-4 flex flex-col items-center justify-center gap-3">
          <p className="text-sm text-gray-700">Delete this task?</p>
          <div className="flex gap-2">
            <Button variant="ghost" size="sm" onClick={() => setShowDeleteConfirm(false)}>
              Cancel
            </Button>
            <Button variant="danger" size="sm" onClick={confirmDelete}>
              Delete
            </Button>
          </div>
        </div>
      )}
    </div>
  );
}
