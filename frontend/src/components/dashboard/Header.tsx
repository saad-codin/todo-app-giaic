'use client';

import { Menu } from 'lucide-react';
import { ThemeToggle } from '@/components/ui/ThemeToggle';

interface HeaderProps {
  onMenuToggle: () => void;
  title?: string;
}

export function Header({ onMenuToggle, title = 'TaskFlow' }: HeaderProps) {
  return (
    <header className="lg:hidden flex items-center justify-between h-14 px-4 bg-white dark:bg-gray-900 border-b border-gray-200 dark:border-gray-800 flex-shrink-0">
      <button
        onClick={onMenuToggle}
        className="p-2 rounded-lg text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200 hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors"
        aria-label="Toggle menu"
      >
        <Menu className="w-5 h-5" />
      </button>

      <div className="flex items-center gap-2">
        <div className="w-6 h-6 rounded-md bg-sage-500 flex items-center justify-center">
          <svg className="w-3.5 h-3.5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
          </svg>
        </div>
        <h1 className="text-base font-bold text-gray-900 dark:text-white">{title}</h1>
      </div>

      <ThemeToggle />
    </header>
  );
}
