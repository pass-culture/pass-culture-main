import cn from 'classnames'
import type React from 'react'

import type { RequiredIndicator } from '@/design-system/common/types'

import { FieldError } from '../FieldError/FieldError'
import styles from './FieldLayout.module.scss'
import { FieldLayoutCharacterCount } from './FieldLayoutCharacterCount/FieldLayoutCharacterCount'

type FieldLayoutBaseProps = {
  // These props are display options that are applicable to all fields using FieldLayout
  label: string | JSX.Element
  name: string
  description?: string
  maxLength?: number
  /**
   * A flag to hide the label.
   * To be used with caution, as it can affect accessibility.
   * Do not use it if the label is mandatory, placeholder is not
   * a substitute for a label.
   */
  isLabelHidden?: boolean
  hasLabelLineBreak?: boolean
  /** A flag to indicate that the field is required. */
  required?: boolean
  /** What type of required indicator is displayed */
  requiredIndicator?: RequiredIndicator
  /**
   * A custom class for the field layout,
   * where label, description, input, and footer are displayed.
   */
  className?: string
  classNameLabel?: string
  /**
   * A custom class for the footer,
   * where errors and character count are displayed.
   */
  classNameFooter?: string
  classNameInput?: string

  inline?: boolean
  ErrorDetails?: React.ReactNode
}

type FieldLayoutProps = FieldLayoutBaseProps & {
  // These props are derived from the formik state and passed by the parent component
  children: React.ReactNode
  showError?: boolean
  error?: string
  count?: number
}

/* istanbul ignore next: DEBT, TO FIX */
export const FieldLayout = ({
  children,
  label,
  isLabelHidden = false,
  hasLabelLineBreak = true,
  className,
  name,
  showError = false,
  error,
  count = undefined,
  maxLength = undefined,
  required = true,
  requiredIndicator = 'symbol',
  inline = false,
  classNameLabel,
  classNameFooter,
  classNameInput,
  description,
  ErrorDetails,
}: FieldLayoutProps): JSX.Element => {
  const hasError = showError && !!error
  const hasCounter = count !== undefined && maxLength !== undefined

  const showFooter = hasError || hasCounter || Boolean(ErrorDetails)

  return (
    <div
      className={cn(
        styles['field-layout'],
        {
          [styles['field-layout-inline']]: inline,
        },
        className
      )}
      data-testid={`wrapper-${name}`}
    >
      <div
        className={cn(styles['field-layout-label-container'], classNameLabel, {
          [styles['visually-hidden']]: isLabelHidden,
        })}
      >
        <label
          className={cn(
            styles['field-layout-label'],
            hasLabelLineBreak && styles['field-layout-label-break']
          )}
          htmlFor={name}
        >
          {label}
          {required && requiredIndicator === 'symbol' && <>&nbsp;*</>}
          {required && requiredIndicator === 'explicit' && (
            <span className={styles['field-header-right']}>Obligatoire</span>
          )}
        </label>
        {description && (
          <span
            id={`description-${name}`}
            data-testid={`description-${name}`}
            className={styles['field-layout-input-description']}
          >
            {description}
          </span>
        )}
      </div>

      <div className={styles['field-layout-content']}>
        <div className={cn(styles['input-wrapper'], classNameInput)}>
          {children}
        </div>

        {showFooter && (
          <div className={cn(classNameFooter, styles['field-layout-footer'])}>
            <div role="alert" id={`error-details-${name}`}>
              {(hasError || Boolean(ErrorDetails)) && (
                <>
                  {hasError && (
                    <FieldError
                      className={styles['field-layout-error']}
                      name={name}
                    >
                      {error}
                    </FieldError>
                  )}
                  {ErrorDetails}
                </>
              )}
            </div>
            {hasCounter && (
              <FieldLayoutCharacterCount
                count={count}
                maxLength={maxLength}
                name={name}
              />
            )}
          </div>
        )}
      </div>
    </div>
  )
}
