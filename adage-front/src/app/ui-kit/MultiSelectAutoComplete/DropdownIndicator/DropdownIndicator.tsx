import cn from 'classnames'
import React from 'react'
import { components } from 'react-select'
import type { DropdownIndicatorProps } from 'react-select'

import { ReactComponent as Chevron } from 'assets/chevron.svg'

import './DropdownIndicator.scss'

const DropdownIndicator = (props: DropdownIndicatorProps): JSX.Element => (
  <components.DropdownIndicator {...props}>
    <Chevron
      className={cn('dropdown-indicator', {
        'dropdown-indicator-is-closed': !props.selectProps.menuIsOpen,
      })}
    />
  </components.DropdownIndicator>
)

export default DropdownIndicator
