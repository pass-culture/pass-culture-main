import PropTypes from 'prop-types'
import React from 'react'

import InputError from '../Errors/InputError'

const TextInput = ({
  countCharacters,
  disabled,
  error,
  label,
  maxLength,
  name,
  onChange,
  placeholder,
  required,
  subLabel,
  type,
  value,
}) => (
  <label className="input-text">
    <div className="labels">
      {label}
      <span className="it-sub-label">
        {subLabel}
      </span>
    </div>
    <input
      className={`it-input ${error ? 'error' : ''}`}
      disabled={disabled}
      id={name}
      maxLength={maxLength}
      name={name}
      onChange={onChange}
      placeholder={placeholder}
      required={required}
      type={type}
      value={value}
    />
    {error && (
      <InputError
        message={error}
        name={name}
      />
    )}
    {countCharacters && (
      <span className="it-character-count">
        {`${value ? value.length : 0}/${maxLength}`}
      </span>
    )}
  </label>
)

TextInput.defaultProps = {
  countCharacters: false,
  disabled: false,
  error: null,
  maxLength: null,
  onChange: null,
  placeholder: '',
  required: false,
  subLabel: '',
  type: 'text',
  value: '',
}

TextInput.propTypes = {
  countCharacters: PropTypes.bool,
  disabled: PropTypes.bool,
  error: PropTypes.string,
  label: PropTypes.string.isRequired,
  maxLength: PropTypes.number,
  name: PropTypes.string.isRequired,
  onChange: PropTypes.func,
  placeholder: PropTypes.string,
  required: PropTypes.bool,
  subLabel: PropTypes.string,
  type: PropTypes.string,
  value: PropTypes.string,
}

export default TextInput
