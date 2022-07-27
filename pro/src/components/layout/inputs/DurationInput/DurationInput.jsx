import PropTypes from 'prop-types'
import React, { useCallback, useState } from 'react'

import InputError from '../Errors/InputError'

const translateMinutesToHours = durationInMinutes => {
  if (durationInMinutes === null) return ''
  const hours = Math.floor(durationInMinutes / 60)
  const minutes = (durationInMinutes % 60).toString().padStart(2, '0')
  return `${hours}:${minutes}`
}

const DurationInput = ({
  disabled,
  error,
  label,
  name,
  onChange,
  required,
  subLabel,
  initialDurationInMinutes,
}) => {
  const [durationInHours, setDurationInHours] = useState(
    translateMinutesToHours(initialDurationInMinutes)
  )

  const onDurationBlur = useCallback(
    event => {
      const updatedHoursDuration = event.target.value

      if (updatedHoursDuration !== '') {
        const [updatedHours, updatedMinutes] = updatedHoursDuration.split(':')

        const updatedDurationInMinutes =
          parseInt(updatedHours) * 60 + parseInt(updatedMinutes | '0')
        setDurationInHours(translateMinutesToHours(updatedDurationInMinutes))
        onChange(updatedDurationInMinutes)
      } else {
        onChange(null)
      }
    },
    [onChange]
  )

  const onDurationChange = useCallback(event => {
    const updatedHoursDuration = event.target.value
    let correctedHoursDuration

    const hasFinishedWritingHours = /[0-9]+:/.test(updatedHoursDuration)
    if (hasFinishedWritingHours) {
      correctedHoursDuration =
        updatedHoursDuration.match(/[0-9]+:[0-5]?[0-9]?/)[0]
      setDurationInHours(correctedHoursDuration)
    } else {
      correctedHoursDuration = updatedHoursDuration.match(/[0-9]*/)[0]
      setDurationInHours(correctedHoursDuration)
    }
  }, [])

  return (
    <label className="input-time">
      <div className="labels">
        {label}
        <span className="itime-sub-label">{subLabel}</span>
      </div>
      <span className={`itime-field-container ${error ? 'error' : ''}`}>
        <input
          className="itime-field"
          disabled={disabled}
          name={name}
          onBlur={onDurationBlur}
          onChange={onDurationChange}
          placeholder="HH:MM"
          required={required}
          type="text"
          value={durationInHours}
        />
      </span>
      {error && <InputError name={name}>{error}</InputError>}
    </label>
  )
}

DurationInput.defaultProps = {
  disabled: false,
  error: null,
  initialDurationInMinutes: null,
  required: false,
  subLabel: '',
}

DurationInput.propTypes = {
  disabled: PropTypes.bool,
  error: PropTypes.string,
  initialDurationInMinutes: PropTypes.number,
  label: PropTypes.string.isRequired,
  name: PropTypes.string.isRequired,
  onChange: PropTypes.func.isRequired,
  required: PropTypes.bool,
  subLabel: PropTypes.string,
}

export default DurationInput
