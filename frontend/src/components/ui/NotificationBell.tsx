'use client';

import { useEffect, useRef, useState } from 'react';
import { Bell } from 'lucide-react';

export interface AppNotification {
  id: string;
  type: 'reminder' | 'info';
  message: string;
  timestamp: Date;
  read: boolean;
  taskId?: string;
}

interface NotificationBellProps {
  notifications: AppNotification[];
  onMarkAllRead: () => void;
  onClear: () => void;
}

function formatRelativeTime(date: Date): string {
  const now = new Date();
  const diffMs = now.getTime() - date.getTime();
  const diffSec = Math.floor(diffMs / 1000);
  const diffMin = Math.floor(diffSec / 60);
  const diffHr = Math.floor(diffMin / 60);

  if (diffSec < 60) return 'just now';
  if (diffMin < 60) return `${diffMin}m ago`;
  if (diffHr < 24) return `${diffHr}h ago`;
  return date.toLocaleDateString();
}

export function NotificationBell({ notifications, onMarkAllRead, onClear }: NotificationBellProps) {
  const [open, setOpen] = useState(false);
  const panelRef = useRef<HTMLDivElement>(null);
  const buttonRef = useRef<HTMLButtonElement>(null);

  const unreadCount = notifications.filter((n) => !n.read).length;
  const visible = notifications.slice(0, 20);

  useEffect(() => {
    if (!open) return;
    const handleMouseDown = (e: MouseEvent) => {
      if (
        panelRef.current &&
        !panelRef.current.contains(e.target as Node) &&
        !buttonRef.current?.contains(e.target as Node)
      ) {
        setOpen(false);
      }
    };
    document.addEventListener('mousedown', handleMouseDown);
    return () => document.removeEventListener('mousedown', handleMouseDown);
  }, [open]);

  return (
    <div className="relative">
      <button
        ref={buttonRef}
        type="button"
        onClick={() => setOpen((prev) => !prev)}
        className="relative w-9 h-9 flex items-center justify-center rounded-lg bg-gray-100 dark:bg-gray-800 text-gray-500 dark:text-gray-400 hover:bg-gray-200 dark:hover:bg-gray-700 hover:text-gray-700 dark:hover:text-gray-200 transition-colors"
        aria-label={`Notifications${unreadCount > 0 ? ` (${unreadCount} unread)` : ''}`}
      >
        <Bell className="w-4 h-4" />
        {unreadCount > 0 && (
          <span className="absolute top-1 right-1 flex h-4 w-4 items-center justify-center rounded-full bg-sage-500 text-white text-[10px] font-bold leading-none">
            {unreadCount > 9 ? '9+' : unreadCount}
          </span>
        )}
      </button>

      {open && (
        <div
          ref={panelRef}
          className="absolute bottom-full mb-2 right-0 w-80 bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-700 rounded-xl shadow-xl z-[100] overflow-hidden"
        >
          <div className="flex items-center justify-between px-4 py-3 border-b border-gray-100 dark:border-gray-800">
            <h3 className="text-sm font-semibold text-gray-900 dark:text-white">Notifications</h3>
            {unreadCount > 0 && (
              <button
                type="button"
                onClick={onMarkAllRead}
                className="text-xs text-sage-600 dark:text-sage-400 hover:text-sage-700 dark:hover:text-sage-300 font-medium transition-colors"
              >
                Mark all read
              </button>
            )}
          </div>

          <div className="max-h-72 overflow-y-auto">
            {visible.length === 0 ? (
              <div className="flex flex-col items-center justify-center py-10 text-gray-400 dark:text-gray-500">
                <Bell className="h-7 w-7 mb-2 opacity-40" />
                <p className="text-sm">No notifications yet</p>
              </div>
            ) : (
              visible.map((n) => (
                <div
                  key={n.id}
                  className={`flex items-start gap-3 px-4 py-3 border-b border-gray-50 dark:border-gray-800 last:border-b-0 ${
                    n.read ? 'bg-white dark:bg-gray-900' : 'bg-sage-50 dark:bg-sage-900/20'
                  }`}
                >
                  <div className="flex-shrink-0 mt-0.5">
                    <span className={`flex h-7 w-7 items-center justify-center rounded-full ${
                      n.type === 'reminder' ? 'bg-amber-100 dark:bg-amber-900/30' : 'bg-blue-100 dark:bg-blue-900/30'
                    }`}>
                      {n.type === 'reminder' ? (
                        <svg className="h-3.5 w-3.5 text-amber-600 dark:text-amber-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                        </svg>
                      ) : (
                        <svg className="h-3.5 w-3.5 text-blue-600 dark:text-blue-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                        </svg>
                      )}
                    </span>
                  </div>
                  <div className="flex-1 min-w-0">
                    <p className="text-xs text-gray-800 dark:text-gray-200 leading-snug">{n.message}</p>
                    <p className="text-xs text-gray-400 dark:text-gray-500 mt-0.5">{formatRelativeTime(n.timestamp)}</p>
                  </div>
                  {!n.read && (
                    <div className="flex-shrink-0 mt-1.5">
                      <span className="block h-2 w-2 rounded-full bg-sage-500" />
                    </div>
                  )}
                </div>
              ))
            )}
          </div>

          {notifications.length > 0 && (
            <div className="px-4 py-2.5 border-t border-gray-100 dark:border-gray-800">
              <button
                type="button"
                onClick={() => { onClear(); setOpen(false); }}
                className="w-full text-xs text-gray-500 dark:text-gray-400 hover:text-red-500 dark:hover:text-red-400 font-medium py-0.5 transition-colors text-center"
              >
                Clear all
              </button>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
