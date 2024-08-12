import { useField } from 'formik'
import React from 'react'

import {
  FieldLayout,
  FieldLayoutBaseProps,
} from '../shared/FieldLayout/FieldLayout'

import { BaseTimePicker } from './BaseTimePicker'
import { SuggestedTimeList } from './types'

type TimePickerProps = FieldLayoutBaseProps & {
  disabled?: boolean
  dateTime?: Date
  value?: Date | null | ''
  min?: string
  suggestedTimeList?: SuggestedTimeList
}

export const TimePicker = ({
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
  min,
  suggestedTimeList,
}: TimePickerProps): JSX.Element => {
  const [field, meta] = useField({ name, type: 'text' })
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
        aria-required={!isOptional}
        min={min}
        suggestedTimeList={suggestedTimeList}
      />
    </FieldLayout>
  )
}
