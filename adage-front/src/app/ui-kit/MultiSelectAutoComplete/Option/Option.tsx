import React, { useEffect, useState } from 'react'
import { components } from 'react-select'
import type { OptionProps } from 'react-select'

import BaseCheckbox from '../../Checkbox'

import './Option.scss'

const Option = ({ isSelected, label, ...props }: OptionProps): JSX.Element => {
  const [isCheckboxChecked, setIsCheckboxChecked] = useState(isSelected)

  useEffect(() => {
    setIsCheckboxChecked(isSelected)
  }, [isSelected])

  return (
    <components.Option {...props} isSelected={isSelected} label={label}>
      <BaseCheckbox
        checked={isCheckboxChecked}
        className="multi-select-autocomplete-option"
        label={label}
        onChange={() => setIsCheckboxChecked(!isCheckboxChecked)}
      />
    </components.Option>
  )
}

export default Option
