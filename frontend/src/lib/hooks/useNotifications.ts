'use client';

import { useState, useEffect, useCallback, useRef } from 'react';
import { useToast } from '@/components/ui/Toast';
import type { NotificationPermission as NotifPermission } from '@/types/task';

interface ScheduledReminder {
  taskId: string;
  reminderTime: string;
  timeoutId: ReturnType<typeof setTimeout>;
}

export function useNotifications() {
  const [permission, setPermission] = useState<NotifPermission>('default');
  const scheduledReminders = useRef<ScheduledReminder[]>([]);
  const { addToast } = useToast();

  // Check notification permission on mount
  useEffect(() => {
    if (typeof window !== 'undefined' && 'Notification' in window) {
      setPermission(Notification.permission as NotifPermission);
    }
  }, []);

  // Request notification permission
  const requestPermission = useCallback(async () => {
    if (!('Notification' in window)) {
      addToast('warning', 'Browser notifications are not supported in this browser.');
      return false;
    }

    try {
      const result = await Notification.requestPermission();
      setPermission(result as NotifPermission);

      if (result === 'granted') {
        addToast('success', 'Notifications enabled! You will receive reminders for your tasks.');
        return true;
      } else if (result === 'denied') {
        addToast('warning', 'Notifications blocked. You can enable them in your browser settings.');
        return false;
      }
      return false;
    } catch (error) {
      addToast('error', 'Failed to request notification permission.');
      return false;
    }
  }, [addToast]);

  // Send a notification
  const sendNotification = useCallback(
    (title: string, options?: NotificationOptions) => {
      if (permission !== 'granted') {
        console.warn('Notification permission not granted');
        return null;
      }

      try {
        const notification = new Notification(title, {
          icon: '/favicon.ico',
          badge: '/favicon.ico',
          ...options,
        });

        // Handle click - focus window and navigate to task
        notification.onclick = () => {
          window.focus();
          notification.close();
        };

        return notification;
      } catch (error) {
        console.error('Failed to send notification:', error);
        return null;
      }
    },
    [permission]
  );

  // Schedule a reminder for a task
  const scheduleReminder = useCallback(
    (taskId: string, reminderTime: string, taskDescription: string) => {
      if (permission !== 'granted') {
        return;
      }

      const reminderDate = new Date(reminderTime);
      const now = new Date();
      const delay = reminderDate.getTime() - now.getTime();

      if (delay <= 0) {
        // Reminder time has passed
        return;
      }

      // Cancel existing reminder for this task
      cancelReminder(taskId);

      // Schedule new reminder
      const timeoutId = setTimeout(() => {
        sendNotification('Task Reminder', {
          body: taskDescription,
          tag: `task-${taskId}`,
          requireInteraction: true,
        });

        // Remove from scheduled list
        scheduledReminders.current = scheduledReminders.current.filter(
          (r) => r.taskId !== taskId
        );
      }, delay);

      scheduledReminders.current.push({
        taskId,
        reminderTime,
        timeoutId,
      });
    },
    [permission, sendNotification]
  );

  // Cancel a scheduled reminder
  const cancelReminder = useCallback((taskId: string) => {
    const reminder = scheduledReminders.current.find((r) => r.taskId === taskId);
    if (reminder) {
      clearTimeout(reminder.timeoutId);
      scheduledReminders.current = scheduledReminders.current.filter(
        (r) => r.taskId !== taskId
      );
    }
  }, []);

  // Cancel all reminders
  const cancelAllReminders = useCallback(() => {
    scheduledReminders.current.forEach((r) => clearTimeout(r.timeoutId));
    scheduledReminders.current = [];
  }, []);

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      cancelAllReminders();
    };
  }, [cancelAllReminders]);

  return {
    permission,
    isSupported: typeof window !== 'undefined' && 'Notification' in window,
    isEnabled: permission === 'granted',
    isDenied: permission === 'denied',
    requestPermission,
    sendNotification,
    scheduleReminder,
    cancelReminder,
    cancelAllReminders,
    scheduledCount: scheduledReminders.current.length,
  };
}
