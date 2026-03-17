'use client';

import { useState, FormEvent, KeyboardEvent } from 'react';
import { Plus } from 'lucide-react';

interface QuickAddProps {
  onAdd: (description: string) => void;
  isLoading?: boolean;
}

export function QuickAdd({ onAdd, isLoading }: QuickAddProps) {
  const [description, setDescription] = useState('');
  const [isExpanded, setIsExpanded] = useState(false);

  const handleSubmit = (e: FormEvent) => {
    e.preventDefault();
    if (description.trim()) {
      onAdd(description.trim());
      setDescription('');
      setIsExpanded(false);
    }
  };

  const handleKeyDown = (e: KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Escape') {
      setIsExpanded(false);
      setDescription('');
    }
  };

  if (!isExpanded) {
    return (
      <button
        onClick={() => setIsExpanded(true)}
        className="w-full flex items-center gap-3 px-4 py-3 bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 border-dashed rounded-xl text-left hover:border-sage-400 dark:hover:border-sage-600 hover:bg-sage-50/50 dark:hover:bg-sage-900/10 transition-colors group"
      >
        <span className="w-5 h-5 rounded-full border-2 border-dashed border-gray-300 dark:border-gray-600 group-hover:border-sage-400 dark:group-hover:border-sage-500 flex items-center justify-center transition-colors flex-shrink-0">
          <Plus className="w-3 h-3 text-gray-400 dark:text-gray-500 group-hover:text-sage-500" />
        </span>
        <span className="text-sm text-gray-400 dark:text-gray-500 group-hover:text-sage-600 dark:group-hover:text-sage-400 transition-colors">
          Add a task...
        </span>
      </button>
    );
  }

  return (
    <form onSubmit={handleSubmit} className="bg-white dark:bg-gray-800 border border-sage-300 dark:border-sage-700 rounded-xl p-4 shadow-sm">
      <input
        type="text"
        value={description}
        onChange={(e) => setDescription(e.target.value)}
        onKeyDown={handleKeyDown}
        placeholder="What needs to be done?"
        className="w-full text-sm text-gray-900 dark:text-white border border-gray-200 dark:border-gray-700 rounded-xl px-4 py-2.5 focus:outline-none focus:ring-2 focus:ring-sage-500/50 placeholder-gray-400 dark:placeholder-gray-500 bg-white dark:bg-gray-800 transition-colors"
        autoFocus
        disabled={isLoading}
      />
      <div className="flex items-center justify-between mt-3 pt-3 border-t border-gray-100 dark:border-gray-700">
        <p className="text-xs text-gray-400 dark:text-gray-500">
          Press Enter to add · Esc to cancel
        </p>
        <div className="flex gap-2">
          <button
            type="button"
            onClick={() => { setIsExpanded(false); setDescription(''); }}
            className="px-3 py-1.5 text-xs font-medium text-gray-600 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg transition-colors"
          >
            Cancel
          </button>
          <button
            type="submit"
            disabled={isLoading || !description.trim()}
            className="px-3 py-1.5 text-xs font-semibold text-white bg-sage-500 hover:bg-sage-600 rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {isLoading ? 'Adding...' : 'Add Task'}
          </button>
        </div>
      </div>
    </form>
  );
}
