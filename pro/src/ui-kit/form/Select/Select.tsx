import cn from 'classnames'
import { useField } from 'formik'
import React, { useEffect } from 'react'

import FieldError from '../FieldError'

import styles from './Select.module.scss'

type Option = {
  value: string
  label: string
}

interface ISelectProps {
  name: string
  options: Option[]
  className?: string
  disabled?: boolean
  label?: string
}

const Select = ({
  name,
  options,
  className,
  disabled,
  label,
}: ISelectProps): JSX.Element => {
  const [field, meta, helpers] = useField({ name, type: 'select' })

  useEffect(() => {
    if (options.length === 1 && field.value !== options[0].value) {
      helpers.setValue(options[0].value)
    }
  }, [options, helpers, field])

  return (
    <div className={cn(styles['select'], className)}>
      <label className={styles['select-label']} htmlFor={name}>
        {label}
      </label>
      <select
        className={cn(styles['select-input'], {
          error: meta.touched && !!meta.error,
        })}
        disabled={disabled}
        id={name}
        {...field}
      >
        {options.map(option => (
          <option key={option.value} value={option.value}>
            {option.label}
          </option>
        ))}
      </select>
      {meta.touched && meta.error && <FieldError>{meta.error}</FieldError>}
    </div>
  )
}

export default Select
