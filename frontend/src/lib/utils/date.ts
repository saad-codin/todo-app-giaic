import {
  format,
  parseISO,
  isToday,
  isTomorrow,
  isPast,
  startOfMonth,
  endOfMonth,
  startOfWeek,
  endOfWeek,
  eachDayOfInterval,
  addMonths,
  subMonths,
  addWeeks,
  subWeeks,
  isSameDay,
  isSameMonth,
} from 'date-fns';

// Format a date string for display
export function formatDate(dateString: string | null): string {
  if (!dateString) return '';
  const date = parseISO(dateString);
  return format(date, 'MMM d, yyyy');
}

// Format a time string for display
export function formatTime(timeString: string | null): string {
  if (!timeString) return '';
  const [hours, minutes] = timeString.split(':');
  const hour = parseInt(hours, 10);
  const ampm = hour >= 12 ? 'PM' : 'AM';
  const displayHour = hour % 12 || 12;
  return `${displayHour}:${minutes} ${ampm}`;
}

// Format date and time together
export function formatDateTime(dateString: string | null, timeString: string | null): string {
  const date = formatDate(dateString);
  const time = formatTime(timeString);
  if (date && time) return `${date} at ${time}`;
  return date || time || '';
}

// Check if a date is today
export function checkIsToday(dateString: string | null): boolean {
  if (!dateString) return false;
  return isToday(parseISO(dateString));
}

// Check if a date is tomorrow
export function checkIsTomorrow(dateString: string | null): boolean {
  if (!dateString) return false;
  return isTomorrow(parseISO(dateString));
}

// Check if a date is overdue (in the past and not completed)
export function checkIsOverdue(dateString: string | null): boolean {
  if (!dateString) return false;
  const date = parseISO(dateString);
  return isPast(date) && !isToday(date);
}

// Get human-readable relative date
export function getRelativeDate(dateString: string | null): string {
  if (!dateString) return '';
  if (checkIsToday(dateString)) return 'Today';
  if (checkIsTomorrow(dateString)) return 'Tomorrow';
  if (checkIsOverdue(dateString)) return 'Overdue';
  return formatDate(dateString);
}

// Get all days in a month for calendar grid
export function getMonthDays(date: Date): Date[] {
  const start = startOfWeek(startOfMonth(date));
  const end = endOfWeek(endOfMonth(date));
  return eachDayOfInterval({ start, end });
}

// Get all days in a week for calendar grid
export function getWeekDays(date: Date): Date[] {
  const start = startOfWeek(date);
  const end = endOfWeek(date);
  return eachDayOfInterval({ start, end });
}

// Navigation helpers
export function goToNextMonth(date: Date): Date {
  return addMonths(date, 1);
}

export function goToPrevMonth(date: Date): Date {
  return subMonths(date, 1);
}

export function goToNextWeek(date: Date): Date {
  return addWeeks(date, 1);
}

export function goToPrevWeek(date: Date): Date {
  return subWeeks(date, 1);
}

// Comparison helpers
export function areSameDay(date1: Date, date2: Date): boolean {
  return isSameDay(date1, date2);
}

export function areSameMonth(date1: Date, date2: Date): boolean {
  return isSameMonth(date1, date2);
}

// Format for API
export function toApiDate(date: Date): string {
  return format(date, 'yyyy-MM-dd');
}

// Format for display in calendar header
export function formatMonthYear(date: Date): string {
  return format(date, 'MMMM yyyy');
}

// Format for display in calendar day
export function formatDayNumber(date: Date): string {
  return format(date, 'd');
}

// Get day name (Mon, Tue, etc.)
export function getDayName(date: Date): string {
  return format(date, 'EEE');
}
