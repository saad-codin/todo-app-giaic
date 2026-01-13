'use client';

import { useState, useEffect, useMemo } from 'react';
import { Input, Select } from '@/components/ui/Input';
import { Button } from '@/components/ui/Button';
import type { TaskFilters, TaskSort, Task } from '@/types/task';

interface TaskFiltersProps {
  filters: TaskFilters;
  sort: TaskSort;
  tasks: Task[];
  onFiltersChange: (filters: TaskFilters) => void;
  onSortChange: (sort: TaskSort) => void;
}

const statusOptions = [
  { value: 'all', label: 'All Tasks' },
  { value: 'incomplete', label: 'Incomplete' },
  { value: 'completed', label: 'Completed' },
];

const priorityOptions = [
  { value: 'all', label: 'All Priorities' },
  { value: 'high', label: 'High' },
  { value: 'medium', label: 'Medium' },
  { value: 'low', label: 'Low' },
];

const sortOptions = [
  { value: 'createdAt', label: 'Date Created' },
  { value: 'dueDate', label: 'Due Date' },
  { value: 'priority', label: 'Priority' },
  { value: 'alphabetical', label: 'Alphabetical' },
];

export function TaskFilters({
  filters,
  sort,
  tasks,
  onFiltersChange,
  onSortChange,
}: TaskFiltersProps) {
  const [searchValue, setSearchValue] = useState(filters.search);

  // Debounce search input
  useEffect(() => {
    const timer = setTimeout(() => {
      if (searchValue !== filters.search) {
        onFiltersChange({ ...filters, search: searchValue });
      }
    }, 300);
    return () => clearTimeout(timer);
  }, [searchValue, filters, onFiltersChange]);

  // Extract unique tags from tasks
  const availableTags = useMemo(() => {
    const tagSet = new Set<string>();
    tasks.forEach((task) => task.tags.forEach((tag) => tagSet.add(tag)));
    return Array.from(tagSet).sort();
  }, [tasks]);

  const tagOptions = [
    { value: '', label: 'All Tags' },
    ...availableTags.map((tag) => ({ value: tag, label: tag })),
  ];

  const hasActiveFilters =
    filters.search ||
    filters.status !== 'all' ||
    filters.priority !== 'all' ||
    filters.tag;

  const handleClearFilters = () => {
    setSearchValue('');
    onFiltersChange({
      search: '',
      status: 'all',
      priority: 'all',
      tag: null,
    });
  };

  return (
    <div className="bg-white rounded-lg border border-gray-200 p-4 mb-6">
      <div className="flex flex-col gap-4">
        {/* Search - full width on its own row */}
        <div className="w-full">
          <Input
            type="search"
            placeholder="Search tasks..."
            value={searchValue}
            onChange={(e) => setSearchValue(e.target.value)}
            className="w-full"
          />
        </div>

        {/* Filters row */}
        <div className="flex flex-wrap items-center gap-3">
          <Select
            options={statusOptions}
            value={filters.status}
            onChange={(e) =>
              onFiltersChange({
                ...filters,
                status: e.target.value as TaskFilters['status'],
              })
            }
            className="w-36"
          />

          <Select
            options={priorityOptions}
            value={filters.priority}
            onChange={(e) =>
              onFiltersChange({
                ...filters,
                priority: e.target.value as TaskFilters['priority'],
              })
            }
            className="w-36"
          />

          {availableTags.length > 0 && (
            <Select
              options={tagOptions}
              value={filters.tag || ''}
              onChange={(e) =>
                onFiltersChange({
                  ...filters,
                  tag: e.target.value || null,
                })
              }
              className="w-36"
            />
          )}

          {/* Sort */}
          <Select
            options={sortOptions}
            value={sort.field}
            onChange={(e) =>
              onSortChange({
                ...sort,
                field: e.target.value as TaskSort['field'],
              })
            }
            className="w-36"
          />

          <button
            onClick={() =>
              onSortChange({
                ...sort,
                direction: sort.direction === 'asc' ? 'desc' : 'asc',
              })
            }
            className="p-2 rounded-lg border border-gray-300 hover:bg-gray-50 transition-colors"
            title={`Sort ${sort.direction === 'asc' ? 'descending' : 'ascending'}`}
          >
            {sort.direction === 'asc' ? (
              <svg className="w-5 h-5 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 4h13M3 8h9m-9 4h6m4 0l4-4m0 0l4 4m-4-4v12" />
              </svg>
            ) : (
              <svg className="w-5 h-5 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 4h13M3 8h9m-9 4h9m5-4v12m0 0l-4-4m4 4l4-4" />
              </svg>
            )}
          </button>

          {hasActiveFilters && (
            <Button variant="ghost" size="sm" onClick={handleClearFilters}>
              Clear Filters
            </Button>
          )}
        </div>
      </div>
    </div>
  );
}
