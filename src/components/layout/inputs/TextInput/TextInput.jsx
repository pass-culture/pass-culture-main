import PropTypes from 'prop-types'
import React from 'react'

import TextInputError from '../Errors/TextInputError'

const TextInput = ({
  disabled,
  error,
  label,
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
      name={name}
      onChange={onChange}
      placeholder={placeholder}
      required={required}
      type={type}
      value={value}
    />
    {error && <TextInputError message={error} />}
  </label>
)

TextInput.defaultProps = {
  disabled: false,
  error: null,
  onChange: null,
  required: false,
  sublabel: '',
  type: 'text',
}

TextInput.propTypes = {
  disabled: PropTypes.bool,
  error: PropTypes.string,
  label: PropTypes.string.isRequired,
  name: PropTypes.string.isRequired,
  onChange: PropTypes.func,
  placeholder: PropTypes.string.isRequired,
  required: PropTypes.bool,
  sublabel: PropTypes.string,
  type: PropTypes.string,
  value: PropTypes.string.isRequired,
}

export default TextInput
