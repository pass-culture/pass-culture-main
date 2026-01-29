import { describe, expect, it } from 'vitest'

import { EditedTodoFormValuesSchema, NewTodoFormValuesSchema } from '../schemas'

describe('NewTodoFormValuesSchema', () => {
  it('accepts valid create with low priority and no due date', () => {
    const result = NewTodoFormValuesSchema.safeParse({ title: 'Test' })

    expect(result.success).toBe(true)
  })

  it('accepts valid create with high priority and due date', () => {
    const result = NewTodoFormValuesSchema.safeParse({
      title: 'Urgent',
      priority: 'high',
      dueDate: '2026-12-31T23:59:00Z',
    })

    expect(result.success).toBe(true)
  })

  it('accepts datetime-local format without Z suffix', () => {
    const result = NewTodoFormValuesSchema.safeParse({
      title: 'Task',
      priority: 'medium',
      dueDate: '2026-12-31T23:59',
    })

    expect(result.success).toBe(true)
  })

  it('rejects high priority without due date', () => {
    const result = NewTodoFormValuesSchema.safeParse({
      title: 'Urgent',
      priority: 'high',
    })

    expect(result.success).toBe(false)
    if (!result.success) {
      const dueDateError = result.error.issues.find((issue) =>
        issue.path.includes('dueDate')
      )
      expect(dueDateError?.message).toBe(
        'Due date is required for high-priority todos'
      )
    }
  })

  it('surfaces custom error message for title exceeding max length', () => {
    const result = NewTodoFormValuesSchema.safeParse({
      title: 'x'.repeat(256),
    })

    expect(result.success).toBe(false)
    if (!result.success) {
      const titleError = result.error.issues.find((issue) =>
        issue.path.includes('title')
      )
      expect(titleError?.message).toBe('Title cannot exceed 255 characters')
    }
  })

  it('rejects low priority with due date', () => {
    const result = NewTodoFormValuesSchema.safeParse({
      title: 'Chill',
      priority: 'low',
      dueDate: '2026-12-31T23:59:00Z',
    })

    expect(result.success).toBe(false)
    if (!result.success) {
      const priorityError = result.error.issues.find((issue) =>
        issue.path.includes('priority')
      )
      expect(priorityError?.message).toBe(
        'Low-priority todos cannot have a due date'
      )
    }
  })
})

describe('EditedTodoFormValuesSchema', () => {
  it('accepts valid update with title only', () => {
    const result = EditedTodoFormValuesSchema.safeParse({ title: 'Updated' })

    expect(result.success).toBe(true)
  })

  it('accepts completing a todo with description', () => {
    const result = EditedTodoFormValuesSchema.safeParse({
      isCompleted: true,
      description: 'Done with details',
    })

    expect(result.success).toBe(true)
  })

  it('accepts datetime-local format without Z suffix', () => {
    const result = EditedTodoFormValuesSchema.safeParse({
      priority: 'high',
      dueDate: '2026-12-31T23:59',
    })

    expect(result.success).toBe(true)
  })

  it('surfaces custom error message for title exceeding max length', () => {
    const result = EditedTodoFormValuesSchema.safeParse({
      title: 'x'.repeat(256),
    })

    expect(result.success).toBe(false)
    if (!result.success) {
      const titleError = result.error.issues.find((issue) =>
        issue.path.includes('title')
      )
      expect(titleError?.message).toBe('Title cannot exceed 255 characters')
    }
  })

  it('rejects completing without description', () => {
    const result = EditedTodoFormValuesSchema.safeParse({
      isCompleted: true,
    })

    expect(result.success).toBe(false)
    if (!result.success) {
      const descriptionError = result.error.issues.find((issue) =>
        issue.path.includes('description')
      )
      expect(descriptionError?.message).toBe(
        'Description is required when completing a todo'
      )
    }
  })

  it('rejects high priority without due date', () => {
    const result = EditedTodoFormValuesSchema.safeParse({
      priority: 'high',
    })

    expect(result.success).toBe(false)
    if (!result.success) {
      const dueDateError = result.error.issues.find((issue) =>
        issue.path.includes('dueDate')
      )
      expect(dueDateError?.message).toBe(
        'Due date is required for high-priority todos'
      )
    }
  })
})
