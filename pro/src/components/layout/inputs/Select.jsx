import PropTypes from 'prop-types'
import React from 'react'

import InputError from './Errors/InputError'

const Select = ({
  defaultOption,
  error,
  isDisabled,
  handleSelection,
  label,
  name,
  options,
  required,
  rightLabel,
  selectedValue,
  subLabel,
}) => (
  <div className="input-select">
    {label && (
      <label className="labels" htmlFor={name}>
        {label}
        {subLabel && <span className="it-sub-label">{subLabel}</span>}
      </label>
    )}
    <div
      className={rightLabel ? 'input-select-inline' : 'input-select-full-width'}
    >
      <select
        className={`${error ? 'error' : ''}`}
        disabled={isDisabled}
        id={name}
        name={name}
        onBlur={handleSelection}
        onChange={handleSelection}
        required={required}
        value={selectedValue || (defaultOption && defaultOption.id) || ''}
      >
        {defaultOption && (
          <option value={defaultOption.id}>{defaultOption.displayName}</option>
        )}
        {options.map(option => (
          <option key={option.id} value={option.id}>
            {option.displayName}
          </option>
        ))}
      </select>
      {rightLabel && (
        <span className="input-select-inline-label-complement">
          {rightLabel}
        </span>
      )}
    </div>
    {error && <InputError name={name}>{error}</InputError>}
  </div>
)

Select.defaultProps = {
  defaultOption: null,
  error: null,
  isDisabled: false,
  label: undefined,
  required: false,
  rightLabel: '',
  subLabel: '',
}

Select.propTypes = {
  defaultOption: PropTypes.shape({
    displayName: PropTypes.string.isRequired,
    id: PropTypes.string.isRequired,
  }),
  error: PropTypes.string,
  handleSelection: PropTypes.func.isRequired,
  isDisabled: PropTypes.bool,
  label: PropTypes.string,
  name: PropTypes.string.isRequired,
  options: PropTypes.arrayOf(
    PropTypes.shape({
      displayName: PropTypes.string.isRequired,
      id: PropTypes.string.isRequired,
    })
  ).isRequired,
  required: PropTypes.bool,
  rightLabel: PropTypes.string,
  selectedValue: PropTypes.string.isRequired,
  subLabel: PropTypes.string,
}

export default Select
