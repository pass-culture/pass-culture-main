import { useField } from 'formik'
import React from 'react'

import { FieldLayout } from '../shared'
import { FieldLayoutBaseProps } from '../shared/FieldLayout/FieldLayout'

import { BaseTimePicker } from './BaseTimePicker'

export type TimePickerProps = FieldLayoutBaseProps & {
  disabled?: boolean
  dateTime?: Date
  hideHiddenFooter?: boolean
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
  hideHiddenFooter = false,
  clearButtonProps,
  filterVariant,
}: TimePickerProps): JSX.Element => {
  const [field, meta, helpers] = useField({ name, type: 'text' })
  const showError = meta.touched && !!meta.error

  /* istanbul ignore next: DEBT, TO FIX */
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
      hideFooter={hideFooter || (hideHiddenFooter && !showError)}
      clearButtonProps={clearButtonProps}
    >
      <BaseTimePicker
        {...field}
        hasError={meta.touched && !!meta.error}
        filterVariant={filterVariant}
        selected={field.value}
        disabled={disabled}
        onChange={(time: Date | null) => {
          /* istanbul ignore next: DEBT, TO FIX */
          helpers.setTouched(true)
          /* istanbul ignore next: DEBT, TO FIX */
          helpers.setValue(time)
        }}
      />
    </FieldLayout>
  )
}

export default TimePicker
