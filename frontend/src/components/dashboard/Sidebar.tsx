'use client';

import { useState } from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { motion } from 'framer-motion';
import {
  LayoutDashboard,
  Bot,
  Calendar,
  StickyNote,
  Circle,
  Briefcase,
  User,
  X,
  LogOut,
  Search,
} from 'lucide-react';
import { useAuthContext } from '@/lib/auth';
import { ThemeToggle } from '@/components/ui/ThemeToggle';
import { NotificationBell } from '@/components/ui/NotificationBell';
import type { AppNotification } from '@/components/ui/NotificationBell';

interface SidebarProps {
  notifications?: AppNotification[];
  onMarkAllRead?: () => void;
  onClearNotifications?: () => void;
  isConnected?: boolean;
  onClose?: () => void;
}

const navItems = [
  { href: '/dashboard', label: 'Dashboard', icon: LayoutDashboard },
  { href: '/dashboard/chat', label: 'AI Assistant', icon: Bot },
  { href: '/dashboard/calendar', label: 'Calendar', icon: Calendar },
  { href: '/dashboard/sticky', label: 'Sticky Wall', icon: StickyNote },
];

const listItems = [
  { label: 'Personal', icon: Circle, color: 'text-sage-500' },
  { label: 'Work', icon: Briefcase, color: 'text-blue-500' },
];

export function Sidebar({
  notifications = [],
  onMarkAllRead,
  onClearNotifications,
  isConnected = false,
  onClose,
}: SidebarProps) {
  const pathname = usePathname();
  const { user, signOut } = useAuthContext();
  const [searchValue, setSearchValue] = useState('');

  return (
    <aside className="flex flex-col h-full bg-white dark:bg-gray-900 border-r border-gray-200 dark:border-gray-800">
      {/* Logo + close button (mobile) */}
      <div className="flex items-center justify-between h-16 px-4 border-b border-gray-200 dark:border-gray-800 flex-shrink-0">
        <Link href="/dashboard" className="flex items-center gap-2">
          <div className="w-7 h-7 rounded-lg bg-sage-500 flex items-center justify-center">
            <svg className="w-4 h-4 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
            </svg>
          </div>
          <span className="text-lg font-bold text-gray-900 dark:text-white">TaskFlow</span>
        </Link>
        {onClose && (
          <button
            onClick={onClose}
            className="p-1.5 rounded-lg text-gray-400 hover:text-gray-600 dark:hover:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors"
            aria-label="Close sidebar"
          >
            <X className="w-5 h-5" />
          </button>
        )}
      </div>

      {/* Search bar */}
      <div className="px-3 py-3 flex-shrink-0">
        <div className="relative">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
          <input
            type="text"
            placeholder="Search tasks..."
            value={searchValue}
            onChange={(e) => setSearchValue(e.target.value)}
            className="w-full pl-9 pr-3 py-2 text-sm rounded-lg bg-gray-100 dark:bg-gray-800 text-gray-700 dark:text-gray-300 placeholder-gray-400 dark:placeholder-gray-500 border-0 focus:outline-none focus:ring-2 focus:ring-sage-500/50 transition-colors"
          />
        </div>
      </div>

      {/* Scrollable nav area */}
      <nav className="flex-1 px-3 py-2 overflow-y-auto space-y-6">
        {/* Navigation section */}
        <div>
          <p className="px-2 mb-1 text-xs font-semibold text-gray-400 dark:text-gray-500 uppercase tracking-wider">
            Navigation
          </p>
          <ul className="space-y-0.5">
            {navItems.map((item) => {
              const isActive = pathname === item.href || (item.href !== '/dashboard' && pathname.startsWith(item.href));
              const Icon = item.icon;
              return (
                <li key={item.href}>
                  <motion.div whileHover={{ x: 2 }} transition={{ duration: 0.15 }}>
                    <Link
                      href={item.href}
                      className={`flex items-center gap-3 px-3 py-2 rounded-lg text-sm font-medium transition-colors duration-150 ${
                        isActive
                          ? 'bg-sage-100 dark:bg-sage-900/30 text-sage-700 dark:text-sage-400 border-l-2 border-sage-500'
                          : 'text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-800'
                      }`}
                    >
                      <Icon className="w-4 h-4 flex-shrink-0" />
                      <span>{item.label}</span>
                    </Link>
                  </motion.div>
                </li>
              );
            })}
          </ul>
        </div>

        {/* My Lists section */}
        <div>
          <p className="px-2 mb-1 text-xs font-semibold text-gray-400 dark:text-gray-500 uppercase tracking-wider">
            My Lists
          </p>
          <ul className="space-y-0.5">
            {listItems.map((item) => {
              const Icon = item.icon;
              return (
                <li key={item.label}>
                  <motion.div whileHover={{ x: 2 }} transition={{ duration: 0.15 }}>
                    <button className="w-full flex items-center gap-3 px-3 py-2 rounded-lg text-sm font-medium text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors duration-150">
                      <Icon className={`w-4 h-4 flex-shrink-0 ${item.color}`} />
                      <span>{item.label}</span>
                    </button>
                  </motion.div>
                </li>
              );
            })}
          </ul>
        </div>

        {/* Tags section */}
        <div>
          <p className="px-2 mb-2 text-xs font-semibold text-gray-400 dark:text-gray-500 uppercase tracking-wider">
            Tags
          </p>
          <div className="flex flex-wrap gap-1.5 px-2">
            {['work', 'personal', 'urgent'].map((tag) => (
              <span
                key={tag}
                className="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium bg-gray-100 dark:bg-gray-800 text-gray-600 dark:text-gray-400 cursor-pointer hover:bg-sage-100 dark:hover:bg-sage-900/30 hover:text-sage-700 dark:hover:text-sage-400 transition-colors"
              >
                {tag}
              </span>
            ))}
          </div>
        </div>
      </nav>

      {/* Footer */}
      <div className="flex-shrink-0 px-3 py-3 border-t border-gray-200 dark:border-gray-800 space-y-2">
        {/* Tools row: ThemeToggle + NotificationBell + WS status */}
        <div className="flex items-center gap-2 px-1">
          <ThemeToggle />

          <div className="relative z-50">
            <NotificationBell
              notifications={notifications}
              onMarkAllRead={onMarkAllRead || (() => {})}
              onClear={onClearNotifications || (() => {})}
            />
          </div>

          {/* WS connection status */}
          <div className="flex items-center gap-1.5 ml-auto">
            <div className="relative flex items-center justify-center">
              {isConnected ? (
                <motion.div
                  animate={{ scale: [1, 1.3, 1] }}
                  transition={{ repeat: Infinity, duration: 2 }}
                  className="w-2 h-2 rounded-full bg-green-400"
                />
              ) : (
                <div className="w-2 h-2 rounded-full bg-gray-400" />
              )}
            </div>
            <span className="text-xs text-gray-500 dark:text-gray-400">
              {isConnected ? 'Live' : 'Offline'}
            </span>
          </div>
        </div>

        {/* User row */}
        <div className="flex items-center gap-2 px-1 py-1 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors group">
          <div className="w-8 h-8 rounded-full bg-sage-100 dark:bg-sage-900/40 flex items-center justify-center flex-shrink-0">
            <span className="text-sm font-semibold text-sage-700 dark:text-sage-400">
              {user?.name?.[0]?.toUpperCase() || user?.email?.[0]?.toUpperCase() || 'U'}
            </span>
          </div>
          <div className="flex-1 min-w-0">
            <p className="text-sm font-medium text-gray-900 dark:text-white truncate leading-tight">
              {user?.name || 'User'}
            </p>
            <p className="text-xs text-gray-500 dark:text-gray-400 truncate leading-tight">
              {user?.email || ''}
            </p>
          </div>
          <button
            onClick={() => signOut()}
            className="p-1.5 text-gray-400 hover:text-gray-600 dark:hover:text-gray-300 opacity-0 group-hover:opacity-100 rounded-lg hover:bg-gray-200 dark:hover:bg-gray-700 transition-all"
            title="Sign out"
            aria-label="Sign out"
          >
            <LogOut className="w-4 h-4" />
          </button>
        </div>
      </div>
    </aside>
  );
}
