import React from 'react'
import Select from 'react-select'

import { Option } from 'app/types'

import CustomControl from './Control'
import CustomDropdownIndicator from './DropdownIndicator'
import CustomOption from './Option'
import CustomPlaceholder from './Placeholder'
import './MultiSelectAutocomplete.scss'

interface MultiSelectAutocompleteProps {
  options: Option[]
  onChange: (selectedOptions: Option[]) => void
  label?: string
  initialValues: Option[]
}
const MultiSelectAutocomplete = ({
  options,
  onChange,
  label,
  initialValues,
}: MultiSelectAutocompleteProps): JSX.Element => (
  <div className="multi-select-autocomplete-container">
    <label
      className="multi-select-autocomplete-label"
      htmlFor={`multi-select-autocomplete-${label}`}
    >
      {label}
    </label>

    <Select
      classNamePrefix="multi-select-autocomplete"
      closeMenuOnSelect={false}
      components={{
        Option: CustomOption,
        DropdownIndicator: CustomDropdownIndicator,
        Control: CustomControl,
        Placeholder: CustomPlaceholder,
      }}
      controlShouldRenderValue={false}
      hideSelectedOptions={false}
      inputId={`multi-select-autocomplete-${label}`}
      isClearable={false}
      isMulti
      name={label}
      noOptionsMessage={() => 'Aucun résultat'}
      onChange={onChange}
      options={options}
      placeholder="Sélectionner"
      value={initialValues}
    />
  </div>
)

export default MultiSelectAutocomplete
