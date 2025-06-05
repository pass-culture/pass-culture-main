import { useField } from 'formik'
import React, { useCallback } from 'react'

import {
  FieldLayout,
  FieldLayoutBaseProps,
} from '../shared/FieldLayout/FieldLayout'

import { BaseDatePicker } from './BaseDatePicker'

interface DatePickerProps extends FieldLayoutBaseProps {
  disabled?: boolean
  maxDate?: Date
  minDate?: Date
  onChange?: React.InputHTMLAttributes<HTMLInputElement>['onChange']
  help?: string
  onBlur?: React.FocusEventHandler<HTMLInputElement>
  hideAsterisk?: boolean
}

export const DatePicker = ({
  name,
  maxDate,
  minDate,
  className,
  classNameLabel,
  classNameFooter,
  disabled,
  label,
  isLabelHidden = false,
  hasLabelLineBreak = true,
  isOptional = false,
  filterVariant,
  onChange,
  help,
  onBlur,
  hideAsterisk = false,
}: DatePickerProps): JSX.Element => {
  const [field, meta] = useField({ name, type: 'date' })
  const showError = meta.touched && !!meta.error

  const onCustomChange = useCallback(
    (e: React.ChangeEvent<HTMLInputElement>) => {
      field.onChange(e)
      if (onChange) {
        onChange(e)
      }
    },
    [field, onChange]
  )

  return (
    <FieldLayout
      className={className}
      classNameLabel={classNameLabel}
      classNameFooter={classNameFooter}
      error={meta.error}
      label={label}
      isLabelHidden={isLabelHidden}
      hasLabelLineBreak={hasLabelLineBreak}
      name={name}
      showError={showError}
      isOptional={isOptional}
      help={help}
      hideAsterisk={hideAsterisk}
    >
      <BaseDatePicker
        {...field}
        id={name}
        hasError={meta.touched && !!meta.error}
        filterVariant={filterVariant}
        disabled={disabled}
        maxDate={maxDate}
        minDate={minDate}
        onChange={onCustomChange}
        aria-required={!isOptional}
        onBlur={onBlur}
      />
    </FieldLayout>
  )
}
