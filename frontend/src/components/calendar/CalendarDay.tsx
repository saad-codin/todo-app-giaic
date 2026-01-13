'use client';

import { isToday, isSameMonth, isSameDay } from 'date-fns';
import { formatDayNumber } from '@/lib/utils/date';
import type { Task } from '@/types/task';

interface CalendarDayProps {
  date: Date;
  currentMonth: Date;
  selectedDate: Date | null;
  tasks: Task[];
  onClick: (date: Date) => void;
}

export function CalendarDay({
  date,
  currentMonth,
  selectedDate,
  tasks,
  onClick,
}: CalendarDayProps) {
  const isCurrentMonth = isSameMonth(date, currentMonth);
  const isSelected = selectedDate && isSameDay(date, selectedDate);
  const isTodayDate = isToday(date);

  const completedCount = tasks.filter((t) => t.completed).length;
  const totalCount = tasks.length;
  const progressPercent = totalCount > 0 ? Math.round((completedCount / totalCount) * 100) : 0;

  // Priority indicators
  const hasHighPriority = tasks.some((t) => t.priority === 'high' && !t.completed);
  const hasMediumPriority = tasks.some((t) => t.priority === 'medium' && !t.completed);

  return (
    <button
      onClick={() => onClick(date)}
      className={`
        min-h-[100px] p-2 border-b border-r border-gray-200 text-left transition-colors
        ${!isCurrentMonth ? 'bg-gray-50 text-gray-400' : 'bg-white hover:bg-gray-50'}
        ${isSelected ? 'ring-2 ring-blue-500 ring-inset' : ''}
      `}
    >
      {/* Date number */}
      <div className="flex items-center justify-between mb-1">
        <span
          className={`
            inline-flex items-center justify-center w-7 h-7 text-sm font-medium rounded-full
            ${isTodayDate ? 'bg-blue-600 text-white' : isCurrentMonth ? 'text-gray-900' : 'text-gray-400'}
          `}
        >
          {formatDayNumber(date)}
        </span>
        {totalCount > 0 && (
          <span className="text-xs text-gray-500">
            {completedCount}/{totalCount}
          </span>
        )}
      </div>

      {/* Task indicators */}
      {totalCount > 0 && (
        <div className="space-y-1">
          {/* Mini progress bar */}
          <div className="h-1 bg-gray-200 rounded-full overflow-hidden">
            <div
              className="h-full bg-green-500 rounded-full transition-all"
              style={{ width: `${progressPercent}%` }}
            />
          </div>

          {/* Priority dots */}
          <div className="flex gap-1">
            {hasHighPriority && (
              <span className="w-2 h-2 rounded-full bg-red-500" title="High priority" />
            )}
            {hasMediumPriority && (
              <span className="w-2 h-2 rounded-full bg-amber-500" title="Medium priority" />
            )}
          </div>

          {/* Task preview (first 2) */}
          <div className="space-y-0.5">
            {tasks.slice(0, 2).map((task) => (
              <div
                key={task.id}
                className={`text-xs truncate ${
                  task.completed ? 'text-gray-400 line-through' : 'text-gray-700'
                }`}
              >
                {task.description}
              </div>
            ))}
            {totalCount > 2 && (
              <div className="text-xs text-gray-500">
                +{totalCount - 2} more
              </div>
            )}
          </div>
        </div>
      )}
    </button>
  );
}
