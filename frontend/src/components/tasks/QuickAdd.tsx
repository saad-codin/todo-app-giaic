'use client';

import { useState, FormEvent, KeyboardEvent } from 'react';
import { Button } from '@/components/ui/Button';

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
        className="w-full flex items-center gap-3 px-4 py-3 bg-white border border-gray-200 rounded-lg text-left hover:border-gray-300 transition-colors group"
      >
        <span className="w-5 h-5 rounded-full border-2 border-dashed border-gray-300 group-hover:border-gray-400 flex items-center justify-center">
          <svg className="w-3 h-3 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
          </svg>
        </span>
        <span className="text-gray-500">Add a task...</span>
      </button>
    );
  }

  return (
    <form onSubmit={handleSubmit} className="bg-white border border-blue-200 rounded-lg p-4 shadow-sm">
      <input
        type="text"
        value={description}
        onChange={(e) => setDescription(e.target.value)}
        onKeyDown={handleKeyDown}
        placeholder="What needs to be done?"
        className="w-full text-base text-gray-900 border border-gray-300 rounded-lg px-4 py-3 focus:ring-2 focus:ring-blue-500 focus:border-blue-500 placeholder-gray-400 bg-white"
        autoFocus
        disabled={isLoading}
      />
      <div className="flex items-center justify-between mt-3 pt-3 border-t border-gray-100">
        <p className="text-xs text-gray-500">
          Press Enter to add, Escape to cancel
        </p>
        <div className="flex gap-2">
          <Button
            type="button"
            variant="ghost"
            size="sm"
            onClick={() => {
              setIsExpanded(false);
              setDescription('');
            }}
          >
            Cancel
          </Button>
          <Button type="submit" size="sm" isLoading={isLoading} disabled={!description.trim()}>
            Add Task
          </Button>
        </div>
      </div>
    </form>
  );
}
