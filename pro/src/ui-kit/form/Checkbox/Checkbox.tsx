import cn from 'classnames'
import { useField } from 'formik'
import React from 'react'

import { BaseCheckbox } from 'ui-kit/form/shared/BaseCheckbox/BaseCheckbox'

import { FieldError } from '../shared/FieldError/FieldError'

import styles from './Checkbox.module.scss'

interface CheckboxProps {
  name: string
  value?: string
  label: string | React.ReactNode
  description?: string
  className?: string
  hideFooter?: boolean
  icon?: string
  disabled?: boolean
  withBorder?: boolean
  onChange?: (e: React.ChangeEvent<HTMLInputElement>) => void
}

export const Checkbox = ({
  name,
  value,
  label,
  className,
  icon,
  hideFooter,
  disabled,
  withBorder,
  ...props
}: CheckboxProps): JSX.Element => {
  const [field, meta] = useField({ name, type: 'checkbox' })
  return (
    <div className={cn(styles['checkbox'], className)}>
      <BaseCheckbox
        {...field}
        icon={icon}
        hasError={meta.touched && !!meta.error}
        label={label}
        value={value}
        disabled={disabled}
        withBorder={withBorder}
        {...props}
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
