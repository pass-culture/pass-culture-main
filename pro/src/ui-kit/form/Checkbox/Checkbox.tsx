import cn from 'classnames'
import { useField } from 'formik'
import React from 'react'

import { BaseCheckbox, FieldError } from '../shared'

import styles from './Checkbox.module.scss'

export interface CheckboxProps {
  name: string
  value?: string
  label: string
  description?: string
  className?: string
  hideFooter?: boolean
  icon?: string
  disabled?: boolean
  withBorder?: boolean
}

const Checkbox = ({
  name,
  value,
  label,
  description,
  className,
  icon,
  hideFooter,
  disabled,
  withBorder,
}: CheckboxProps): JSX.Element => {
  const [field, meta] = useField({ name, type: 'checkbox' })
  return (
    <div className={cn(styles['checkbox'], className)}>
      <BaseCheckbox
        {...field}
        icon={icon}
        hasError={meta.touched && !!meta.error}
        label={label}
        description={description}
        value={value}
        disabled={disabled}
        withBorder={withBorder}
      />
      {!hideFooter && (
        <div className={styles['checkbox-error']}>
          {meta.touched && !!meta.error && (
            <FieldError name={name}>{meta.error}</FieldError>
          )}
        </div>
      )}
    </div>
  )
}

export default Checkbox
