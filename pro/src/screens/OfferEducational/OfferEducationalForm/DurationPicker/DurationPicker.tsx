import { useField } from 'formik'
import React, { useCallback, useState } from 'react'

import { translateMinutesToHours } from './utils/translateMinutesToHours'

type DurationPickerProps = {
  label?: string;
  name: string;
  className?: string;
  onChange: (value: number | null) => void;
}

const DurationPicker = ({
  label,
  name,
  className,
  onChange,
}: DurationPickerProps): JSX.Element => {
  const [field, meta] = useField({ name, className })
  const [durationInHours, setDurationInHours] = useState(translateMinutesToHours(field.value))
    
  const onDurationBlur = useCallback(
    (event: React.FocusEvent<HTMLInputElement>) => {
      const updatedHoursDuration = event.target.value
    
      if (updatedHoursDuration !== '') {
        const [updatedHours, updatedMinutes] = updatedHoursDuration.split(':')
    
        const updatedDurationInMinutes =
                parseInt(updatedHours || '0') * 60 + parseInt(updatedMinutes || '0')
        setDurationInHours(translateMinutesToHours(updatedDurationInMinutes))
        onChange(updatedDurationInMinutes)
      } else {
        onChange(null)
      }
    },
    [onChange]
  )
    
  const onDurationChange = useCallback((event: React.ChangeEvent<HTMLInputElement>) => {
    const updatedHoursDuration = event.target.value
    let correctedHoursDuration
    
    const hasFinishedWritingHours = /[0-9]+:/.test(updatedHoursDuration)
    if (hasFinishedWritingHours) {
      correctedHoursDuration = updatedHoursDuration?.match(/[0-9]+:[0-5]?[0-9]?/)?.[0] || '0'
      setDurationInHours(correctedHoursDuration)
    } else {
      correctedHoursDuration = updatedHoursDuration?.match(/[0-9]*/)?.[0] || '0'
      setDurationInHours(correctedHoursDuration)
    }
  }, [])

  return (
    <>
      <label>
        {label}
        <input
          {...field}
          onBlur={onDurationBlur}
          onChange={onDurationChange}
          placeholder="HH:MM"
          value={durationInHours}
        />
      </label>
      {meta.touched && meta.error ? (
        <div className="error">
          {meta.error}
        </div>
      ) : null}
    </>
  )
}

export default DurationPicker
