'use client';

import { InputHTMLAttributes, forwardRef } from 'react';

export interface InputProps extends InputHTMLAttributes<HTMLInputElement> {
  label?: string;
  error?: string;
  helperText?: string;
}

export const Input = forwardRef<HTMLInputElement, InputProps>(
  ({ className = '', label, error, helperText, id, ...props }, ref) => {
    const inputId = id || props.name;
    const hasError = !!error;

    const baseClasses = 'block w-full rounded-xl border px-4 py-2.5 text-sm bg-white dark:bg-gray-800 text-gray-900 dark:text-white placeholder-gray-400 dark:placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-sage-500/50 transition-colors';
    const stateClasses = hasError
      ? 'border-red-400 dark:border-red-700'
      : 'border-gray-200 dark:border-gray-700';

    return (
      <div className="w-full">
        {label && (
          <label
            htmlFor={inputId}
            className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1.5"
          >
            {label}
          </label>
        )}
        <input
          ref={ref}
          id={inputId}
          className={`${baseClasses} ${stateClasses} ${className}`}
          aria-invalid={hasError}
          aria-describedby={hasError ? `${inputId}-error` : undefined}
          {...props}
        />
        {hasError && (
          <p id={`${inputId}-error`} className="mt-1 text-xs text-red-500">
            {error}
          </p>
        )}
        {helperText && !hasError && (
          <p className="mt-1 text-xs text-gray-500 dark:text-gray-400">{helperText}</p>
        )}
      </div>
    );
  }
);

Input.displayName = 'Input';

export interface TextareaProps extends React.TextareaHTMLAttributes<HTMLTextAreaElement> {
  label?: string;
  error?: string;
  helperText?: string;
}

export const Textarea = forwardRef<HTMLTextAreaElement, TextareaProps>(
  ({ className = '', label, error, helperText, id, ...props }, ref) => {
    const textareaId = id || props.name;
    const hasError = !!error;

    const baseClasses = 'block w-full rounded-xl border px-4 py-2.5 text-sm bg-white dark:bg-gray-800 text-gray-900 dark:text-white placeholder-gray-400 dark:placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-sage-500/50 transition-colors resize-y min-h-[90px]';
    const stateClasses = hasError
      ? 'border-red-400 dark:border-red-700'
      : 'border-gray-200 dark:border-gray-700';

    return (
      <div className="w-full">
        {label && (
          <label
            htmlFor={textareaId}
            className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1.5"
          >
            {label}
          </label>
        )}
        <textarea
          ref={ref}
          id={textareaId}
          className={`${baseClasses} ${stateClasses} ${className}`}
          aria-invalid={hasError}
          aria-describedby={hasError ? `${textareaId}-error` : undefined}
          {...props}
        />
        {hasError && (
          <p id={`${textareaId}-error`} className="mt-1 text-xs text-red-500">
            {error}
          </p>
        )}
        {helperText && !hasError && (
          <p className="mt-1 text-xs text-gray-500 dark:text-gray-400">{helperText}</p>
        )}
      </div>
    );
  }
);

Textarea.displayName = 'Textarea';

export interface SelectProps extends React.SelectHTMLAttributes<HTMLSelectElement> {
  label?: string;
  error?: string;
  helperText?: string;
  options: Array<{ value: string; label: string }>;
}

export const Select = forwardRef<HTMLSelectElement, SelectProps>(
  ({ className = '', label, error, helperText, id, options, ...props }, ref) => {
    const selectId = id || props.name;
    const hasError = !!error;

    const baseClasses = 'block w-full rounded-xl border px-4 py-2.5 text-sm bg-white dark:bg-gray-800 text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-sage-500/50 transition-colors';
    const stateClasses = hasError
      ? 'border-red-400 dark:border-red-700'
      : 'border-gray-200 dark:border-gray-700';

    const widthMatch = className.match(/w-\S+/);
    const wrapperClass = widthMatch ? widthMatch[0] : 'w-full';

    return (
      <div className={wrapperClass}>
        {label && (
          <label
            htmlFor={selectId}
            className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1.5"
          >
            {label}
          </label>
        )}
        <select
          ref={ref}
          id={selectId}
          className={`${baseClasses} ${stateClasses} ${className}`}
          aria-invalid={hasError}
          aria-describedby={hasError ? `${selectId}-error` : undefined}
          {...props}
        >
          {options.map((option) => (
            <option key={option.value} value={option.value}>
              {option.label}
            </option>
          ))}
        </select>
        {hasError && (
          <p id={`${selectId}-error`} className="mt-1 text-xs text-red-500">
            {error}
          </p>
        )}
        {helperText && !hasError && (
          <p className="mt-1 text-xs text-gray-500 dark:text-gray-400">{helperText}</p>
        )}
      </div>
    );
  }
);

Select.displayName = 'Select';
