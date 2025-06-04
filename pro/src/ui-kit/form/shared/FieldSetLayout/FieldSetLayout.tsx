import cn from 'classnames'
import { isValidElement } from 'react'

import { FieldError } from '../FieldError/FieldError'

import styles from './FieldSetLayout.module.scss'

interface FieldSetLayoutProps {
  children: React.ReactNode
  legend?: string | React.ReactNode
  className?: string
  error?: string
  name: string
  hideFooter?: boolean
  dataTestId?: string
  isOptional?: boolean
  ariaDescribedBy?: string
  /**
   * Can be false only when it's the only field in a form and it's mandatory,
   * or when all fields are mandatory and the form indicates that all fields are mandatory
   * or when the legend itself handles the asterisk
   */
  hideAsterisk?: boolean
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
  ariaDescribedBy,
  hideAsterisk = false,
}: FieldSetLayoutProps): JSX.Element => {
  const showError = Boolean(error) || !hideFooter

  return (
    <fieldset
      className={cn(styles['fieldset-layout'], className)}
      data-testid={dataTestId}
      aria-labelledby="fieldsetlayout-legend"
      aria-describedby={`fieldsetlayout-error ${ariaDescribedBy ?? ''}`.trim()}
    >
      {legend && (
        <legend
          id="fieldsetlayout-legend"
          className={
            isValidElement(legend)
              ? undefined
              : styles['fieldset-layout-legend']
          }
        >
          {legend}
          {!isOptional && !hideAsterisk && ' *'}
        </legend>
      )}
      {children}
      {showError && (
        <div
          id="fieldsetlayout-error"
          className={styles['fieldset-layout-error']}
          aria-live="assertive"
        >
          {!!error && <FieldError name={name}>{error}</FieldError>}
        </div>
      )}
    </fieldset>
  )
}
