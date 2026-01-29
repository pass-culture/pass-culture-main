import type { PokeTodoResponseModel } from '@/apiClient/hey-api'

import { PokeTodoItem } from '../PokeTodoItem/PokeTodoItem'
import styles from './PokeTodoList.module.scss'

interface PokeTodoListProps {
  todos: PokeTodoResponseModel[]
  onToggle: (id: number) => void
  onDelete: (id: number) => void
  onEdit: (todo: PokeTodoResponseModel) => void
}

export function PokeTodoList({
  todos,
  onToggle,
  onDelete,
  onEdit,
}: PokeTodoListProps) {
  if (todos.length === 0) {
    return (
      <p className={styles['empty-message']}>No todos yet. Create one above!</p>
    )
  }

  return (
    <ul className={styles['todo-list']}>
      {todos.map((todo) => (
        <PokeTodoItem
          key={todo.id}
          todo={todo}
          onToggle={onToggle}
          onDelete={onDelete}
          onEdit={onEdit}
        />
      ))}
    </ul>
  )
}
