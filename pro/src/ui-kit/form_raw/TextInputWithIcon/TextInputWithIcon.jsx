import PropTypes from 'prop-types'
import React from 'react'

import InputError from '../Errors/InputError'

const TextInputWithIcon = ({
  disabled,
  error,
  icon,
  label,
  name,
  onChange,
  onIconClick,
  placeholder,
  required,
  sublabel,
  type,
  value,
}) => (
  <label className="input-text">
    <div className="labels">
      {label}
      <span className="it-sub-label">{sublabel}</span>
    </div>
    <div
      className={`it-with-icon-container${disabled ? ' disabled' : ''} ${
        error ? 'error' : ''
      }`}
    >
      <input
        className="it-input-with-icon"
        disabled={disabled}
        name={name}
        onChange={onChange}
        placeholder={placeholder}
        required={required}
        type={type}
        value={value}
      />
      <button className="it-icon" onClick={onIconClick} type="button">
        {icon}
      </button>
    </div>
    {error && <InputError>{error}</InputError>}
  </label>
)

TextInputWithIcon.defaultProps = {
  disabled: false,
  error: null,
  onChange: null,
  required: false,
  sublabel: '',
  type: 'text',
}

TextInputWithIcon.propTypes = {
  disabled: PropTypes.bool,
  error: PropTypes.string,
  icon: PropTypes.element.isRequired,
  label: PropTypes.string.isRequired,
  name: PropTypes.string.isRequired,
  onChange: PropTypes.func,
  onIconClick: PropTypes.func.isRequired,
  placeholder: PropTypes.string.isRequired,
  required: PropTypes.bool,
  sublabel: PropTypes.string,
  type: PropTypes.string,
  value: PropTypes.string.isRequired,
}

export default TextInputWithIcon
