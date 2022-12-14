import fr from 'date-fns/locale/fr'
import { useField } from 'formik'
import React, { createRef } from 'react'
import ReactDatePicker, { registerLocale } from 'react-datepicker'

import { FORMAT_HH_mm } from 'utils/date'

import { BaseInput, FieldLayout } from '../shared'

registerLocale('fr', fr)

export interface ITimePickerProps {
  name: string
  className?: string
  disabled?: boolean
  label: string
  isLabelHidden?: boolean
  dateTime?: Date
  smallLabel?: boolean
  classNameFooter?: string
  classNameLabel?: string
  hideFooter?: boolean
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
}: ITimePickerProps): JSX.Element => {
  const [field, meta, helpers] = useField({ name, type: 'text' })
  const ref = createRef<HTMLInputElement>()
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
    >
      <ReactDatePicker
        {...field}
        customInput={
          <BaseInput hasError={meta.touched && !!meta.error} ref={ref} />
        }
        dateFormat={FORMAT_HH_mm}
        disabled={disabled}
        dropdownMode="scroll"
        locale="fr"
        onChange={time => {
          /* istanbul ignore next: DEBT, TO FIX */
          helpers.setTouched(true)
          /* istanbul ignore next: DEBT, TO FIX */
          helpers.setValue(time)
        }}
        placeholderText="HH:MM"
        selected={field.value}
        showTimeSelect
        showTimeSelectOnly
        timeCaption="Horaire"
        timeFormat={FORMAT_HH_mm}
        timeIntervals={15}
        onKeyDown={event => {
          !/[0-9:]|Backspace|Tab/.test(event.key) && event.preventDefault()
        }}
      />
    </FieldLayout>
  )
}

export default TimePicker
