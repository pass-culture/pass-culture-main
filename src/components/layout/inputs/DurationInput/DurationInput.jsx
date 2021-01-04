import PropTypes from 'prop-types'
import React, { useCallback, useState } from 'react'

import InputError from '../Errors/InputError'

const translateMinutesToHours = durationInMinutes => {
  if (durationInMinutes === null) return ''
  const hours = Math.floor(durationInMinutes / 60)
  const minutes = (durationInMinutes % 60).toString().padStart(2, '0')
  return `${hours}:${minutes}`
}

const validHoursDuration = durationInHours => durationInHours.match(/[0-9]*:[0-5][0-9]/)

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

  const onDurationChange = useCallback(
    event => {
      const updatedHoursDuration = event.target.value
      let correctedHoursDuration

      const hasFinishedWritingHours = /[0-9]+:/.test(updatedHoursDuration)
      if (hasFinishedWritingHours) {
        const hasFinishedWritingMinutes = /[0-9]+:[0-5][0-9]/.test(updatedHoursDuration)
        const hasBegunWritingMinutes = /[0-9]+:[0-5]/.test(updatedHoursDuration)

        if (hasFinishedWritingMinutes) {
          correctedHoursDuration = updatedHoursDuration.match(/[0-9]+:[0-5][0-9]/)[0]
          setDurationInHours(correctedHoursDuration)
        } else if (hasBegunWritingMinutes) {
          correctedHoursDuration = updatedHoursDuration.match(/[0-9]+:[0-5]/)[0]
          setDurationInHours(correctedHoursDuration)
        } else {
          correctedHoursDuration = updatedHoursDuration.match(/[0-9]+:/)[0]
          setDurationInHours(correctedHoursDuration)
        }
      } else {
        correctedHoursDuration = updatedHoursDuration.match(/[0-9]*/)[0]
        setDurationInHours(correctedHoursDuration)
      }

      if (validHoursDuration(correctedHoursDuration)) {
        const [updatedHours, updatedMinutes] = correctedHoursDuration.split(':')
        const updatedDurationInMinutes = parseInt(updatedHours) * 60 + parseInt(updatedMinutes)
        onChange(updatedDurationInMinutes)
      } else if (correctedHoursDuration === '') {
        onChange(null)
      }
    },
    [onChange]
  )

  return (
    <label className="input-time">
      <div className="labels">
        {label}
        <span className="itime-sub-label">
          {subLabel}
        </span>
      </div>
      <span className={`itime-field-container ${error ? 'error' : ''}`}>
        <input
          className="itime-field"
          disabled={disabled}
          name={name}
          onChange={onDurationChange}
          placeholder="HH:MM"
          required={required}
          type="text"
          value={durationInHours}
        />
      </span>
      {error && (
        <InputError
          message={error}
          name={name}
        />
      )}
    </label>
  )
}

DurationInput.defaultProps = {
  disabled: false,
  error: null,
  initialDurationInMinutes: null,
  onChange: null,
  required: false,
  subLabel: '',
}

DurationInput.propTypes = {
  disabled: PropTypes.bool,
  error: PropTypes.string,
  initialDurationInMinutes: PropTypes.number,
  label: PropTypes.string.isRequired,
  name: PropTypes.string.isRequired,
  onChange: PropTypes.func,
  required: PropTypes.bool,
  subLabel: PropTypes.string,
}

export default DurationInput
