import PropTypes from 'prop-types'
import React from 'react'

const Select = ({ className, defaultLabel, onOptionClick, options, value }) => {
  return (
    <select
      className={className || 'select'}
      onBlur={onOptionClick}
      value={value || defaultLabel}
    >
      <option
        disabled
        key={-1}
      >
        {defaultLabel}
      </option>
      {options.map(({ label, value }) => (
        <option
          key={value}
          value={value}
        >
          {label}
        </option>
      ))}
    </select>
  )
}

Select.propTypes = {
  className: PropTypes.string.isRequired,
  defaultLabel: PropTypes.string.isRequired,
  onOptionClick: PropTypes.func.isRequired,
  options: PropTypes.arrayOf(PropTypes.shape()).isRequired,
  value: PropTypes.string.isRequired,
}

export default Select
