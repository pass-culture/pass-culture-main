import classNames from 'classnames'
import { type ForwardedRef, forwardRef, useId } from 'react'

import { Tooltip, type TooltipProps } from '@/ui-kit/Tooltip/Tooltip'

import styles from './DayCheckbox.module.scss'

type DayCheckboxProps = {
  /** Name of the input. Used for identifying it in an uncontrolled form, and for referencing the error */
  name: string
  className?: string
  /** Error text for the checkbox */
  hasError?: boolean
  /** Whether or not to display the error message. If false, the field has the error styles but no message */
  displayErrorMessage?: boolean
  onChange?: React.InputHTMLAttributes<HTMLInputElement>['onChange']
  onBlur?: React.InputHTMLAttributes<HTMLInputElement>['onBlur']
  label: string | React.ReactNode
  checked?: boolean
  disabled?: boolean
  tooltipContent: TooltipProps['content']
}

export const DayCheckbox = forwardRef(
  (
    {
      name,
      className,
      label,
      hasError,
      onChange,
      onBlur,
      checked,
      disabled,
      tooltipContent,
    }: DayCheckboxProps,
    ref: ForwardedRef<HTMLInputElement>
  ) => {
    const inputId = useId()

    return (
      <div
        className={classNames(
          styles['checkbox'],
          {
            [styles['disabled']]: disabled,
            [styles['error']]: Boolean(hasError),
          },
          className
        )}
      >
        {/* The tooltip already adds a aria-labelledby atribute to the input tag */}
        <label className={styles['checkbox-label']} htmlFor={inputId}>
          <span aria-hidden="true">{label}</span>
          <span className={styles['visually-hidden']}>{tooltipContent}</span>
        </label>
        <Tooltip content={tooltipContent}>
          <input
            type="checkbox"
            className={styles['checkbox-input']}
            aria-labelledby={`${name}-label`}
            aria-invalid={hasError}
            name={name}
            ref={ref}
            onChange={onChange}
            onBlur={onBlur}
            checked={checked}
            disabled={disabled}
            id={inputId}
          />
        </Tooltip>
      </div>
    )
  }
)

DayCheckbox.displayName = 'DayCheckbox'
