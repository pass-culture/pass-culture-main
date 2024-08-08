import cn from 'classnames'
import React, { useId } from 'react'

import fullClearIcon from 'icons/full-clear.svg'
import { Button } from 'ui-kit/Button/Button'
import { ButtonVariant } from 'ui-kit/Button/types'

import { FieldError } from '../FieldError/FieldError'

import styles from './FieldLayout.module.scss'

export type FieldLayoutBaseProps = {
  // These props are display options that are applicable to all fields using FieldLayout
  label: string | JSX.Element
  name: string
  description?: string
  maxLength?: number
  isLabelHidden?: boolean
  hasLabelLineBreak?: boolean
  isOptional?: boolean
  className?: string
  classNameLabel?: string
  classNameFooter?: string
  classNameInput?: string
  filterVariant?: boolean
  smallLabel?: boolean
  hideFooter?: boolean
  inline?: boolean
  clearButtonProps?: React.ButtonHTMLAttributes<HTMLButtonElement> & {
    tooltip: string
  }
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
  isOptional = false,
  smallLabel,
  hideFooter = false,
  inline = false,
  classNameLabel,
  classNameFooter,
  classNameInput,
  description,
  clearButtonProps,
  ErrorDetails,
}: FieldLayoutProps): JSX.Element => {
  const hasError = showError && !!error
  const hasCounter = count !== undefined && maxLength !== undefined
  const tooltipId = useId()

  const showFooter =
    !hideFooter || hasError || hasCounter || Boolean(ErrorDetails)

  return (
    <div
      className={cn(
        styles['field-layout'],
        {
          [styles['field-layout-small-label']]: smallLabel,
          [styles['field-layout-inline']]: inline,
        },
        className
      )}
      data-testid={`wrapper-${name}`}
    >
      <div
        className={cn(styles['field-layout-label-container'], {
          ['visually-hidden']: isLabelHidden,
          classNameLabel,
        })}
      >
        <label
          className={cn(
            styles['field-layout-label'],
            hasLabelLineBreak && styles['field-layout-label-break']
          )}
          htmlFor={name}
        >
          {label} {!isOptional && '*'}
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
          {clearButtonProps && (
            <div className={styles['clear-button-container']}>
              <Button
                {...clearButtonProps}
                aria-describedby={tooltipId}
                className={styles['clear-button']}
                hasTooltip={true}
                type="button"
                icon={fullClearIcon}
                variant={ButtonVariant.TERNARY}
              >
                Supprimer
              </Button>
            </div>
          )}
        </div>

        {showFooter && (
          <div className={cn(classNameFooter, styles['field-layout-footer'])}>
            <div
              role="alert"
              className={styles['field-layout-error']}
              id={`error-details-${name}`}
            >
              {(hasError || Boolean(ErrorDetails)) && (
                <>
                  {hasError && <FieldError name={name}>{error}</FieldError>}
                  {ErrorDetails}
                </>
              )}
            </div>
            {hasCounter && (
              <span
                className={styles['field-layout-counter']}
                data-testid={`counter-${name}`}
                role="status"
              >
                {count}/{maxLength}
              </span>
            )}
          </div>
        )}
      </div>
    </div>
  )
}
