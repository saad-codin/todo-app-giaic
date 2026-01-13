'use client';

import { useMemo } from 'react';
import { format, isSameDay } from 'date-fns';
import { CalendarDay } from './CalendarDay';
import { toApiDate, getDayName } from '@/lib/utils/date';
import type { Task, CalendarView } from '@/types/task';

interface CalendarGridProps {
  days: Date[];
  currentDate: Date;
  selectedDate: Date | null;
  view: CalendarView;
  tasks: Task[];
  onSelectDate: (date: Date) => void;
}

const WEEKDAY_NAMES = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'];

export function CalendarGrid({
  days,
  currentDate,
  selectedDate,
  view,
  tasks,
  onSelectDate,
}: CalendarGridProps) {
  // Group tasks by date
  const tasksByDate = useMemo(() => {
    const map = new Map<string, Task[]>();
    tasks.forEach((task) => {
      if (task.dueDate) {
        const existing = map.get(task.dueDate) || [];
        map.set(task.dueDate, [...existing, task]);
      }
    });
    return map;
  }, [tasks]);

  const getTasksForDate = (date: Date): Task[] => {
    return tasksByDate.get(toApiDate(date)) || [];
  };

  return (
    <div className="bg-white rounded-lg border border-gray-200 overflow-hidden">
      {/* Weekday headers */}
      <div className="grid grid-cols-7 border-b border-gray-200">
        {WEEKDAY_NAMES.map((name) => (
          <div
            key={name}
            className="px-2 py-3 text-center text-sm font-medium text-gray-500 bg-gray-50"
          >
            {name}
          </div>
        ))}
      </div>

      {/* Calendar days */}
      <div className={`grid grid-cols-7 ${view === 'week' ? '' : ''}`}>
        {days.map((date) => (
          <CalendarDay
            key={date.toISOString()}
            date={date}
            currentMonth={currentDate}
            selectedDate={selectedDate}
            tasks={getTasksForDate(date)}
            onClick={onSelectDate}
          />
        ))}
      </div>
    </div>
  );
}

// Selected day detail panel
interface DayDetailProps {
  date: Date;
  tasks: Task[];
  onClose: () => void;
}

export function DayDetail({ date, tasks, onClose }: DayDetailProps) {
  const completedCount = tasks.filter((t) => t.completed).length;

  return (
    <div className="bg-white rounded-lg border border-gray-200 p-4 mt-4">
      <div className="flex items-center justify-between mb-4">
        <div>
          <h3 className="text-lg font-semibold text-gray-900">
            {format(date, 'EEEE, MMMM d, yyyy')}
          </h3>
          <p className="text-sm text-gray-500">
            {tasks.length === 0
              ? 'No tasks'
              : `${completedCount}/${tasks.length} tasks completed`}
          </p>
        </div>
        <button
          onClick={onClose}
          className="p-2 rounded-lg hover:bg-gray-100 transition-colors"
          aria-label="Close"
        >
          <svg className="w-5 h-5 text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>
      </div>

      {tasks.length === 0 ? (
        <p className="text-gray-500 text-center py-8">No tasks scheduled for this day</p>
      ) : (
        <div className="space-y-2">
          {tasks.map((task) => (
            <div
              key={task.id}
              className={`p-3 rounded-lg border ${
                task.completed
                  ? 'bg-gray-50 border-gray-200'
                  : 'bg-white border-gray-200'
              }`}
            >
              <div className="flex items-start gap-3">
                <div
                  className={`w-4 h-4 mt-0.5 rounded border-2 flex-shrink-0 ${
                    task.completed
                      ? 'bg-green-500 border-green-500'
                      : 'border-gray-300'
                  }`}
                >
                  {task.completed && (
                    <svg className="w-full h-full text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={3} d="M5 13l4 4L19 7" />
                    </svg>
                  )}
                </div>
                <div className="flex-1 min-w-0">
                  <p className={`text-sm ${task.completed ? 'text-gray-500 line-through' : 'text-gray-900'}`}>
                    {task.description}
                  </p>
                  <div className="flex items-center gap-2 mt-1">
                    <span
                      className={`text-xs px-1.5 py-0.5 rounded ${
                        task.priority === 'high'
                          ? 'bg-red-100 text-red-700'
                          : task.priority === 'medium'
                          ? 'bg-amber-100 text-amber-700'
                          : 'bg-green-100 text-green-700'
                      }`}
                    >
                      {task.priority}
                    </span>
                    {task.dueTime && (
                      <span className="text-xs text-gray-500">{task.dueTime}</span>
                    )}
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
