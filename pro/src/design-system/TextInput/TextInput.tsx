import classNames from 'classnames'
import { useId } from 'react'

import styles from './TextInput.module.scss'

type TextInputProps = {
  label: string
  type?: 'text' | 'search'
  disabled?: boolean
  description?: string
  error?: string
}

export function TextInput({
  label,
  type = 'text',
  disabled = false,
  description,
  error,
}: TextInputProps) {
  const inputId = useId()
  const descriptionId = useId()
  const errorId = useId()

  const describedBy = `${description ? descriptionId : ''} ${error ? errorId : ''}`

  return (
    <div
      className={classNames(styles['container'], {
        [styles['is-disabled']]: disabled,
        [styles['has-error']]: Boolean(error),
        [styles['has-description']]: Boolean(description),
      })}
    >
      <label htmlFor={inputId} className={styles['label']}>
        {label}
      </label>
      {description && (
        <p id={descriptionId} className={styles['description']}>
          {description}
        </p>
      )}
      <input
        className={styles['input']}
        id={inputId}
        /*         type={type} */
        disabled={disabled}
        aria-describedby={describedBy}
        aria-invalid={Boolean(error)}
        type="number"
      />
      <div role="alert">
        {error && (
          <p id={errorId} className={styles['error']}>
            {error}
          </p>
        )}
      </div>
    </div>
  )
}
