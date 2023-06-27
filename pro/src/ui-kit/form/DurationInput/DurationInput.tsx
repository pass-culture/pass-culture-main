import { useField } from 'formik'
import React from 'react'

import TextInput from '../TextInput'

import { parseMinutesToHours } from './utils/parseMinutesToHours'

export interface DurationInputProps {
  label: string
  name: string
  isOptional?: boolean
  className?: string
  disabled?: boolean
}

const DurationInput = ({
  label,
  name,
  isOptional = false,
  className,
  disabled,
  ...props
}: DurationInputProps): JSX.Element => {
  const [field, , helpers] = useField({ name })

  const onDurationBlur = (event: React.FocusEvent<HTMLInputElement>) => {
    const [updatedHours, updatedMinutes] = event.target.value.split(':')
    const updatedDurationInMinutes =
      parseInt(updatedHours || '0') * 60 + parseInt(updatedMinutes || '0')
    const durationMinutes = parseMinutesToHours(updatedDurationInMinutes)

    helpers.setValue(durationMinutes)
  }

  const onDurationChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const durationInputValue = event.target.value.match(/\d*:?[0-5]?\d?/)
    durationInputValue &&
      durationInputValue.length > 0 &&
      helpers.setValue(durationInputValue[0])
  }

  return (
    <TextInput
      name={field.name}
      value={field.value || ''}
      label={label}
      onChange={onDurationChange}
      onBlur={onDurationBlur}
      className={className}
      isOptional={isOptional}
      placeholder="HH:MM"
      disabled={disabled}
      {...props}
    />
  )
}

export default DurationInput
