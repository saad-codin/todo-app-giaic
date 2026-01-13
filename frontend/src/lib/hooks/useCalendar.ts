'use client';

import { useState, useCallback, useMemo } from 'react';
import {
  getMonthDays,
  getWeekDays,
  goToNextMonth,
  goToPrevMonth,
  goToNextWeek,
  goToPrevWeek,
  toApiDate,
} from '@/lib/utils/date';
import type { CalendarView } from '@/types/task';

export function useCalendar() {
  const [view, setView] = useState<CalendarView>('month');
  const [currentDate, setCurrentDate] = useState(new Date());
  const [selectedDate, setSelectedDate] = useState<Date | null>(null);

  const days = useMemo(() => {
    return view === 'month' ? getMonthDays(currentDate) : getWeekDays(currentDate);
  }, [view, currentDate]);

  const goToNext = useCallback(() => {
    setCurrentDate((prev) => (view === 'month' ? goToNextMonth(prev) : goToNextWeek(prev)));
  }, [view]);

  const goToPrev = useCallback(() => {
    setCurrentDate((prev) => (view === 'month' ? goToPrevMonth(prev) : goToPrevWeek(prev)));
  }, [view]);

  const goToToday = useCallback(() => {
    setCurrentDate(new Date());
    setSelectedDate(new Date());
  }, []);

  const selectDate = useCallback((date: Date) => {
    setSelectedDate((prev) => {
      // Toggle: if same date is clicked, deselect it
      if (prev && prev.getTime() === date.getTime()) {
        return null;
      }
      return date;
    });
  }, []);

  const toggleView = useCallback(() => {
    setView((prev) => (prev === 'month' ? 'week' : 'month'));
  }, []);

  // Get date range for API queries
  const dateRange = useMemo(() => {
    if (days.length === 0) return { startDate: '', endDate: '' };
    return {
      startDate: toApiDate(days[0]),
      endDate: toApiDate(days[days.length - 1]),
    };
  }, [days]);

  return {
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
    setView,
  };
}
