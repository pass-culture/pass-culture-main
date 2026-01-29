import { render, screen, waitFor } from '@testing-library/react'
import { userEvent } from '@testing-library/user-event'
import { describe, expect, it, vi } from 'vitest'

import type { PokeTodoResponseModel } from '@/apiClient/hey-api'

import { PokeTodoForm } from './PokeTodoForm'

function buildTodo(
  overrides: Partial<PokeTodoResponseModel> = {}
): PokeTodoResponseModel {
  return {
    id: 1,
    title: 'Existing todo',
    description: 'Existing description',
    priority: 'medium',
    dueDate: null,
    isCompleted: false,
    dateCreated: '2026-01-01T00:00:00',
    dateUpdated: null,
    ...overrides,
  }
}

describe('PokeTodoForm', () => {
  describe('create mode', () => {
    it('renders create form when not editing', () => {
      render(
        <PokeTodoForm
          editingTodo={null}
          onSubmitCreate={vi.fn()}
          onSubmitUpdate={vi.fn()}
          onCancelEdit={vi.fn()}
        />
      )

      expect(screen.getByText('New Todo')).toBeInTheDocument()
      expect(screen.getByLabelText('Title')).toBeInTheDocument()
      expect(screen.getByLabelText('Description')).toBeInTheDocument()
      expect(screen.getByLabelText('Priority')).toBeInTheDocument()
      expect(screen.getByLabelText('Due Date')).toBeInTheDocument()
      expect(screen.getByRole('button', { name: 'Create' })).toBeInTheDocument()
    })

    it('calls onSubmitCreate with form values', async () => {
      const onSubmitCreate = vi.fn().mockResolvedValue(undefined)
      render(
        <PokeTodoForm
          editingTodo={null}
          onSubmitCreate={onSubmitCreate}
          onSubmitUpdate={vi.fn()}
          onCancelEdit={vi.fn()}
        />
      )

      await userEvent.type(screen.getByLabelText('Title'), 'New task')
      await userEvent.type(screen.getByLabelText('Description'), 'Task details')
      await userEvent.click(screen.getByRole('button', { name: 'Create' }))

      await waitFor(() => {
        expect(onSubmitCreate).toHaveBeenCalledWith(
          expect.objectContaining({
            title: 'New task',
            description: 'Task details',
          })
        )
      })
    })

    it('shows validation error when title exceeds max length', async () => {
      const onSubmitCreate = vi.fn()
      render(
        <PokeTodoForm
          editingTodo={null}
          onSubmitCreate={onSubmitCreate}
          onSubmitUpdate={vi.fn()}
          onCancelEdit={vi.fn()}
        />
      )

      const longTitle = 'x'.repeat(256)
      await userEvent.type(screen.getByLabelText('Title'), longTitle)
      await userEvent.click(screen.getByRole('button', { name: 'Create' }))

      await waitFor(() => {
        expect(screen.getByRole('alert')).toBeInTheDocument()
      })
      expect(onSubmitCreate).not.toHaveBeenCalled()
    })

    it('shows validation error when high priority without due date', async () => {
      const onSubmitCreate = vi.fn()
      render(
        <PokeTodoForm
          editingTodo={null}
          onSubmitCreate={onSubmitCreate}
          onSubmitUpdate={vi.fn()}
          onCancelEdit={vi.fn()}
        />
      )

      await userEvent.type(screen.getByLabelText('Title'), 'Urgent task')
      await userEvent.selectOptions(screen.getByLabelText('Priority'), 'high')
      await userEvent.click(screen.getByRole('button', { name: 'Create' }))

      await waitFor(() => {
        expect(
          screen.getByText('Due date is required for high-priority todos')
        ).toBeInTheDocument()
      })
      expect(onSubmitCreate).not.toHaveBeenCalled()
    })

    it('shows validation error when low priority with due date', async () => {
      const onSubmitCreate = vi.fn()
      render(
        <PokeTodoForm
          editingTodo={null}
          onSubmitCreate={onSubmitCreate}
          onSubmitUpdate={vi.fn()}
          onCancelEdit={vi.fn()}
        />
      )

      await userEvent.type(screen.getByLabelText('Title'), 'Chill task')
      const dueDateInput = screen.getByLabelText('Due Date')
      await userEvent.type(dueDateInput, '2026-12-31T23:59')
      await userEvent.click(screen.getByRole('button', { name: 'Create' }))

      await waitFor(() => {
        expect(
          screen.getByText('Low-priority todos cannot have a due date')
        ).toBeInTheDocument()
      })
      expect(onSubmitCreate).not.toHaveBeenCalled()
    })

    it('submits with priority and due date', async () => {
      const onSubmitCreate = vi.fn().mockResolvedValue(undefined)
      render(
        <PokeTodoForm
          editingTodo={null}
          onSubmitCreate={onSubmitCreate}
          onSubmitUpdate={vi.fn()}
          onCancelEdit={vi.fn()}
        />
      )

      await userEvent.type(screen.getByLabelText('Title'), 'Urgent task')
      await userEvent.selectOptions(screen.getByLabelText('Priority'), 'high')
      const dueDateInput = screen.getByLabelText('Due Date')
      await userEvent.type(dueDateInput, '2026-12-31T23:59')
      await userEvent.click(screen.getByRole('button', { name: 'Create' }))

      await waitFor(() => {
        expect(onSubmitCreate).toHaveBeenCalledWith(
          expect.objectContaining({
            title: 'Urgent task',
            priority: 'high',
            dueDate: '2026-12-31T23:59:00Z',
          })
        )
      })
    })
  })

  describe('edit mode', () => {
    it('renders edit form with pre-filled values', () => {
      const todo = buildTodo({
        title: 'My task',
        description: 'My details',
        priority: 'medium',
      })
      render(
        <PokeTodoForm
          editingTodo={todo}
          onSubmitCreate={vi.fn()}
          onSubmitUpdate={vi.fn()}
          onCancelEdit={vi.fn()}
        />
      )

      expect(screen.getByText('Edit Todo')).toBeInTheDocument()
      expect(screen.getByLabelText('Title')).toHaveValue('My task')
      expect(screen.getByLabelText('Description')).toHaveValue('My details')
      expect(screen.getByLabelText('Priority')).toHaveValue('medium')
      expect(screen.getByRole('button', { name: 'Save' })).toBeInTheDocument()
      expect(screen.getByRole('button', { name: 'Cancel' })).toBeInTheDocument()
    })

    it('renders isCompleted checkbox in edit mode', () => {
      const todo = buildTodo({ isCompleted: false })
      render(
        <PokeTodoForm
          editingTodo={todo}
          onSubmitCreate={vi.fn()}
          onSubmitUpdate={vi.fn()}
          onCancelEdit={vi.fn()}
        />
      )

      expect(screen.getByText('Mark as completed')).toBeInTheDocument()
      expect(screen.getByRole('checkbox')).not.toBeChecked()
    })

    it('calls onSubmitUpdate with updated values', async () => {
      const onSubmitUpdate = vi.fn().mockResolvedValue(undefined)
      const todo = buildTodo({ id: 5, title: 'Old title' })
      render(
        <PokeTodoForm
          editingTodo={todo}
          onSubmitCreate={vi.fn()}
          onSubmitUpdate={onSubmitUpdate}
          onCancelEdit={vi.fn()}
        />
      )

      const titleInput = screen.getByLabelText('Title')
      await userEvent.clear(titleInput)
      await userEvent.type(titleInput, 'Updated title')
      await userEvent.click(screen.getByRole('button', { name: 'Save' }))

      await waitFor(() => {
        expect(onSubmitUpdate).toHaveBeenCalledWith(
          5,
          expect.objectContaining({ title: 'Updated title' })
        )
      })
    })

    it('shows validation error when completing without description', async () => {
      const onSubmitUpdate = vi.fn()
      const todo = buildTodo({ description: null })
      render(
        <PokeTodoForm
          editingTodo={todo}
          onSubmitCreate={vi.fn()}
          onSubmitUpdate={onSubmitUpdate}
          onCancelEdit={vi.fn()}
        />
      )

      await userEvent.click(screen.getByRole('checkbox'))
      await userEvent.click(screen.getByRole('button', { name: 'Save' }))

      await waitFor(() => {
        expect(
          screen.getByText('Description is required when completing a todo')
        ).toBeInTheDocument()
      })
      expect(onSubmitUpdate).not.toHaveBeenCalled()
    })

    it('calls onCancelEdit when cancel button is clicked', async () => {
      const onCancelEdit = vi.fn()
      const todo = buildTodo()
      render(
        <PokeTodoForm
          editingTodo={todo}
          onSubmitCreate={vi.fn()}
          onSubmitUpdate={vi.fn()}
          onCancelEdit={onCancelEdit}
        />
      )

      await userEvent.click(screen.getByRole('button', { name: 'Cancel' }))
      expect(onCancelEdit).toHaveBeenCalled()
    })
  })
})
