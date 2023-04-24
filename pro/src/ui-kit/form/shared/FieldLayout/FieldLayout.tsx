import cn from 'classnames'
import React, { useId } from 'react'

import { ClearIcon } from 'icons'
import Tooltip from 'ui-kit/Tooltip'

import FieldError from '../FieldError'

import styles from './FieldLayout.module.scss'

export type FieldLayoutBaseProps = {
  // These props are display options that are applicable to all fields using FieldLayout
  label: string
  name: string
  description?: string
  maxLength?: number
  isLabelHidden?: boolean
  hasLabelLineBreak?: boolean
  isOptional?: boolean
  className?: string
  classNameLabel?: string
  classNameFooter?: string
  filterVariant?: boolean
  smallLabel?: boolean
  hideFooter?: boolean
  inline?: boolean
  clearButtonProps?: React.ButtonHTMLAttributes<HTMLButtonElement> & {
    tooltip: string
  }
}

type FieldLayoutProps = FieldLayoutBaseProps & {
  // These props are derived from the formik state and passed by the parent component
  children: React.ReactNode
  showError: boolean
  error?: string
  count?: number
}

/* istanbul ignore next: DEBT, TO FIX */
const FieldLayout = ({
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
  description,
  clearButtonProps,
}: FieldLayoutProps): JSX.Element => {
  const hasError = showError && !!error
  const hasCounter = count !== undefined && maxLength !== undefined
  const tooltipId = useId()

  const clearButton = (
    <button
      type="button"
      {...clearButtonProps}
      aria-describedby={tooltipId}
      className={styles['clear-button']}
    >
      <ClearIcon className={styles['clear-button-icon']} />
    </button>
  )
  const showFooter = !hideFooter || hasError || hasCounter

  return (
    <div
      className={cn(styles['field-layout'], className, {
        [styles['field-layout-small-label']]: smallLabel,
        [styles['field-layout-inline']]: inline,
      })}
      data-testid={`wrapper-${name}`}
    >
      <div
        className={cn(styles['field-layout-label-container'], {
          [styles['label-hidden']]: isLabelHidden,
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
          {label}
          {isOptional && (
            <span className={styles['field-layout-optional']}>Optionnel</span>
          )}
        </label>
        {description && (
          <span className={styles['field-layout-input-description']}>
            {description}
          </span>
        )}
      </div>

      <div className={styles['field-layout-content']}>
        <div className={styles['input-wrapper']}>
          {children}
          {clearButtonProps && (
            <div className={styles['clear-button-container']}>
              {clearButtonProps.disabled ? (
                clearButton
              ) : (
                <Tooltip content={clearButtonProps.tooltip} id={tooltipId}>
                  {clearButton}
                </Tooltip>
              )}
            </div>
          )}
        </div>

        {showFooter && (
          <div className={cn(classNameFooter, styles['field-layout-footer'])}>
            {hasError && (
              <div className={styles['field-layout-error']}>
                <FieldError name={name}>{error}</FieldError>
              </div>
            )}
            {hasCounter && (
              <span
                className={styles['field-layout-counter']}
                data-testid={`counter-${name}`}
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

export default FieldLayout
