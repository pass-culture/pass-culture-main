import PropTypes from 'prop-types'
import React from 'react'

import TextInputError from '../Errors/TextInputError'

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
  sublabel,
  type,
  value,
}) => (
  <label
    className="input-text"
    htmlFor={name}
  >
    <div className="labels">
      {label}
      <span className="it-sub-label">
        {sublabel}
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
    {error && <TextInputError message={error} />}
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
  required: false,
  sublabel: '',
  type: 'text',
}

TextInput.propTypes = {
  countCharacters: PropTypes.bool,
  disabled: PropTypes.bool,
  error: PropTypes.string,
  label: PropTypes.string.isRequired,
  maxLength: PropTypes.number,
  name: PropTypes.string.isRequired,
  onChange: PropTypes.func,
  placeholder: PropTypes.string.isRequired,
  required: PropTypes.bool,
  sublabel: PropTypes.string,
  type: PropTypes.string,
  value: PropTypes.string.isRequired,
}

export default TextInput
