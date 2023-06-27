import cn from 'classnames'
import React from 'react'

import SuccessIcon from 'icons/ico-valid.svg'

import styles from './FieldSuccess.module.scss'

interface IFieldSuccessProps {
  children: React.ReactNode | React.ReactNode[]
  className?: string
  name: string
}

const FieldSuccess = ({
  children,
  className,
  name,
}: IFieldSuccessProps): JSX.Element => (
  <div className={cn(styles['field-success'], className)} id={name}>
    <SuccessIcon />
    <span
      className={styles['field-success-text']}
      data-testid={`success-${name}`}
      role="alert"
    >
      {children}
    </span>
  </div>
)

export default FieldSuccess
