import classNames from 'classnames'
import { ForwardedRef, forwardRef, useId } from 'react'

import { FieldError } from '@/ui-kit/form/shared/FieldError/FieldError'
import { Tooltip, TooltipProps } from '@/ui-kit/Tooltip/Tooltip'

import styles from './DayCheckbox.module.scss'

type DayCheckboxProps = {
  /** Name of the input. Used for identifying it in an uncontrolled form, and for referencing the error */
  name: string
  className?: string
  /** Error text for the checkbox */
  error?: string
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
      error,
      label,
      displayErrorMessage = true,
      onChange,
      onBlur,
      checked,
      disabled,
      tooltipContent,
    }: DayCheckboxProps,
    ref: ForwardedRef<HTMLInputElement>
  ) => {
    const errorId = useId()

    return (
      <div
        className={classNames(
          styles['checkbox'],
          { [styles['disabled']]: disabled, [styles['error']]: Boolean(error) },
          className
        )}
      >
        {/* The tooltip already adds a aria-labelledby atribute to the input tag */}
        <label className={styles['checkbox-label']} aria-hidden={true}>
          {label}
        </label>
        <Tooltip content={tooltipContent}>
          <input
            type="checkbox"
            className={styles['checkbox-input']}
            name={name}
            ref={ref}
            aria-describedby={errorId}
            onChange={onChange}
            onBlur={onBlur}
            checked={checked}
            disabled={disabled}
          />
        </Tooltip>

        <div role="alert" id={errorId}>
          {error && displayErrorMessage && (
            <FieldError name={name} className={styles['error']}>
              {error}
            </FieldError>
          )}
        </div>
      </div>
    )
  }
)

DayCheckbox.displayName = 'DayCheckbox'
