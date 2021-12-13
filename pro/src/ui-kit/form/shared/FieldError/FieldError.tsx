import cn from 'classnames'
import React from 'react'

import { ReactComponent as ErrorIcon } from './assets/error-icon.svg'
import styles from './FieldError.module.scss'

interface IFieldErrorProps {
  children: React.ReactNode | React.ReactNode[]
  className?: string
}

const FieldError = ({ children, className }: IFieldErrorProps): JSX.Element => (
  <div className={cn(styles['field-error'], className)}>
    <ErrorIcon />
    <span className={styles['field-error-text']}>{children}</span>
  </div>
)

export default FieldError
