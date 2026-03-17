'use client';

import { useState, useEffect, useCallback } from 'react';
import { useRouter } from 'next/navigation';
import { motion, AnimatePresence } from 'framer-motion';
import { Sidebar } from '@/components/dashboard/Sidebar';
import { Header } from '@/components/dashboard/Header';
import { useAuthContext } from '@/lib/auth';
import { useWebSocket } from '@/lib/hooks/useWebSocket';
import { useToast } from '@/components/ui/Toast';
import { getAuthToken } from '@/lib/api';
import type { AppNotification } from '@/components/ui/NotificationBell';

export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const { isLoading, isAuthenticated } = useAuthContext();
  const [isMobileOpen, setIsMobileOpen] = useState(false);
  const [notifications, setNotifications] = useState<AppNotification[]>([]);
  const router = useRouter();
  const { addToast } = useToast();
  const token = getAuthToken();

  useEffect(() => {
    if (!isLoading && !isAuthenticated) {
      router.push('/signin');
    }
  }, [isLoading, isAuthenticated, router]);

  const addNotification = useCallback((n: Omit<AppNotification, 'id' | 'timestamp' | 'read'>) => {
    setNotifications((prev) =>
      [{ ...n, id: Math.random().toString(36).slice(2), timestamp: new Date(), read: false }, ...prev].slice(0, 50)
    );
  }, []);

  const markAllRead = useCallback(() => {
    setNotifications((prev) => prev.map((n) => ({ ...n, read: true })));
  }, []);

  const clearNotifications = useCallback(() => {
    setNotifications([]);
  }, []);

  const wsUrl = process.env.NEXT_PUBLIC_WS_URL || 'ws://localhost:8003';
  const { isConnected } = useWebSocket({
    url: `${wsUrl}/ws`,
    token,
    enabled: isAuthenticated,
    onMessage: (message) => {
      if (message.type === 'reminder') {
        addToast('info', `Reminder: ${message.task_description}`, 8000);
        addNotification({
          type: 'reminder',
          message: `Reminder: ${message.task_description}${message.due_date ? ` (due ${message.due_date})` : ''}`,
          taskId: message.task_id,
        });
      }
    },
  });

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-background">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary" />
      </div>
    );
  }

  if (!isAuthenticated) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-background">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary" />
      </div>
    );
  }

  return (
    <div className="min-h-screen flex bg-background">
      {/* Mobile overlay */}
      <AnimatePresence>
        {isMobileOpen && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            transition={{ duration: 0.2 }}
            className="lg:hidden fixed inset-0 bg-black/50 z-40"
            onClick={() => setIsMobileOpen(false)}
          />
        )}
      </AnimatePresence>

      {/* Mobile sidebar slide-in */}
      <AnimatePresence>
        {isMobileOpen && (
          <motion.div
            initial={{ x: -280 }}
            animate={{ x: 0 }}
            exit={{ x: -280 }}
            transition={{ duration: 0.25, ease: 'easeOut' }}
            className="lg:hidden fixed inset-y-0 left-0 z-50 w-64"
          >
            <Sidebar
              notifications={notifications}
              onMarkAllRead={markAllRead}
              onClearNotifications={clearNotifications}
              isConnected={isConnected}
              onClose={() => setIsMobileOpen(false)}
            />
          </motion.div>
        )}
      </AnimatePresence>

      {/* Desktop sidebar (always visible) */}
      <div className="hidden lg:flex flex-col w-64 flex-shrink-0">
        <Sidebar
          notifications={notifications}
          onMarkAllRead={markAllRead}
          onClearNotifications={clearNotifications}
          isConnected={isConnected}
        />
      </div>

      {/* Main area */}
      <div className="flex-1 flex flex-col min-w-0">
        {/* Mobile header */}
        <Header onMenuToggle={() => setIsMobileOpen(true)} />

        {/* Page content */}
        <main className="flex-1 overflow-auto">
          {children}
        </main>
      </div>
    </div>
  );
}
