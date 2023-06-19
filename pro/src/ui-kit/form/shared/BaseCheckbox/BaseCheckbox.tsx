import cn from 'classnames'
import React from 'react'

import styles from './BaseCheckbox.module.scss'

export interface BaseCheckboxProps
  extends Partial<React.InputHTMLAttributes<HTMLInputElement>> {
  label: string | React.ReactNode
  description?: string
  hasError?: boolean
  className?: string
  icon?: string
  withBorder?: boolean
}

const BaseCheckbox = ({
  label,
  description,
  hasError,
  className,
  icon,
  withBorder,
  ...props
}: BaseCheckboxProps): JSX.Element => (
  <label
    className={cn(
      styles['base-checkbox'],
      {
        [styles['with-border']]: withBorder,
      },
      className
    )}
  >
    <span className={styles['base-checkbox-label-row']}>
      <input
        aria-invalid={hasError}
        type="checkbox"
        {...props}
        className={cn(styles['base-checkbox-input'], {
          [styles['has-error']]: hasError,
        })}
        data-testid={'checkbox'}
      />
      {!!icon && (
        <span className={styles['base-checkbox-icon']}>
          <img src={icon} className={styles['base-checkbox-icon-svg']} />
        </span>
      )}
      <span className={styles['base-checkbox-label']}>{label}</span>
    </span>
    {description && (
      <p className={styles['base-checkbox-description']}>{description}</p>
    )}
  </label>
)

export default BaseCheckbox
