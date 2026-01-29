import type { PokeTodoResponseModel } from '@/apiClient/hey-api'

import styles from './PokeTodoItem.module.scss'

interface PokeTodoItemProps {
  todo: PokeTodoResponseModel
  onToggle: (id: number) => void
  onDelete: (id: number) => void
  onEdit: (todo: PokeTodoResponseModel) => void
}

function formatDueDate(isoDatetime: string): string {
  const date = new Date(isoDatetime)
  return date.toLocaleDateString(undefined, {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  })
}

export function PokeTodoItem({
  todo,
  onToggle,
  onDelete,
  onEdit,
}: PokeTodoItemProps) {
  return (
    <li className={styles['todo-item']} data-testid={`todo-item-${todo.id}`}>
      <div className={styles['todo-content']}>
        <label className={styles['todo-checkbox']}>
          <input
            type="checkbox"
            checked={todo.isCompleted}
            onChange={() => onToggle(todo.id)}
            aria-label={`Mark "${todo.title}" as ${todo.isCompleted ? 'incomplete' : 'complete'}`}
          />
          <span
            className={
              todo.isCompleted
                ? styles['todo-title-completed']
                : styles['todo-title']
            }
          >
            {todo.title}
          </span>
        </label>
        <div className={styles['todo-meta']}>
          <span
            className={styles[`priority-${todo.priority}`]}
            data-testid="priority-badge"
          >
            {todo.priority}
          </span>
          {todo.dueDate && (
            <span className={styles['due-date']} data-testid="due-date">
              Due: {formatDueDate(todo.dueDate)}
            </span>
          )}
        </div>
        {todo.description && (
          <p className={styles['todo-description']}>{todo.description}</p>
        )}
      </div>
      <div className={styles['todo-actions']}>
        <button
          type="button"
          className={styles['action-button']}
          onClick={() => onEdit(todo)}
          aria-label={`Edit "${todo.title}"`}
        >
          Edit
        </button>
        <button
          type="button"
          className={styles['action-button-danger']}
          onClick={() => onDelete(todo.id)}
          aria-label={`Delete "${todo.title}"`}
        >
          Delete
        </button>
      </div>
    </li>
  )
}
