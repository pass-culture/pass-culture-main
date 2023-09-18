import cn from 'classnames'
import React from 'react'

import styles from './BaseCheckbox.module.scss'

export interface BaseCheckboxProps
  extends Partial<React.InputHTMLAttributes<HTMLInputElement>> {
  label: string | React.ReactNode
  hasError?: boolean
  className?: string
  icon?: string
  withBorder?: boolean
  ref?: React.Ref<HTMLInputElement>
  partialCheck?: boolean
}

const BaseCheckbox = ({
  label,
  hasError,
  className,
  icon,
  withBorder,
  partialCheck,
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
          [styles['partial-check']]: partialCheck,
        })}
      />
      {Boolean(icon) && (
        <span className={styles['base-checkbox-icon']}>
          <img src={icon} className={styles['base-checkbox-icon-svg']} />
        </span>
      )}
      <span className={styles['base-checkbox-label']}>{label}</span>
    </span>
  </label>
)

export default BaseCheckbox
