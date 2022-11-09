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
    const [updatedHours, updatedMinutes] = event.target.value.split(':')
    const updatedDurationInMinutes =
      parseInt(updatedHours || '0') * 60 + parseInt(updatedMinutes || '0')
    const durationMinutes = parseMinutesToHours(updatedDurationInMinutes)

    helpers.setValue(durationMinutes)
  }

  const onDurationChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const durationInputValue = event.target.value.match(/\d*:?[0-5]?\d?/)
    durationInputValue && helpers.setValue(durationInputValue[0])
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
