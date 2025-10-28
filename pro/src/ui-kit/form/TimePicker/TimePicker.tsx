import classNames from 'classnames'
import { type ForwardedRef, forwardRef, useId } from 'react'

import { FieldFooter } from '@/design-system/common/FieldFooter/FieldFooter'
import { FieldHeader } from '@/design-system/common/FieldHeader/FieldHeader'
import type { RequiredIndicator } from '@/design-system/common/types'
import {
  BaseTimePicker,
  type SuggestedTimeList,
} from '@/ui-kit/form/shared/BaseTimePicker/BaseTimePicker'

import styles from './TimePicker.module.scss'

type TimePickerProps = {
  disabled?: boolean
  value?: string
  onChange?: React.InputHTMLAttributes<HTMLInputElement>['onChange']
  onBlur?: React.FocusEventHandler<HTMLInputElement>
  /** What type of required indicator is displayed */
  requiredIndicator?: RequiredIndicator
  /** Name of the input. Used for identifying it in an uncontrolled form, and for referencing the error */
  name: string
  className?: string
  label: string
  required?: boolean
  error?: string
  suggestedTimeList?: SuggestedTimeList
  isLabelHidden?: boolean
}

export const TimePicker = forwardRef(
  (
    {
      name,
      className,
      disabled,
      label,
      required = false,
      requiredIndicator,
      error,
      value,
      onChange,
      onBlur,
      suggestedTimeList,
      isLabelHidden,
    }: TimePickerProps,
    ref: ForwardedRef<HTMLInputElement>
  ): JSX.Element => {
    const inputId = useId()
    const errorId = useId()

    return (
      <div className={className}>
        <div
          className={classNames({
            [styles['visually-hidden']]: isLabelHidden,
          })}
        >
          <FieldHeader
            fieldId={inputId}
            label={label}
            required={required}
            requiredIndicator={requiredIndicator}
          />
        </div>
        <BaseTimePicker
          hasError={Boolean(error)}
          disabled={disabled}
          aria-required={required}
          value={value}
          ref={ref}
          onChange={onChange}
          onBlur={onBlur}
          name={name}
          id={inputId}
          aria-describedby={errorId}
          suggestedTimeList={suggestedTimeList}
        />
        <FieldFooter error={error} errorId={errorId} />
      </div>
    )
  }
)

TimePicker.displayName = 'TimePicker'
