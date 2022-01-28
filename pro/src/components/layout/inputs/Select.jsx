/*
 * @debt directory "Gaël: this file should be migrated within the new directory structure"
 */

import PropTypes from 'prop-types'
import React from 'react'

import InputError from './Errors/InputError'

export const buildSelectOptions = (idField, valueField, data) => {
  return data
    .map(item => ({
      id: item[idField].toString(),
      displayName: item[valueField],
    }))
    .sort((a, b) => a.displayName.localeCompare(b.displayName, 'fr'))
}

export const buildSelectOptionsWithOptionalFields = (
  idField,
  valueFields,
  data
) => {
  return data
    .map(item => {
      const [desiredValueField, defaultValueField] = valueFields

      return {
        id: item[idField].toString(),
        displayName: item[desiredValueField]
          ? item[desiredValueField]
          : item[defaultValueField],
      }
    })
    .sort((a, b) => a.displayName.localeCompare(b.displayName, 'fr'))
}

const Select = ({
  defaultOption,
  error,
  isDisabled,
  handleSelection,
  label,
  name,
  options,
  required,
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
    <select
      className={`${error ? 'error' : ''}`}
      disabled={isDisabled}
      id={name}
      name={name}
      onBlur={handleSelection}
      onChange={handleSelection}
      required={required}
      value={selectedValue || (defaultOption && defaultOption.id) || null}
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
    {error && <InputError name={name}>{error}</InputError>}
  </div>
)

Select.defaultProps = {
  defaultOption: null,
  error: null,
  isDisabled: false,
  label: undefined,
  required: false,
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
  selectedValue: PropTypes.string.isRequired,
  subLabel: PropTypes.string,
}

export default Select
