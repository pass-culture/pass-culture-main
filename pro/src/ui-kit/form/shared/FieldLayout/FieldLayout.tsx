import FieldError from '../FieldError'
import React from 'react'
import cn from 'classnames'
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
  hideFooter?: boolean
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
  hideFooter = false,
}: IFieldLayoutProps): JSX.Element => (
  <div
    className={cn(styles['field-layout'], className, {
      [styles['field-layout-small-label']]: smallLabel,
    })}
    data-testid={`wrapper-${name}`}
  >
    <label className={styles['field-layout-label']} htmlFor={name}>
      {label}
      {isOptional && (
        <span className={styles['field-layout-optional']}>Optionnel</span>
      )}
    </label>

    <div>{children}</div>

    {!hideFooter && (
      <div className={styles['field-layout-footer']}>
        {showError && !!error && (
          <div className={styles['field-layout-error']}>
            <FieldError name={name}>{error}</FieldError>
          </div>
        )}
        {count !== undefined && maxLength !== undefined && (
          <span
            className={styles['field-layout-counter']}
            data-testid={`counter-${name}`}
          >
            {count}/{maxLength}
          </span>
        )}
      </div>
    )}
  </div>
)

export default FieldLayout
