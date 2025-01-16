import cn from 'classnames'

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
  ariaDescribedBy?: string
  /**
   * Can be false only when it's the only field in a form and it's mandatory,
   * or when all fields are mandatory and the form indicates that all fields are mandatory
   */
  showMandatoryAsterisk?: boolean
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
  showMandatoryAsterisk = true,
}: FieldSetLayoutProps): JSX.Element => {
  const showError = Boolean(error) || !hideFooter
  return (
    <fieldset
      className={cn(styles['fieldset-layout'], className)}
      data-testid={dataTestId}
      aria-required={!isOptional}
      aria-describedby={ariaDescribedBy}
    >
      {legend && (
        <legend className={styles['fieldset-layout-legend']}>
          {legend}
          {!isOptional && showMandatoryAsterisk && ' *'}
        </legend>
      )}
      <div>{children}</div>
      {showError && (
        <div className={styles['fieldset-layout-error']}>
          {!!error && <FieldError name={name}>{error}</FieldError>}
        </div>
      )}
    </fieldset>
  )
}
