import cn from 'classnames'
import React from 'react'

import { FieldError } from '../FieldError/FieldError'

import styles from './FieldSetLayout.module.scss'

interface FieldSetLayoutProps {
  children: React.ReactNode
  legend?: string
  className?: string
  error?: string
  name: string
  hideFooter?: boolean
  dataTestId?: string
  isOptional?: boolean
}

export const FieldSetLayout = ({
  children,
  legend,
  className,
  error,
  name,
  hideFooter = false,
  dataTestId,
  isOptional = false,
}: FieldSetLayoutProps): JSX.Element => {
  return (
    <fieldset
      className={cn(styles['fieldset-layout'], className)}
      data-testid={dataTestId}
      aria-required={!isOptional}
      role="group"
      aria-labelledby="checkboxes-error-legend"
    >
      {legend && (
        <legend
          className={styles['fieldset-layout-legend']}
          id="checkboxes-error-legend"
        >
          {legend}
          {!isOptional && ' *'}
        </legend>
      )}

      <div> {children} </div>

      {!hideFooter && (
        <div className={styles['fieldset-layout-error']}>
          {!!error && <FieldError name={name}>{error}</FieldError>}
        </div>
      )}
    </fieldset>
  )
}
