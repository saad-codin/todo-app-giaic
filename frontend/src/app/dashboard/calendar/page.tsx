'use client';

import { useMemo } from 'react';
import { useCalendar } from '@/lib/hooks/useCalendar';
import { useTasks } from '@/lib/hooks/useTasks';
import { CalendarNav } from '@/components/calendar/CalendarNav';
import { CalendarGrid, DayDetail } from '@/components/calendar/CalendarGrid';
import { toApiDate } from '@/lib/utils/date';

export default function CalendarPage() {
  const {
    view,
    currentDate,
    selectedDate,
    days,
    dateRange,
    goToNext,
    goToPrev,
    goToToday,
    selectDate,
    toggleView,
  } = useCalendar();

  // Fetch tasks for the visible date range
  const { tasks, isLoading } = useTasks();

  // Filter tasks within the visible date range
  const visibleTasks = useMemo(() => {
    if (!tasks.length || !dateRange.startDate) return [];
    return tasks.filter((task) => {
      if (!task.dueDate) return false;
      return task.dueDate >= dateRange.startDate && task.dueDate <= dateRange.endDate;
    });
  }, [tasks, dateRange]);

  // Tasks for selected date
  const selectedDateTasks = useMemo(() => {
    if (!selectedDate) return [];
    const dateStr = toApiDate(selectedDate);
    return tasks.filter((task) => task.dueDate === dateStr);
  }, [selectedDate, tasks]);

  return (
    <div className="p-6">
      <div className="max-w-6xl mx-auto">
        <h1 className="text-2xl font-bold text-gray-900 mb-6">Calendar</h1>

        <CalendarNav
          currentDate={currentDate}
          view={view}
          onPrev={goToPrev}
          onNext={goToNext}
          onToday={goToToday}
          onToggleView={toggleView}
        />

        {isLoading ? (
          <div className="bg-white rounded-lg border border-gray-200 p-8 text-center">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto" />
            <p className="text-gray-500 mt-4">Loading calendar...</p>
          </div>
        ) : (
          <>
            <CalendarGrid
              days={days}
              currentDate={currentDate}
              selectedDate={selectedDate}
              view={view}
              tasks={visibleTasks}
              onSelectDate={selectDate}
            />

            {selectedDate && (
              <DayDetail
                date={selectedDate}
                tasks={selectedDateTasks}
                onClose={() => selectDate(selectedDate)} // Toggle off (same date click deselects)
              />
            )}
          </>
        )}
      </div>
    </div>
  );
}
