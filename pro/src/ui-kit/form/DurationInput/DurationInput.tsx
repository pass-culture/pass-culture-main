import fr from 'date-fns/locale/fr'
import { useField } from 'formik'
import React, { ChangeEvent, useCallback } from 'react'

import TextInput from '../TextInput'

interface IDurationInput {
  label: string
  name: string
  placeholder: string
  isOptional?: boolean
  className?: string
}

const DurationInput = ({
  label,
  name,
  placeholder,
  isOptional = false,
  className,
}: IDurationInput): JSX.Element => {
  const [field, meta, helpers] = useField({ name })

  const translateMinutesToHours = (durationInMinutes: number | null) => {
    if (durationInMinutes === null) return ''
    const hours = Math.floor(durationInMinutes / 60)
    const minutes = (durationInMinutes % 60).toString().padStart(2, '0')
    return `${hours}:${minutes}`
  }

  const onDurationBlur = (event: React.FocusEvent<HTMLInputElement>) => {
    const updatedHoursDuration = event.target.value

    if (!meta.touched) {
      helpers.setTouched(true, false)
    }

    if (updatedHoursDuration !== '') {
      const [updatedHours, updatedMinutes] = updatedHoursDuration.split(':')

      const updatedDurationInMinutes =
        parseInt(updatedHours || '0') * 60 + parseInt(updatedMinutes || '0')
      const durationMinutes = translateMinutesToHours(updatedDurationInMinutes)
      translateMinutesToHours(updatedDurationInMinutes)
      helpers.setValue(durationMinutes)
    } else {
      helpers.setValue('')
    }
  }
  const onDurationChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const durationInputValue = event.target.value
    if (durationInputValue !== '' && !/^[\d:]*$/.test(durationInputValue)) {
      const durationInputValueReplaced = durationInputValue.match(/^[\d:]*$/)
      helpers.setValue(durationInputValueReplaced)
    } else {
      helpers.setValue(durationInputValue)
    }
  }
  return (
    <TextInput
      name={name}
      label={label}
      placeholder={placeholder}
      onChange={onDurationChange}
      onBlur={onDurationBlur}
      className={className}
      isOptional={isOptional}
    />
  )
}

export default DurationInput
