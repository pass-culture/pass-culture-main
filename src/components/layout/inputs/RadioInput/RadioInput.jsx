import PropTypes from 'prop-types'
import React from 'react'

export const RadioInput = ({ onChange, value, name, label, checked }) => (
  <label>
    <input
      checked={checked}
      className="input-radio"
      name={name}
      onChange={onChange}
      type="radio"
      value={value}
    />
    {label}
  </label>
)

RadioInput.propTypes = {
  checked: PropTypes.bool.isRequired,
  label: PropTypes.string.isRequired,
  name: PropTypes.string.isRequired,
  onChange: PropTypes.func.isRequired,
  value: PropTypes.string.isRequired,
}
