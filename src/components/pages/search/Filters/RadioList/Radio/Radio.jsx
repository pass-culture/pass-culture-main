import React from 'react'
import PropTypes from "prop-types"
import Icon from "../../../../../layout/Icon/Icon"

export const Radio = ({ option, onDateSelection, selectedDateOption }) => {
  return (
    <li>
      <input
        id={option.id}
        name="dateOption"
        onChange={onDateSelection}
        type="radio"
        value={option.value}
      />
      <label
        className={selectedDateOption === option.value ? 'sf-filter-checked' : ''}
        htmlFor={option.id}
      >
        {option.label}
      </label>
      {selectedDateOption === option.value && <Icon svg="ico-check-pink" />}
    </li>
  )
}

Radio.propTypes = {
  onDateSelection: PropTypes.func.isRequired,
  option: PropTypes.shape({
    id: PropTypes.string.isRequired,
    value: PropTypes.string.isRequired,
    label: PropTypes.string.isRequired,
  }).isRequired,
  selectedDateOption: PropTypes.string.isRequired
}
