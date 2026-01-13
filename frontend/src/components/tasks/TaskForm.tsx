'use client';

import { useForm, Controller } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { Button } from '@/components/ui/Button';
import { Input, Textarea, Select } from '@/components/ui/Input';
import { taskSchema, type TaskFormData } from '@/lib/utils/validation';
import type { Task } from '@/types/task';

interface TaskFormProps {
  task?: Task;
  onSubmit: (data: TaskFormData) => void;
  onCancel: () => void;
  isSubmitting?: boolean;
}

const priorityOptions = [
  { value: 'low', label: 'Low' },
  { value: 'medium', label: 'Medium' },
  { value: 'high', label: 'High' },
];

const recurrenceOptions = [
  { value: 'none', label: 'No Recurrence' },
  { value: 'daily', label: 'Daily' },
  { value: 'weekly', label: 'Weekly' },
  { value: 'monthly', label: 'Monthly' },
];

export function TaskForm({ task, onSubmit, onCancel, isSubmitting }: TaskFormProps) {
  const {
    register,
    handleSubmit,
    control,
    formState: { errors },
  } = useForm<TaskFormData>({
    resolver: zodResolver(taskSchema),
    defaultValues: {
      description: task?.description || '',
      priority: task?.priority || 'medium',
      tags: task?.tags || [],
      dueDate: task?.dueDate || null,
      dueTime: task?.dueTime || null,
      recurrence: task?.recurrence || 'none',
    },
  });

  return (
    <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
      <Textarea
        label="Description"
        placeholder="What needs to be done?"
        error={errors.description?.message}
        {...register('description')}
      />

      <div className="grid grid-cols-2 gap-4">
        <Controller
          name="priority"
          control={control}
          render={({ field }) => (
            <Select
              label="Priority"
              options={priorityOptions}
              error={errors.priority?.message}
              {...field}
            />
          )}
        />

        <Controller
          name="recurrence"
          control={control}
          render={({ field }) => (
            <Select
              label="Recurrence"
              options={recurrenceOptions}
              error={errors.recurrence?.message}
              {...field}
            />
          )}
        />
      </div>

      <div className="grid grid-cols-2 gap-4">
        <Input
          type="date"
          label="Due Date"
          error={errors.dueDate?.message}
          {...register('dueDate')}
        />

        <Input
          type="time"
          label="Due Time (optional)"
          error={errors.dueTime?.message}
          {...register('dueTime')}
        />
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">
          Tags (comma separated)
        </label>
        <Controller
          name="tags"
          control={control}
          render={({ field }) => (
            <Input
              placeholder="work, personal, urgent"
              value={field.value?.join(', ') || ''}
              onChange={(e) => {
                const tags = e.target.value
                  .split(',')
                  .map((t) => t.trim())
                  .filter((t) => t.length > 0);
                field.onChange(tags);
              }}
            />
          )}
        />
      </div>

      <div className="flex justify-end gap-3 pt-4 border-t">
        <Button type="button" variant="ghost" onClick={onCancel}>
          Cancel
        </Button>
        <Button type="submit" isLoading={isSubmitting}>
          {task ? 'Update Task' : 'Create Task'}
        </Button>
      </div>
    </form>
  );
}
