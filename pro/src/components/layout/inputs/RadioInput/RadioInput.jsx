import cn from 'classnames'
import PropTypes from 'prop-types'
import React from 'react'

export const RadioInput = ({
  onChange,
  value,
  name,
  label,
  checked,
  disabled,
  subLabel,
  error,
}) => (
  <label className="input-radio">
    <input
      checked={checked}
      className={cn('input-radio-input', { error })}
      disabled={disabled}
      name={name}
      onChange={onChange}
      type="radio"
      value={value}
    />
    <span className={`input-radio-label ${disabled ? 'disabled' : ''}`}>
      {label}
      {subLabel && (
        <span className={`input-radio-sub-label ${disabled ? 'disabled' : ''}`}>
          {subLabel}
        </span>
      )}
    </span>
  </label>
)

RadioInput.defaultProps = {
  disabled: false,
  error: null,
  subLabel: null,
}

RadioInput.propTypes = {
  checked: PropTypes.bool.isRequired,
  disabled: PropTypes.bool,
  error: PropTypes.string,
  label: PropTypes.string.isRequired,
  name: PropTypes.string.isRequired,
  onChange: PropTypes.func.isRequired,
  subLabel: PropTypes.string,
  value: PropTypes.string.isRequired,
}
