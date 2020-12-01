import PropTypes from 'prop-types'
import React from 'react'
import ReactTimeInput from 'react-time-input'

import TextInputError from 'components/layout/inputs/Errors/TextInputError'
import TextInput from 'components/layout/inputs/TextInput/TextInput'

const TimeInput = props => {
  const {
    error,
    label,
    name,
    onChange,
    readOnly,
    subLabel,
    value,
    // see https://www.npmjs.com/package/react-time-input
    ...ReactTimeInputProps
  } = props

  return (
    <label
      className="input-time"
      htmlFor={name}
    >
      <div className="labels">
        {label}
        {subLabel && (
          <span className="itime-sub-label">
            {subLabel}
          </span>
        )}
      </div>

      {readOnly ? (
        <TextInput
          disabled={readOnly}
          error={error}
          name={name}
          value={value}
        />
      ) : (
        <ReactTimeInput
          className={`itime-input ${error ? 'error' : ''}`}
          initTime={value}
          {...ReactTimeInputProps}
          onTimeChange={onChange}
        />
      )}
      {error && <TextInputError message={error} />}
    </label>
  )
}

TimeInput.defaultProps = {
  error: '',
  label: '',
  readOnly: false,
  subLabel: null,
  value: '01:00',
}

TimeInput.propTypes = {
  error: PropTypes.string,
  label: PropTypes.string,
  name: PropTypes.string.isRequired,
  onChange: PropTypes.func.isRequired,
  readOnly: PropTypes.bool,
  subLabel: PropTypes.string,
  value: PropTypes.string,
}

export default TimeInput
