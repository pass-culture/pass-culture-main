import React from 'react'
import PropTypes from 'prop-types'
import Icon from "../../Icon"

const TextInput = ({
  disabled,
  errors,
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
      className="it-input"
      disabled={disabled}
      id={name}
      name={name}
      onChange={onChange}
      placeholder={placeholder}
      required={required}
      type={type}
      value={value}
    />
    {errors &&
      <span className="it-errors">
        <Icon
          alt="Une erreur est survenue"
          svg="picto-echec"
        />
        <pre>
          {errors}
        </pre>
      </span>}
  </label>
)

TextInput.defaultProps = {
  disabled: false,
  errors: null,
  onChange: null,
  required: false,
  sublabel: '',
  type: 'text',
}

TextInput.propTypes = {
  disabled: PropTypes.bool,
  errors: PropTypes.string,
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
