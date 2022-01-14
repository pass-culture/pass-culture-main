import React from 'react'
import { components } from 'react-select'
import type { PlaceholderProps } from 'react-select'

import { Option } from 'app/types'

const Placeholder = ({ ...props }: PlaceholderProps): JSX.Element => {
  const selectedValues = props.selectProps.value as Option[] | null
  const hasMultipleSelectedValues = selectedValues && selectedValues.length > 0

  return (
    <components.Placeholder {...props}>
      {hasMultipleSelectedValues
        ? props.selectProps.name
        : props.selectProps.placeholder}
    </components.Placeholder>
  )
}

export default Placeholder
