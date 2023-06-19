import cn from 'classnames'
import React from 'react'

import strokeErrorIcon from 'icons/stroke-error.svg'
import { SvgIcon } from 'ui-kit/SvgIcon/SvgIcon'

import styles from './FieldError.module.scss'

interface IFieldErrorProps {
  children: React.ReactNode | React.ReactNode[]
  className?: string
  name: string
  iconAlt?: string
}

const FieldError = ({
  children,
  className,
  name,
  iconAlt = '',
}: IFieldErrorProps): JSX.Element => (
  <div
    className={cn(styles['field-error'], className)}
    id={`error-${name}`}
    role="alert"
  >
    <SvgIcon src={strokeErrorIcon} alt={iconAlt} />
    <span className={styles['field-error-text']} data-testid={`error-${name}`}>
      {children}
    </span>
  </div>
)

export default FieldError
