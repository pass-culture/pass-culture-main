import { useField } from 'formik'
import React from 'react'

import TextInput from '../TextInput'

import { parseMinutesToHours } from './utils/parseMinutesToHours'

export interface IDurationInputProps {
  label: string
  name: string
  isOptional?: boolean
  className?: string
}

const DurationInput = ({
  label,
  name,
  isOptional = false,
  className,
}: IDurationInputProps): JSX.Element => {
  const [field, meta, helpers] = useField({ name })

  const onDurationBlur = (event: React.FocusEvent<HTMLInputElement>) => {
    if (!meta.touched) {
      helpers.setTouched(true, false)
    }
    const [updatedHours, updatedMinutes] = event.target.value.split(':')
    const updatedDurationInMinutes =
      parseInt(updatedHours || '0') * 60 + parseInt(updatedMinutes || '0')
    const durationMinutes = parseMinutesToHours(updatedDurationInMinutes)
    helpers.setValue(durationMinutes)
  }

  const onDurationChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const durationInputValue = event.target.value
    const durationInputValueReplaced = durationInputValue.replace(
      /[^\d:]+/g,
      ''
    )
    helpers.setValue(durationInputValueReplaced)
  }

  return (
    <TextInput
      name={field.name}
      label={label}
      onChange={onDurationChange}
      onBlur={onDurationBlur}
      className={className}
      isOptional={isOptional}
      placeholder="HH:MM"
    />
  )
}

export default DurationInput
