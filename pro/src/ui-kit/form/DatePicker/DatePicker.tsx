import { useField } from 'formik'
import React, { useCallback } from 'react'

import { FieldLayout } from '../shared'
import { FieldLayoutBaseProps } from '../shared/FieldLayout/FieldLayout'

import { BaseDatePicker } from './BaseDatePicker'

export interface DatePickerProps extends FieldLayoutBaseProps {
  disabled?: boolean
  maxDate?: Date
  minDate?: Date
  onChange?: React.InputHTMLAttributes<HTMLInputElement>['onChange']
}

const DatePicker = ({
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
  smallLabel,
  isOptional = false,
  hideFooter = false,
  filterVariant,
  onChange,
}: DatePickerProps): JSX.Element => {
  const [field, meta] = useField({ name, type: 'date' })
  const showError = meta.touched && !!meta.error

  const onCustomChange = useCallback(
    async (e: React.ChangeEvent<HTMLInputElement>) => {
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
      smallLabel={smallLabel}
      isOptional={isOptional}
      hideFooter={hideFooter}
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
      />
    </FieldLayout>
  )
}

export default DatePicker
