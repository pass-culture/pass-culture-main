import { render, screen, waitFor } from '@testing-library/react'
import { userEvent } from '@testing-library/user-event'
import { SWRConfig } from 'swr'
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'

import type { PokeTodoResponseModel } from '@/apiClient/hey-api'

const MOCK_TODO: PokeTodoResponseModel = {
  id: 1,
  title: 'Test todo',
  description: 'Test description',
  priority: 'medium',
  dueDate: null,
  isCompleted: false,
  dateCreated: '2026-01-01T00:00:00',
  dateUpdated: null,
}

const MOCK_TODOS: PokeTodoResponseModel[] = [
  MOCK_TODO,
  {
    id: 2,
    title: 'Second todo',
    description: null,
    priority: 'high',
    dueDate: '2026-06-15T12:00:00Z',
    isCompleted: true,
    dateCreated: '2026-01-02T00:00:00',
    dateUpdated: null,
  },
]

function createFetchMock(responses: Array<{ status: number; body?: unknown }>) {
  const queue = [...responses]
  return vi.fn().mockImplementation(() => {
    const response = queue.shift() ?? { status: 500 }
    return Promise.resolve({
      ok: response.status >= 200 && response.status < 300,
      status: response.status,
      json: () => Promise.resolve(response.body),
    })
  })
}

function renderWithSWR(component: React.ReactElement) {
  return render(
    <SWRConfig value={{ provider: () => new Map(), dedupingInterval: 0 }}>
      {component}
    </SWRConfig>
  )
}

describe('PokeTodoPage', () => {
  const originalFetch = global.fetch

  beforeEach(() => {
    vi.resetModules()
  })

  afterEach(() => {
    global.fetch = originalFetch
  })

  it('renders page title and loads todos', async () => {
    global.fetch = createFetchMock([{ status: 200, body: [] }])

    const { Component } = await import('./PokeTodoPage')
    renderWithSWR(<Component />)

    await waitFor(() => {
      expect(screen.getByText('Todos (0)')).toBeInTheDocument()
    })

    expect(screen.getByText('Poke Todo')).toBeInTheDocument()
  })

  it('renders todos after loading', async () => {
    global.fetch = createFetchMock([{ status: 200, body: MOCK_TODOS }])

    const { Component } = await import('./PokeTodoPage')
    renderWithSWR(<Component />)

    await waitFor(() => {
      expect(screen.getByText('Test todo')).toBeInTheDocument()
    })
    expect(screen.getByText('Second todo')).toBeInTheDocument()
    expect(screen.getByText('Todos (2)')).toBeInTheDocument()
  })

  it('renders empty state when no todos', async () => {
    global.fetch = createFetchMock([{ status: 200, body: [] }])

    const { Component } = await import('./PokeTodoPage')
    renderWithSWR(<Component />)

    await waitFor(() => {
      expect(
        screen.getByText('No todos yet. Create one above!')
      ).toBeInTheDocument()
    })
  })

  it('shows error when loading fails', async () => {
    global.fetch = createFetchMock([{ status: 500 }])

    const { Component } = await import('./PokeTodoPage')
    renderWithSWR(<Component />)

    await waitFor(() => {
      expect(screen.getByRole('alert')).toHaveTextContent(
        'Failed to load todos'
      )
    })
  })

  it('creates a new todo', async () => {
    global.fetch = createFetchMock([
      { status: 200, body: [] },
      { status: 201, body: { ...MOCK_TODO, id: 3, title: 'New task' } },
      { status: 200, body: [{ ...MOCK_TODO, id: 3, title: 'New task' }] },
    ])

    const { Component } = await import('./PokeTodoPage')
    renderWithSWR(<Component />)

    await waitFor(() => {
      expect(screen.getByText('New Todo')).toBeInTheDocument()
    })

    await userEvent.type(screen.getByLabelText('Title'), 'New task')
    await userEvent.click(screen.getByRole('button', { name: 'Create' }))

    await waitFor(() => {
      expect(screen.getByText('New task')).toBeInTheDocument()
    })
  })

  it('deletes a todo', async () => {
    global.fetch = createFetchMock([
      { status: 200, body: [MOCK_TODO] },
      { status: 204 },
      { status: 200, body: [] },
    ])

    const { Component } = await import('./PokeTodoPage')
    renderWithSWR(<Component />)

    await waitFor(() => {
      expect(screen.getByText('Test todo')).toBeInTheDocument()
    })

    await userEvent.click(screen.getByLabelText('Delete "Test todo"'))

    await waitFor(() => {
      expect(
        screen.getByText('No todos yet. Create one above!')
      ).toBeInTheDocument()
    })
  })

  it('toggles todo completion', async () => {
    const toggledTodo = { ...MOCK_TODO, isCompleted: true }
    global.fetch = createFetchMock([
      { status: 200, body: [MOCK_TODO] },
      { status: 200, body: toggledTodo },
      { status: 200, body: [toggledTodo] },
    ])

    const { Component } = await import('./PokeTodoPage')
    renderWithSWR(<Component />)

    await waitFor(() => {
      expect(screen.getByRole('checkbox')).not.toBeChecked()
    })

    await userEvent.click(screen.getByRole('checkbox'))

    await waitFor(() => {
      expect(screen.getByRole('checkbox')).toBeChecked()
    })
  })
})
