import React from 'react'
import PropTypes from 'prop-types'

const Select = ({
  defaultOption,
  isDisabled,
  handleSelection,
  label,
  name,
  options,
  required,
  selectedValue,
}) => (
  <div className="input-select">
    <label htmlFor={name}>
      {label}
    </label>
    <select
      disabled={isDisabled}
      id={name}
      name={name}
      onBlur={handleSelection}
      onChange={handleSelection}
      required={required}
      value={selectedValue || defaultOption.id}
    >
      <option value={defaultOption.id}>
        {defaultOption.displayName}
      </option>
      {options.map(option => (
        <option
          key={option.id}
          value={option.id}
        >
          {option.displayName}
        </option>
      ))}
    </select>
  </div>
)

Select.defaultProps = {
  isDisabled: false,
  required: false,
}

Select.propTypes = {
  defaultOption: PropTypes.shape({
    displayName: PropTypes.string.isRequired,
    id: PropTypes.string.isRequired,
  }).isRequired,
  handleSelection: PropTypes.func.isRequired,
  isDisabled: PropTypes.bool,
  label: PropTypes.string.isRequired,
  name: PropTypes.string.isRequired,
  options: PropTypes.arrayOf(
    PropTypes.shape({
      displayName: PropTypes.string.isRequired,
      id: PropTypes.string.isRequired,
    })
  ).isRequired,
  required: PropTypes.bool,
  selectedValue: PropTypes.string.isRequired,
}

export default Select
