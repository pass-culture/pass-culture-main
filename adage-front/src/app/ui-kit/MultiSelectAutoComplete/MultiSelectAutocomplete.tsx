import cn from 'classnames'
import React from 'react'
import Select from 'react-select'

import { Option } from 'app/types'

import CustomControl from './Control'
import CustomDropdownIndicator from './DropdownIndicator'
import CustomOption from './Option'
import CustomPlaceholder from './Placeholder'
import './MultiSelectAutocomplete.scss'

interface MultiSelectAutocompleteProps<T = string> {
  options: Option<T>[]
  onChange: (selectedOptions: Option<T>[]) => void
  label?: string
  initialValues: Option<T>[]
  className?: string
  pluralLabel: string
}

const MultiSelectAutocomplete = <T,>({
  options,
  onChange,
  label,
  initialValues,
  className,
  pluralLabel,
}: MultiSelectAutocompleteProps<T>): JSX.Element => {
  return (
    <div className={cn(className, 'multi-select-autocomplete-container')}>
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
        name={initialValues.length > 1 ? pluralLabel : label}
        noOptionsMessage={() => 'Aucun résultat'}
        onChange={onChange}
        options={options}
        placeholder="Sélectionner"
        value={initialValues}
      />
    </div>
  )
}

export default MultiSelectAutocomplete
