import cn from 'classnames'
import { useField } from 'formik'
import React from 'react'

import FieldError from '../FieldError'

import styles from './Checkbox.module.scss'

interface ICheckboxProps {
  name: string
  value: string
  label: string
  className?: string
}

const Checkbox = ({
  name,
  value,
  label,
  className,
}: ICheckboxProps): JSX.Element => {
  const [field, meta] = useField({ name, type: 'checkbox' })

  return (
    <div className={cn(styles['checkbox'], className)}>
      <label
        className={cn(styles['checkbox-label'], {
          [styles['has-error']]: meta.touched && !!meta.error,
        })}
      >
        <input
          {...field}
          className={styles['checkbox-input']}
          type="checkbox"
          value={value}
        />

        {label}
      </label>

      {meta.touched && !!meta.error && <FieldError>{meta.error}</FieldError>}
    </div>
  )
}

export default Checkbox
