import { ReactComponent as ErrorIcon } from './assets/error-icon.svg'
import React from 'react'
import cn from 'classnames'
import styles from './FieldError.module.scss'

interface IFieldErrorProps {
  children: React.ReactNode | React.ReactNode[]
  className?: string
  name: string
}

const FieldError = ({
  children,
  className,
  name,
}: IFieldErrorProps): JSX.Element => (
  <div className={cn(styles['field-error'], className)}>
    <ErrorIcon />
    <span
      className={styles['field-error-text']}
      data-testid={`error-${name}`}
      role="alert"
    >
      {children}
    </span>
  </div>
)

export default FieldError
