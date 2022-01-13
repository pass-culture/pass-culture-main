import React from 'react'
import Select from 'react-select'

import { Option } from 'app/types'

import CustomDropdownIndicator from './DropdownIndicator'
import CustomOption from './Option/Option'
import './MultiSelectAutocomplete.scss'

interface MultiSelectAutocompleteProps {
  options: Option[]
  onChange: (selectedOptions: Option[]) => void
  label?: string
}
const MultiSelectAutocomplete = ({
  options,
  onChange,
  label,
}: MultiSelectAutocompleteProps): JSX.Element => (
  <div className="multi-select-autocomplete-container">
    <label
      className="multi-select-autocomplete-label"
      htmlFor={`multi-select-autocmplete-${label}`}
    >
      {label}
    </label>

    <Select
      classNamePrefix="multi-select-autocomplete"
      components={{
        Option: CustomOption,
        DropdownIndicator: CustomDropdownIndicator,
      }}
      controlShouldRenderValue={false}
      hideSelectedOptions={false}
      isClearable={false}
      isMulti
      name={`multi-select-autocmplete-${label}`}
      onChange={onChange}
      options={options}
      placeholder="Sélectionner"
    />
  </div>
)

export default MultiSelectAutocomplete
