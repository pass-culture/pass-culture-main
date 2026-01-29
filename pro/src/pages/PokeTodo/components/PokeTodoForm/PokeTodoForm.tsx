import { zodResolver } from '@hookform/resolvers/zod'
import { useEffect, useId } from 'react'
import { useForm } from 'react-hook-form'

import type { PokeTodoResponseModel } from '@/apiClient/hey-api'

import { TextField } from '../../fields/TextField'
import {
  type EditedTodoFormInput,
  type EditedTodoFormValues,
  EditedTodoFormValuesSchema,
  type NewTodoFormInput,
  type NewTodoFormValues,
  NewTodoFormValuesSchema,
} from '../../utils/schemas'
import { toIsoDatetime } from '../../utils/toIsoDatetime'
import styles from './PokeTodoForm.module.scss'

interface PokeTodoFormProps {
  editingTodo: PokeTodoResponseModel | null
  onSubmitCreate: (values: NewTodoFormValues) => Promise<void>
  onSubmitUpdate: (id: number, values: EditedTodoFormValues) => Promise<void>
  onCancelEdit: () => void
}
export function PokeTodoForm({
  editingTodo,
  onSubmitCreate,
  onSubmitUpdate,
  onCancelEdit,
}: PokeTodoFormProps) {
  const titleFieldId = useId()
  const descriptionFieldId = useId()
  const priorityFieldId = useId()
  const dueDateFieldId = useId()

  const isEditing = editingTodo !== null

  const createForm = useForm<NewTodoFormInput, unknown, NewTodoFormValues>({
    resolver: zodResolver(NewTodoFormValuesSchema),
    defaultValues: {
      title: '',
      description: null,
      priority: 'low',
      dueDate: null,
    },
    mode: 'onTouched',
  })

  const updateForm = useForm<
    EditedTodoFormInput,
    unknown,
    EditedTodoFormValues
  >({
    resolver: zodResolver(EditedTodoFormValuesSchema),
    defaultValues: {
      title: null,
      description: null,
      priority: null,
      dueDate: null,
      isCompleted: null,
    },
    mode: 'onTouched',
  })

  useEffect(() => {
    if (editingTodo) {
      updateForm.reset({
        title: editingTodo.title,
        description: editingTodo.description,
        priority: editingTodo.priority,
        dueDate: editingTodo.dueDate?.replace('Z', '').slice(0, 16) ?? null,
        isCompleted: editingTodo.isCompleted,
      })
    }
  }, [editingTodo, updateForm])

  async function handleCreateSubmit(values: NewTodoFormValues) {
    await onSubmitCreate({
      ...values,
      dueDate: toIsoDatetime(values.dueDate ?? null),
    })
    createForm.reset()
  }

  async function handleUpdateSubmit(values: EditedTodoFormValues) {
    if (editingTodo) {
      await onSubmitUpdate(editingTodo.id, {
        ...values,
        dueDate: toIsoDatetime(values.dueDate ?? null),
      })
    }
  }

  if (isEditing) {
    return (
      <form
        className={styles['todo-form']}
        onSubmit={updateForm.handleSubmit(handleUpdateSubmit)}
        data-testid="todo-update-form"
      >
        <h2>Edit Todo</h2>
        <TextField
          aria-invalid={!!updateForm.formState.errors.title}
          error={updateForm.formState.errors.title?.message}
          label="Title"
          {...updateForm.register('title')}
        />
        <div className={styles['form-field']}>
          <label htmlFor={descriptionFieldId}>Description</label>
          <textarea
            id={descriptionFieldId}
            {...updateForm.register('description')}
            aria-invalid={!!updateForm.formState.errors.description}
          />
          {updateForm.formState.errors.description && (
            <p className={styles['field-error']} role="alert">
              {updateForm.formState.errors.description.message}
            </p>
          )}
        </div>
        <div className={styles['form-row']}>
          <div className={styles['form-field']}>
            <label htmlFor={priorityFieldId}>Priority</label>
            <select
              id={priorityFieldId}
              {...updateForm.register('priority')}
              aria-invalid={!!updateForm.formState.errors.priority}
            >
              <option value="low">Low</option>
              <option value="medium">Medium</option>
              <option value="high">High</option>
            </select>
            {updateForm.formState.errors.priority && (
              <p className={styles['field-error']} role="alert">
                {updateForm.formState.errors.priority.message}
              </p>
            )}
          </div>
          <div className={styles['form-field']}>
            <label htmlFor={dueDateFieldId}>Due Date</label>
            <input
              id={dueDateFieldId}
              type="datetime-local"
              {...updateForm.register('dueDate')}
              aria-invalid={!!updateForm.formState.errors.dueDate}
            />
            {updateForm.formState.errors.dueDate && (
              <p className={styles['field-error']} role="alert">
                {updateForm.formState.errors.dueDate.message}
              </p>
            )}
          </div>
        </div>

        <div className={styles['form-field']}>
          <label className={styles['checkbox-label']}>
            <input type="checkbox" {...updateForm.register('isCompleted')} />
            Mark as completed
          </label>
        </div>

        <div className={styles['form-actions']}>
          <button type="submit" className={styles['submit-button']}>
            Save
          </button>
          <button
            type="button"
            className={styles['cancel-button']}
            onClick={onCancelEdit}
          >
            Cancel
          </button>
        </div>
      </form>
    )
  }

  return (
    <form
      className={styles['todo-form']}
      onSubmit={createForm.handleSubmit(handleCreateSubmit)}
      data-testid="todo-create-form"
    >
      <h2>New Todo</h2>
      <div className={styles['form-field']}>
        <label htmlFor={titleFieldId}>Title</label>
        <input
          id={titleFieldId}
          type="text"
          {...createForm.register('title')}
          aria-invalid={!!createForm.formState.errors.title}
        />
        {createForm.formState.errors.title && (
          <p className={styles['field-error']} role="alert">
            {createForm.formState.errors.title.message}
          </p>
        )}
      </div>
      <div className={styles['form-field']}>
        <label htmlFor={descriptionFieldId}>Description</label>
        <textarea
          id={descriptionFieldId}
          {...createForm.register('description')}
        />
      </div>
      <div className={styles['form-row']}>
        <div className={styles['form-field']}>
          <label htmlFor={priorityFieldId}>Priority</label>
          <select
            id={priorityFieldId}
            {...createForm.register('priority')}
            aria-invalid={!!createForm.formState.errors.priority}
          >
            <option value="low">Low</option>
            <option value="medium">Medium</option>
            <option value="high">High</option>
          </select>
          {createForm.formState.errors.priority && (
            <p className={styles['field-error']} role="alert">
              {createForm.formState.errors.priority.message}
            </p>
          )}
        </div>
        <div className={styles['form-field']}>
          <label htmlFor={dueDateFieldId}>Due Date</label>
          <input
            id={dueDateFieldId}
            type="datetime-local"
            {...createForm.register('dueDate')}
            aria-invalid={!!createForm.formState.errors.dueDate}
          />
          {createForm.formState.errors.dueDate && (
            <p className={styles['field-error']} role="alert">
              {createForm.formState.errors.dueDate.message}
            </p>
          )}
        </div>
      </div>

      <button type="submit" className={styles['submit-button']}>
        Create
      </button>
    </form>
  )
}
