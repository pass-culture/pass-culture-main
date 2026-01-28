import { useState } from 'react'
import useSWR from 'swr'

import type { PokeTodoResponseModel } from '@/apiClient/hey-api'

import { PokeTodoForm } from './components/PokeTodoForm/PokeTodoForm'
import { PokeTodoList } from './components/PokeTodoList/PokeTodoList'
import styles from './PokeTodoPage.module.scss'
import type { EditedTodoFormValues, NewTodoFormValues } from './utils/schemas'

const API_BASE_URL = 'http://localhost:5001'
const POKE_TODOS_KEY = 'pokeTodos'

async function fetchTodos(): Promise<PokeTodoResponseModel[]> {
  const response = await fetch(`${API_BASE_URL}/poke-todos`)
  if (!response.ok) {
    throw new Error('Failed to fetch todos')
  }
  return response.json()
}

async function createTodoRequest(
  body: NewTodoFormValues
): Promise<PokeTodoResponseModel> {
  const response = await fetch(`${API_BASE_URL}/poke-todos`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  })
  if (!response.ok) {
    throw new Error('Failed to create todo')
  }
  return response.json()
}

async function updateTodoRequest(
  id: number,
  body: Partial<EditedTodoFormValues>
): Promise<PokeTodoResponseModel> {
  const response = await fetch(`${API_BASE_URL}/poke-todos/${id}`, {
    method: 'PATCH',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  })
  if (!response.ok) {
    throw new Error('Failed to update todo')
  }
  return response.json()
}

async function deleteTodoRequest(id: number): Promise<void> {
  const response = await fetch(`${API_BASE_URL}/poke-todos/${id}`, {
    method: 'DELETE',
  })
  if (!response.ok) {
    throw new Error('Failed to delete todo')
  }
}

function PokeTodoPage() {
  const {
    data: todos = [],
    error: loadError,
    mutate: mutateTodos,
  } = useSWR<PokeTodoResponseModel[]>(POKE_TODOS_KEY, fetchTodos)
  const [mutationError, setMutationError] = useState<string | null>(null)
  const [editingTodo, setEditingTodo] = useState<PokeTodoResponseModel | null>(
    null
  )

  const displayError =
    mutationError ?? (loadError ? 'Failed to load todos' : null)

  async function handleCreate(values: NewTodoFormValues) {
    try {
      setMutationError(null)
      await createTodoRequest(values)
      await mutateTodos()
    } catch {
      setMutationError('Failed to create todo')
    }
  }

  async function handleUpdate(id: number, values: EditedTodoFormValues) {
    try {
      setMutationError(null)
      await updateTodoRequest(id, values)
      setEditingTodo(null)
      await mutateTodos()
    } catch {
      setMutationError('Failed to update todo')
    }
  }

  async function handleToggle(id: number) {
    const todo = todos.find((t) => t.id === id)
    if (!todo) {
      return
    }

    try {
      setMutationError(null)
      await updateTodoRequest(id, { isCompleted: !todo.isCompleted })
      await mutateTodos()
    } catch {
      setMutationError('Failed to toggle todo')
    }
  }

  async function handleDelete(id: number) {
    try {
      setMutationError(null)
      await deleteTodoRequest(id)
      await mutateTodos()
    } catch {
      setMutationError('Failed to delete todo')
    }
  }

  function handleEdit(todo: PokeTodoResponseModel) {
    setEditingTodo(todo)
  }

  function handleCancelEdit() {
    setEditingTodo(null)
  }

  return (
    <div className={styles['page-container']}>
      <header className={styles['page-header']}>
        <h1>Poke Todo</h1>
        <p className={styles['page-subtitle']}>
          Pydantic v2 &rarr; OpenAPI &rarr; Zod schema generation demo
        </p>
      </header>

      {displayError && (
        <div className={styles['error-banner']} role="alert">
          {displayError}
        </div>
      )}

      <PokeTodoForm
        editingTodo={editingTodo}
        onSubmitCreate={handleCreate}
        onSubmitUpdate={handleUpdate}
        onCancelEdit={handleCancelEdit}
      />

      <section className={styles['list-section']}>
        <h2>Todos ({todos.length})</h2>
        <PokeTodoList
          todos={todos}
          onToggle={handleToggle}
          onDelete={handleDelete}
          onEdit={handleEdit}
        />
      </section>
    </div>
  )
}

// ts-unused-exports:disable-next-line
export const Component = PokeTodoPage
