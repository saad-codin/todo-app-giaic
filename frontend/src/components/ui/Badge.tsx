'use client';

import { HTMLAttributes, forwardRef } from 'react';

export interface BadgeProps extends HTMLAttributes<HTMLSpanElement> {
  variant?: 'default' | 'primary' | 'success' | 'warning' | 'danger' | 'priority-urgent' | 'priority-high' | 'priority-medium' | 'priority-low';
  size?: 'sm' | 'md';
}

const variantClasses = {
  default: 'bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300',
  primary: 'bg-sage-100 dark:bg-sage-900/30 text-sage-700 dark:text-sage-400',
  success: 'bg-green-100 dark:bg-green-900/30 text-green-700 dark:text-green-400',
  warning: 'bg-amber-100 dark:bg-amber-900/30 text-amber-700 dark:text-amber-400',
  danger: 'bg-red-100 dark:bg-red-900/30 text-red-700 dark:text-red-400',
  'priority-urgent': 'bg-purple-100 dark:bg-purple-900/30 text-purple-700 dark:text-purple-400',
  'priority-high': 'bg-red-100 dark:bg-red-900/30 text-red-700 dark:text-red-400',
  'priority-medium': 'bg-amber-100 dark:bg-amber-900/30 text-amber-700 dark:text-amber-400',
  'priority-low': 'bg-green-100 dark:bg-green-900/30 text-green-700 dark:text-green-400',
};

const sizeClasses = {
  sm: 'px-2 py-0.5 text-xs',
  md: 'px-2.5 py-1 text-sm',
};

export const Badge = forwardRef<HTMLSpanElement, BadgeProps>(
  ({ className = '', variant = 'default', size = 'sm', children, ...props }, ref) => {
    const baseClasses = 'inline-flex items-center font-medium rounded-full';

    return (
      <span
        ref={ref}
        className={`${baseClasses} ${variantClasses[variant]} ${sizeClasses[size]} ${className}`}
        {...props}
      >
        {children}
      </span>
    );
  }
);

Badge.displayName = 'Badge';

export interface PriorityBadgeProps {
  priority: 'urgent' | 'high' | 'medium' | 'low';
  size?: 'sm' | 'md';
  className?: string;
}

export function PriorityBadge({ priority, size = 'sm', className = '' }: PriorityBadgeProps) {
  const labels = {
    urgent: 'Urgent',
    high: 'High',
    medium: 'Medium',
    low: 'Low',
  };

  return (
    <Badge variant={`priority-${priority}`} size={size} className={className}>
      {labels[priority]}
    </Badge>
  );
}

export interface TagBadgeProps {
  tag: string;
  onClick?: () => void;
  onRemove?: () => void;
  size?: 'sm' | 'md';
  className?: string;
}

export function TagBadge({ tag, onClick, onRemove, size = 'sm', className = '' }: TagBadgeProps) {
  return (
    <Badge
      variant="default"
      size={size}
      className={`${onClick ? 'cursor-pointer hover:bg-gray-200 dark:hover:bg-gray-600' : ''} ${className}`}
      onClick={onClick}
    >
      {tag}
      {onRemove && (
        <button
          type="button"
          onClick={(e) => {
            e.stopPropagation();
            onRemove();
          }}
          className="ml-1 -mr-1 h-4 w-4 rounded-full hover:bg-gray-300 dark:hover:bg-gray-500 inline-flex items-center justify-center transition-colors"
          aria-label={`Remove ${tag}`}
        >
          <svg className="h-3 w-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>
      )}
    </Badge>
  );
}
