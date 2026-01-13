'use client';

import { HTMLAttributes, forwardRef } from 'react';

export interface BadgeProps extends HTMLAttributes<HTMLSpanElement> {
  variant?: 'default' | 'primary' | 'success' | 'warning' | 'danger' | 'priority-high' | 'priority-medium' | 'priority-low';
  size?: 'sm' | 'md';
}

const variantClasses = {
  default: 'bg-gray-100 text-gray-800',
  primary: 'bg-blue-100 text-blue-800',
  success: 'bg-green-100 text-green-800',
  warning: 'bg-amber-100 text-amber-800',
  danger: 'bg-red-100 text-red-800',
  'priority-high': 'bg-red-100 text-red-800 border border-red-300',
  'priority-medium': 'bg-amber-100 text-amber-800 border border-amber-300',
  'priority-low': 'bg-green-100 text-green-800 border border-green-300',
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

// Priority badge helper component
export interface PriorityBadgeProps {
  priority: 'high' | 'medium' | 'low';
  size?: 'sm' | 'md';
  className?: string;
}

export function PriorityBadge({ priority, size = 'sm', className = '' }: PriorityBadgeProps) {
  const labels = {
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

// Tag badge component
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
      className={`${onClick ? 'cursor-pointer hover:bg-gray-200' : ''} ${className}`}
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
          className="ml-1 -mr-1 h-4 w-4 rounded-full hover:bg-gray-300 inline-flex items-center justify-center"
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
