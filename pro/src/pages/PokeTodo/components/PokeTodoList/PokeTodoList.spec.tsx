import { render, screen } from '@testing-library/react'
import { describe, expect, it, vi } from 'vitest'

import type { PokeTodoResponseModel } from '@/apiClient/hey-api'

import { PokeTodoList } from './PokeTodoList'

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

describe('PokeTodoList', () => {
  it('renders empty message when no todos', () => {
    render(
      <PokeTodoList
        todos={[]}
        onToggle={vi.fn()}
        onDelete={vi.fn()}
        onEdit={vi.fn()}
      />
    )

    expect(
      screen.getByText('No todos yet. Create one above!')
    ).toBeInTheDocument()
  })

  it('renders all todos', () => {
    const todos = [
      buildTodo({ id: 1, title: 'First' }),
      buildTodo({ id: 2, title: 'Second' }),
    ]
    render(
      <PokeTodoList
        todos={todos}
        onToggle={vi.fn()}
        onDelete={vi.fn()}
        onEdit={vi.fn()}
      />
    )

    expect(screen.getByText('First')).toBeInTheDocument()
    expect(screen.getByText('Second')).toBeInTheDocument()
  })

  it('does not render empty message when todos exist', () => {
    const todos = [buildTodo()]
    render(
      <PokeTodoList
        todos={todos}
        onToggle={vi.fn()}
        onDelete={vi.fn()}
        onEdit={vi.fn()}
      />
    )

    expect(
      screen.queryByText('No todos yet. Create one above!')
    ).not.toBeInTheDocument()
  })
})
