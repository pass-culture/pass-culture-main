import { useField } from 'formik'
import React from 'react'

import { TextInput } from '../TextInput/TextInput'

import { parseMinutesToHours } from './utils/parseMinutesToHours'

export interface DurationInputProps {
  label: string
  name: string
  isOptional?: boolean
  className?: string
  disabled?: boolean
}

export const DurationInput = ({
  label,
  name,
  isOptional = false,
  className,
  disabled,
  ...props
}: DurationInputProps): JSX.Element => {
  const [field, , helpers] = useField({ name })

  const onDurationBlur = async (event: React.FocusEvent<HTMLInputElement>) => {
    const [updatedHours, updatedMinutes] = event.target.value.split(':')
    const updatedDurationInMinutes =
      parseInt(updatedHours || '0') * 60 + parseInt(updatedMinutes || '0')
    const durationMinutes = parseMinutesToHours(updatedDurationInMinutes)

    await helpers.setValue(durationMinutes)
  }

  const onDurationChange = async (
    event: React.ChangeEvent<HTMLInputElement>
  ) => {
    const durationInputValue = event.target.value.match(/\d*:?[0-5]?\d?/)
    if (durationInputValue && durationInputValue.length > 0) {
      await helpers.setValue(durationInputValue[0])
    }
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
      description="Format : HH:MM"
      disabled={disabled}
      {...props}
    />
  )
}
