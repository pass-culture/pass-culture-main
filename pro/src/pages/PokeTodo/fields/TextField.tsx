import { forwardRef, type InputHTMLAttributes, useId } from 'react'

import styles from './fields.module.scss'

interface TextFieldProps extends InputHTMLAttributes<HTMLInputElement> {
  error: string | undefined
  label: string
  onChange: (event: React.ChangeEvent<{ value: string | null }>) => void
}

export const TextField = forwardRef<HTMLInputElement, Readonly<TextFieldProps>>(
  ({ error, label, onChange, ...rest }, ref) => {
    const id = useId()

    const handleOnChange = (event: React.ChangeEvent<HTMLInputElement>) => {
      onChange?.(
        Object.assign(event, {
          target: { value: event.target.value?.trim() ?? null },
        })
      )
    }

    return (
      <div className={styles['form-field']}>
        <label htmlFor={id}>{label}</label>
        <input
          ref={ref}
          id={id}
          onChange={handleOnChange}
          type="text"
          {...rest}
        />
        {error && (
          <p className={styles['field-error']} role="alert">
            {error}
          </p>
        )}
      </div>
    )
  }
)
