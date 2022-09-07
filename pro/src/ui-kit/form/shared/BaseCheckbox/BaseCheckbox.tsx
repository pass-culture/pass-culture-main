import cn from 'classnames'
import React from 'react'

import styles from './BaseCheckbox.module.scss'

export interface IBaseCheckboxProps
  extends Partial<React.InputHTMLAttributes<HTMLInputElement>> {
  label: string
  description?: string
  hasError?: boolean
  className?: string
  Icon?: React.FunctionComponent<
    React.SVGProps<SVGSVGElement> & {
      title?: string | undefined
    }
  >
}

const BaseCheckbox = ({
  label,
  description,
  hasError,
  className,
  Icon,
  ...props
}: IBaseCheckboxProps): JSX.Element => (
  <label className={cn(styles['base-checkbox'], className)}>
    <div className={styles['base-checkbox-label-row']}>
      <input
        aria-invalid={hasError}
        type="checkbox"
        {...props}
        className={cn(styles['base-checkbox-input'], {
          [styles['has-error']]: hasError,
        })}
      />
      {!!Icon && (
        <span className={styles['base-checkbox-icon']}>
          <Icon />
        </span>
      )}
      <span className={styles['base-checkbox-label']}>{label}</span>
    </div>
    {description && (
      <p className={styles['base-checkbox-description']}>{description}</p>
    )}
  </label>
)

export default BaseCheckbox
