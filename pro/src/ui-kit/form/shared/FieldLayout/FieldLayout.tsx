import cn from 'classnames'
import React, { useId } from 'react'

import fullClearIcon from '@/icons/full-clear.svg'
import fullCloseIcon from '@/icons/full-close.svg'
import fullHelpIcon from '@/icons/full-help.svg'
import { Button } from '@/ui-kit/Button/Button'
import { ButtonVariant } from '@/ui-kit/Button/types'

import { FieldError } from '../FieldError/FieldError'
import styles from './FieldLayout.module.scss'
import { FieldLayoutCharacterCount } from './FieldLayoutCharacterCount/FieldLayoutCharacterCount'

export type FieldLayoutBaseProps = {
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
  /**
   * A flag to indicate that the field is optional.
   * It will display an asterisk next to the label.
   */
  isOptional?: boolean
  /**
   * Can be false only when it's the only field in a form and it's mandatory,
   * or when all fields are mandatory and the form indicates that all fields are mandatory
   */
  hideAsterisk?: boolean
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
  filterVariant?: boolean
  /**
   * A flag to display a smaller label.
   */
  smallLabel?: boolean

  inline?: boolean
  clearButtonProps?: React.ButtonHTMLAttributes<HTMLButtonElement> & {
    tooltip: string
    display?: 'clear' | 'close'
  }
  ErrorDetails?: React.ReactNode
}

type FieldLayoutProps = FieldLayoutBaseProps & {
  // These props are derived from the formik state and passed by the parent component
  children: React.ReactNode
  showError?: boolean
  error?: string
  count?: number
  help?: string
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
  hideAsterisk = false,
  smallLabel,
  inline = false,
  classNameLabel,
  classNameFooter,
  classNameInput,
  description,
  clearButtonProps,
  ErrorDetails,
  help,
}: FieldLayoutProps): JSX.Element => {
  const hasError = showError && !!error
  const hasCounter = count !== undefined && maxLength !== undefined
  const tooltipId = useId()

  const showFooter = hasError || hasCounter || Boolean(ErrorDetails)

  const clearButtonDisplay = clearButtonProps?.display || 'clear'

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
        className={cn(styles['field-layout-label-container'], classNameLabel, {
          [styles['visually-hidden']]: isLabelHidden,
        })}
      >
        <div
          className={cn({
            [styles['field-layout-label-with-help']]: !!help,
          })}
        >
          <label
            className={cn(
              styles['field-layout-label'],
              hasLabelLineBreak && styles['field-layout-label-break']
            )}
            htmlFor={name}
          >
            {label} {!isOptional && !hideAsterisk && '*'}
          </label>
          {help && (
            <Button
              className={styles['field-layout-button-tooltip-help']}
              icon={fullHelpIcon}
              iconAlt="À propos"
              variant={ButtonVariant.SECONDARY}
              tooltipContent={<>{help}</>}
            />
          )}
        </div>
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
            <div
              className={cn(
                styles['clear-button-container'],
                styles[`clear-button-${clearButtonDisplay}-container`]
              )}
            >
              <Button
                {...clearButtonProps}
                aria-describedby={tooltipId}
                className={styles['clear-button']}
                type="button"
                icon={
                  clearButtonDisplay === 'clear' ? fullClearIcon : fullCloseIcon
                }
                tooltipContent={<>{clearButtonProps.tooltip || 'Supprimer'}</>}
                variant={ButtonVariant.TERNARY}
              />
            </div>
          )}
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
