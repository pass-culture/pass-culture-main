import { useField } from 'formik'
import React from 'react'

import { FieldLayout } from '../shared'
import { FieldLayoutBaseProps } from '../shared/FieldLayout/FieldLayout'

import { BaseTimePicker } from './BaseTimePicker'

export type TimePickerProps = FieldLayoutBaseProps & {
  disabled?: boolean
  dateTime?: Date
  value?: Date | null | ''
}

const isDateValid = (date: Date | null): boolean => {
  return date instanceof Date && !isNaN(date.getTime())
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
  const { value, ...otherFieldProps } = field

  // react-datepicker crashes if the value is not a Date or an InvalidDate
  // (InvalidDate is the result of new Date('stringthebrowsercantparse'))
  const selected = isDateValid(value) ? value : new Date()

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
        {...otherFieldProps}
        hasError={meta.touched && !!meta.error}
        filterVariant={filterVariant}
        selected={selected}
        disabled={disabled}
        onChange={(time: Date | null) => {
          if (isDateValid(time)) {
            helpers.setTouched(true)
            helpers.setValue(time)
          }
        }}
        value={isDateValid(value) ? value : ''}
      />
    </FieldLayout>
  )
}

export default TimePicker
