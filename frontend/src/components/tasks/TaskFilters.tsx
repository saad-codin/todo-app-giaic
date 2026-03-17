'use client';

import { useState, useEffect, useMemo } from 'react';
import { motion } from 'framer-motion';
import { Search, SortAsc, SortDesc } from 'lucide-react';
import type { TaskFilters, TaskSort, Task } from '@/types/task';

interface TaskFiltersProps {
  filters: TaskFilters;
  sort: TaskSort;
  tasks: Task[];
  onFiltersChange: (filters: TaskFilters) => void;
  onSortChange: (sort: TaskSort) => void;
}

const priorityTabs = [
  { value: 'all', label: 'All', priority: null },
  { value: 'incomplete', label: 'Active', priority: null, status: 'incomplete' as const },
  { value: 'urgent', label: 'Urgent', priority: 'urgent' as const },
  { value: 'high', label: 'High', priority: 'high' as const },
  { value: 'medium', label: 'Medium', priority: 'medium' as const },
  { value: 'low', label: 'Low', priority: 'low' as const },
  { value: 'completed', label: 'Done', priority: null, status: 'completed' as const },
] as const;

const sortOptions = [
  { value: 'createdAt', label: 'Created' },
  { value: 'dueDate', label: 'Due Date' },
  { value: 'priority', label: 'Priority' },
  { value: 'alphabetical', label: 'A–Z' },
];

export function TaskFilters({
  filters,
  sort,
  tasks,
  onFiltersChange,
  onSortChange,
}: TaskFiltersProps) {
  const [searchValue, setSearchValue] = useState(filters.search);

  // Debounce search
  useEffect(() => {
    const timer = setTimeout(() => {
      if (searchValue !== filters.search) {
        onFiltersChange({ ...filters, search: searchValue });
      }
    }, 300);
    return () => clearTimeout(timer);
  }, [searchValue, filters, onFiltersChange]);

  // Determine active tab from current filters
  const activeTab = useMemo(() => {
    if (filters.status === 'completed') return 'completed';
    if (filters.status === 'incomplete' && filters.priority === 'all') return 'incomplete';
    if (filters.priority !== 'all') return filters.priority;
    return 'all';
  }, [filters.status, filters.priority]);

  const handleTabClick = (tab: typeof priorityTabs[number]) => {
    if (tab.value === 'all') {
      onFiltersChange({ ...filters, status: 'all', priority: 'all' });
    } else if (tab.value === 'incomplete') {
      onFiltersChange({ ...filters, status: 'incomplete', priority: 'all' });
    } else if (tab.value === 'completed') {
      onFiltersChange({ ...filters, status: 'completed', priority: 'all' });
    } else if (tab.priority) {
      onFiltersChange({ ...filters, status: 'all', priority: tab.priority });
    }
  };

  const tabColors: Record<string, string> = {
    all: 'text-gray-700 dark:text-gray-200',
    incomplete: 'text-blue-700 dark:text-blue-300',
    urgent: 'text-purple-700 dark:text-purple-300',
    high: 'text-red-700 dark:text-red-300',
    medium: 'text-amber-700 dark:text-amber-300',
    low: 'text-green-700 dark:text-green-300',
    completed: 'text-gray-500 dark:text-gray-400',
  };

  const activeTabBg: Record<string, string> = {
    all: 'bg-gray-100 dark:bg-gray-700',
    incomplete: 'bg-blue-100 dark:bg-blue-900/40',
    urgent: 'bg-purple-100 dark:bg-purple-900/40',
    high: 'bg-red-100 dark:bg-red-900/40',
    medium: 'bg-amber-100 dark:bg-amber-900/40',
    low: 'bg-green-100 dark:bg-green-900/40',
    completed: 'bg-gray-100 dark:bg-gray-700',
  };

  return (
    <div className="mb-4 space-y-3">
      {/* Priority tabs */}
      <div className="flex items-center gap-1 flex-wrap">
        {priorityTabs.map((tab) => (
          <button
            key={tab.value}
            onClick={() => handleTabClick(tab)}
            className={`relative px-3 py-1.5 rounded-full text-xs font-medium transition-colors ${
              activeTab === tab.value
                ? `${activeTabBg[tab.value]} ${tabColors[tab.value]}`
                : 'text-gray-500 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-gray-800'
            }`}
          >
            {activeTab === tab.value && (
              <motion.span
                layoutId="activeTabIndicator"
                className={`absolute inset-0 rounded-full ${activeTabBg[tab.value]}`}
                transition={{ duration: 0.2 }}
              />
            )}
            <span className="relative">{tab.label}</span>
          </button>
        ))}
      </div>

      {/* Search + sort row */}
      <div className="flex items-center gap-2">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-3.5 h-3.5 text-gray-400" />
          <input
            type="search"
            placeholder="Search tasks..."
            value={searchValue}
            onChange={(e) => setSearchValue(e.target.value)}
            className="w-full pl-8 pr-3 py-2 text-sm rounded-xl border border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800 text-gray-900 dark:text-white placeholder-gray-400 dark:placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-sage-500/50 transition-colors"
          />
        </div>

        <select
          value={sort.field}
          onChange={(e) => onSortChange({ ...sort, field: e.target.value as TaskSort['field'] })}
          className="px-3 py-2 text-sm rounded-xl border border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800 text-gray-700 dark:text-gray-300 focus:outline-none focus:ring-2 focus:ring-sage-500/50 transition-colors"
        >
          {sortOptions.map((o) => (
            <option key={o.value} value={o.value}>{o.label}</option>
          ))}
        </select>

        <button
          onClick={() => onSortChange({ ...sort, direction: sort.direction === 'asc' ? 'desc' : 'asc' })}
          className="p-2 rounded-xl border border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800 text-gray-500 dark:text-gray-400 hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors"
          title={`Sort ${sort.direction === 'asc' ? 'descending' : 'ascending'}`}
        >
          {sort.direction === 'asc' ? <SortAsc className="w-4 h-4" /> : <SortDesc className="w-4 h-4" />}
        </button>
      </div>
    </div>
  );
}
