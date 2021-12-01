import cn from 'classnames'
import React from 'react'

import Icon from 'components/layout/Icon'

import styles from './FieldError.module.scss'

interface IFieldErrorProps {
  children: React.ReactNode | React.ReactNode[]
  className?: string
}

const FieldError = ({ children, className }: IFieldErrorProps): JSX.Element => (
  <div className={cn(styles['field-error'], className)}>
    <Icon alt={null} png={null} svg="ico-notification-error-red" />
    <span>{children}</span>
  </div>
)

export default FieldError
