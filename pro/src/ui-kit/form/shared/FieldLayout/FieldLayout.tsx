import cn from 'classnames'
import React from 'react'

import FieldError from '../FieldError'

import styles from './FieldLayout.module.scss'

interface IFieldLayoutProps {
  children: React.ReactNode
  label: string
  name: string
  showError: boolean
  className?: string
  error?: string
  count?: number
  maxLength?: number
  isOptional?: boolean
  smallLabel?: boolean
}

const FieldLayout = ({
  children,
  label,
  className,
  name,
  showError = false,
  error,
  count = undefined,
  maxLength = undefined,
  isOptional = false,
  smallLabel,
}: IFieldLayoutProps): JSX.Element => (
  <div
    className={cn(styles['field-layout'], className, {
      [styles['field-layout-small-label']]: smallLabel,
    })}
  >
    <label className={styles['field-layout-label']} htmlFor={name}>
      {label}
      {isOptional && (
        <span className={styles['field-layout-optional']}>Optionnel</span>
      )}
    </label>

    <div
      aria-invalid={showError && !!error ? 'true' : 'false'}
      className={styles['field-layout-input']}
    >
      {children}
    </div>

    <div className={styles['field-layout-footer']}>
      {showError && !!error && (
        <div className={styles['field-layout-error']}>
          <FieldError>{error}</FieldError>
        </div>
      )}
      {count !== undefined && maxLength !== undefined && (
        <span className={styles['field-layout-counter']}>
          {count}/{maxLength}
        </span>
      )}
    </div>
  </div>
)

export default FieldLayout
