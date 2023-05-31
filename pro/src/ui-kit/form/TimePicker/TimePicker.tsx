import { useField } from 'formik'
import React from 'react'

import { FieldLayout } from '../shared'
import { FieldLayoutBaseProps } from '../shared/FieldLayout/FieldLayout'

import { BaseTimePicker, isDateValid } from './BaseTimePicker'

export type TimePickerProps = FieldLayoutBaseProps & {
  disabled?: boolean
  dateTime?: Date
  value?: Date | null | ''
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
        disabled={disabled}
        onChange={(time: Date | null) => {
          if (isDateValid(time)) {
            helpers.setTouched(true)
            helpers.setValue(time)
          }
        }}
      />
    </FieldLayout>
  )
}

export default TimePicker
