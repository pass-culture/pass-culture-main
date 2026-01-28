import { render, screen } from '@testing-library/react'
import { userEvent } from '@testing-library/user-event'
import { describe, expect, it, vi } from 'vitest'

import type { PokeTodoResponseModel } from '@/apiClient/hey-api'

import { PokeTodoItem } from './PokeTodoItem'

function buildTodo(
  overrides: Partial<PokeTodoResponseModel> = {}
): PokeTodoResponseModel {
  return {
    id: 1,
    title: 'Test todo',
    description: null,
    priority: 'low',
    dueDate: null,
    isCompleted: false,
    dateCreated: '2026-01-01T00:00:00',
    dateUpdated: null,
    ...overrides,
  }
}

describe('PokeTodoItem', () => {
  it('renders todo title', () => {
    const todo = buildTodo({ title: 'My task' })
    render(
      <PokeTodoItem
        todo={todo}
        onToggle={vi.fn()}
        onDelete={vi.fn()}
        onEdit={vi.fn()}
      />
    )

    expect(screen.getByText('My task')).toBeInTheDocument()
  })

  it('renders todo description when present', () => {
    const todo = buildTodo({ description: 'Some details' })
    render(
      <PokeTodoItem
        todo={todo}
        onToggle={vi.fn()}
        onDelete={vi.fn()}
        onEdit={vi.fn()}
      />
    )

    expect(screen.getByText('Some details')).toBeInTheDocument()
  })

  it('does not render description when null', () => {
    const todo = buildTodo({ description: null })
    render(
      <PokeTodoItem
        todo={todo}
        onToggle={vi.fn()}
        onDelete={vi.fn()}
        onEdit={vi.fn()}
      />
    )

    expect(screen.queryByText('Some details')).not.toBeInTheDocument()
  })

  it('renders checkbox as checked when completed', () => {
    const todo = buildTodo({ isCompleted: true })
    render(
      <PokeTodoItem
        todo={todo}
        onToggle={vi.fn()}
        onDelete={vi.fn()}
        onEdit={vi.fn()}
      />
    )

    const checkbox = screen.getByRole('checkbox')
    expect(checkbox).toBeChecked()
  })

  it('renders checkbox as unchecked when not completed', () => {
    const todo = buildTodo({ isCompleted: false })
    render(
      <PokeTodoItem
        todo={todo}
        onToggle={vi.fn()}
        onDelete={vi.fn()}
        onEdit={vi.fn()}
      />
    )

    const checkbox = screen.getByRole('checkbox')
    expect(checkbox).not.toBeChecked()
  })

  it('calls onToggle when checkbox is clicked', async () => {
    const onToggle = vi.fn()
    const todo = buildTodo({ id: 42 })
    render(
      <PokeTodoItem
        todo={todo}
        onToggle={onToggle}
        onDelete={vi.fn()}
        onEdit={vi.fn()}
      />
    )

    await userEvent.click(screen.getByRole('checkbox'))
    expect(onToggle).toHaveBeenCalledWith(42)
  })

  it('calls onDelete when delete button is clicked', async () => {
    const onDelete = vi.fn()
    const todo = buildTodo({ id: 7, title: 'A task' })
    render(
      <PokeTodoItem
        todo={todo}
        onToggle={vi.fn()}
        onDelete={onDelete}
        onEdit={vi.fn()}
      />
    )

    await userEvent.click(screen.getByLabelText('Delete "A task"'))
    expect(onDelete).toHaveBeenCalledWith(7)
  })

  it('calls onEdit when edit button is clicked', async () => {
    const onEdit = vi.fn()
    const todo = buildTodo({ title: 'Editable' })
    render(
      <PokeTodoItem
        todo={todo}
        onToggle={vi.fn()}
        onDelete={vi.fn()}
        onEdit={onEdit}
      />
    )

    await userEvent.click(screen.getByLabelText('Edit "Editable"'))
    expect(onEdit).toHaveBeenCalledWith(todo)
  })

  it('renders priority badge', () => {
    const todo = buildTodo({ priority: 'high' })
    render(
      <PokeTodoItem
        todo={todo}
        onToggle={vi.fn()}
        onDelete={vi.fn()}
        onEdit={vi.fn()}
      />
    )

    const badge = screen.getByTestId('priority-badge')
    expect(badge).toHaveTextContent('high')
  })

  it('renders due date when present', () => {
    const todo = buildTodo({ dueDate: '2026-12-31T23:59:00Z' })
    render(
      <PokeTodoItem
        todo={todo}
        onToggle={vi.fn()}
        onDelete={vi.fn()}
        onEdit={vi.fn()}
      />
    )

    const dueDate = screen.getByTestId('due-date')
    expect(dueDate).toHaveTextContent('Due:')
    expect(dueDate).toHaveTextContent('Dec')
    expect(dueDate).toHaveTextContent('2026')
  })

  it('does not render due date when null', () => {
    const todo = buildTodo({ dueDate: null })
    render(
      <PokeTodoItem
        todo={todo}
        onToggle={vi.fn()}
        onDelete={vi.fn()}
        onEdit={vi.fn()}
      />
    )

    expect(screen.queryByTestId('due-date')).not.toBeInTheDocument()
  })
})
