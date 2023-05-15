import { useField } from 'formik'
import React from 'react'

import { FieldLayout } from '../shared'
import { FieldLayoutBaseProps } from '../shared/FieldLayout/FieldLayout'

import { BaseTimePicker } from './BaseTimePicker'

export type TimePickerProps = FieldLayoutBaseProps & {
  disabled?: boolean
  dateTime?: Date
}

const isDateValid = (date: Date | null): boolean => {
  return date === null || (date instanceof Date && !isNaN(date.getTime()))
}

const TimePicker = ({
  name,
  className,
  classNameLabel,
  classNameFooter,
  disabled,
  label,
  isLabelHidden = false,
  smallLabel,
  hideFooter = false,
  clearButtonProps,
  filterVariant,
  isOptional = false,
}: TimePickerProps): JSX.Element => {
  const [field, meta, helpers] = useField({ name, type: 'text' })
  const showError = meta.touched && !!meta.error

  return (
    <FieldLayout
      className={className}
      error={meta.error}
      label={label}
      isLabelHidden={isLabelHidden}
      name={name}
      showError={showError}
      smallLabel={smallLabel}
      classNameLabel={classNameLabel}
      classNameFooter={classNameFooter}
      hideFooter={hideFooter}
      clearButtonProps={clearButtonProps}
      isOptional={isOptional}
    >
      <BaseTimePicker
        {...field}
        hasError={meta.touched && !!meta.error}
        filterVariant={filterVariant}
        // react-datepicker crashes if the value is not a Date or an InvalidDate
        // (InvalidDate is the result of new Date('stringthebrowsercantparse'))
        selected={isDateValid(field.value) ? field.value : new Date()}
        disabled={disabled}
        onChange={(time: Date | null) => {
          helpers.setTouched(true)
          helpers.setValue(time)
        }}
      />
    </FieldLayout>
  )
}

export default TimePicker
