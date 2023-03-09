import React, { useEffect, useState } from 'react'
import { components } from 'react-select'
import type { OptionProps } from 'react-select'

import { Option } from 'pages/AdageIframe/app/types'
import './Option.scss'
import { BaseCheckbox } from 'ui-kit/form/shared'

const CustomOption = <T,>({
  isSelected,
  label,
  ...props
}: OptionProps<Option<T>>): JSX.Element => {
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

export default CustomOption
