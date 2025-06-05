import { useField } from 'formik'

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
  hideAsterisk?: boolean
}

export const TimePicker = ({
  name,
  className,
  classNameLabel,
  classNameFooter,
  classNameInput,
  disabled,
  label,
  isLabelHidden = false,
  clearButtonProps,
  filterVariant,
  isOptional = false,
  min,
  suggestedTimeList,
  hideAsterisk = false,
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
      classNameLabel={classNameLabel}
      classNameFooter={classNameFooter}
      classNameInput={classNameInput}
      clearButtonProps={clearButtonProps}
      isOptional={isOptional}
      hideAsterisk={hideAsterisk}
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
