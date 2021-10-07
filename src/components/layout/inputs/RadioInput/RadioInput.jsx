/*
 * @debt directory "Gaël: this file should be migrated within the new directory structure"
 */

import PropTypes from 'prop-types'
import React from 'react'

export const RadioInput = ({ onChange, value, name, label, checked, disabled, subLabel }) => (
  <label className="field-radio">
    <input
      checked={checked}
      className="field-radio-input"
      disabled={disabled}
      name={name}
      onChange={onChange}
      type="radio"
      value={value}
    />
    <span className={`field-radio-label ${disabled?'disabled':''}`}>
      {label}
      {subLabel && (
        <span className={`field-radio-sub-label ${disabled ? 'disabled' : ''}`}>
          {subLabel}
        </span>
      )}
    </span>
  </label>
)

RadioInput.defaultProps = {
  disabled: false,
  subLabel: null,
}

RadioInput.propTypes = {
  checked: PropTypes.bool.isRequired,
  disabled: PropTypes.bool,
  label: PropTypes.string.isRequired,
  name: PropTypes.string.isRequired,
  onChange: PropTypes.func.isRequired,
  subLabel: PropTypes.string,
  value: PropTypes.string.isRequired,
}
