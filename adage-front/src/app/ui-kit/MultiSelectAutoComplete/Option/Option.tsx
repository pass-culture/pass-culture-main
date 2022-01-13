import React from 'react'
import { components } from 'react-select'
import type { OptionProps } from 'react-select'

import BaseCheckbox from '../../Checkbox'

import './Option.scss'

const Option = ({ isSelected, label, ...props }: OptionProps): JSX.Element => (
  <components.Option {...props} isSelected={isSelected} label={label}>
    <BaseCheckbox
      checked={isSelected}
      className="multi-select-autocomplete-option"
      label={label}
    />
  </components.Option>
)

export default Option
