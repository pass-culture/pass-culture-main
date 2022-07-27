import cn from 'classnames'
import React from 'react'

import styles from './BaseCheckbox.module.scss'

interface IBaseCheckboxProps
  extends Partial<React.InputHTMLAttributes<HTMLInputElement>> {
  label: string
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
  hasError,
  className,
  Icon,
  ...props
}: IBaseCheckboxProps): JSX.Element => (
  <label className={cn(styles['base-checkbox'], className)}>
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
  </label>
)

export default BaseCheckbox
