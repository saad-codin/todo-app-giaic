'use client';

import { Button } from '@/components/ui/Button';
import { formatMonthYear } from '@/lib/utils/date';
import type { CalendarView } from '@/types/task';

interface CalendarNavProps {
  currentDate: Date;
  view: CalendarView;
  onPrev: () => void;
  onNext: () => void;
  onToday: () => void;
  onToggleView: () => void;
}

export function CalendarNav({
  currentDate,
  view,
  onPrev,
  onNext,
  onToday,
  onToggleView,
}: CalendarNavProps) {
  return (
    <div className="flex items-center justify-between mb-6">
      <div className="flex items-center gap-4">
        <h2 className="text-xl font-bold text-gray-900">
          {formatMonthYear(currentDate)}
        </h2>
        <div className="flex items-center gap-1">
          <button
            onClick={onPrev}
            className="p-2 rounded-lg hover:bg-gray-100 transition-colors"
            aria-label="Previous"
          >
            <svg className="w-5 h-5 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
            </svg>
          </button>
          <button
            onClick={onNext}
            className="p-2 rounded-lg hover:bg-gray-100 transition-colors"
            aria-label="Next"
          >
            <svg className="w-5 h-5 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
            </svg>
          </button>
        </div>
      </div>

      <div className="flex items-center gap-2">
        <Button variant="outline" size="sm" onClick={onToday}>
          Today
        </Button>
        <div className="flex rounded-lg border border-gray-200 overflow-hidden">
          <button
            onClick={view === 'week' ? onToggleView : undefined}
            className={`px-3 py-1.5 text-sm font-medium transition-colors ${
              view === 'month'
                ? 'bg-blue-50 text-blue-700'
                : 'bg-white text-gray-600 hover:bg-gray-50'
            }`}
          >
            Month
          </button>
          <button
            onClick={view === 'month' ? onToggleView : undefined}
            className={`px-3 py-1.5 text-sm font-medium transition-colors ${
              view === 'week'
                ? 'bg-blue-50 text-blue-700'
                : 'bg-white text-gray-600 hover:bg-gray-50'
            }`}
          >
            Week
          </button>
        </div>
      </div>
    </div>
  );
}
