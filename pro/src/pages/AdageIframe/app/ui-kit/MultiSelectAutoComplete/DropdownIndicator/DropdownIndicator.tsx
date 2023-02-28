import cn from 'classnames'
import React from 'react'
import { components } from 'react-select'
import type { DropdownIndicatorProps } from 'react-select'

import { Option } from 'pages/AdageIframe/app/types'
import { ReactComponent as Chevron } from 'pages/AdageIframe/assets/chevron.svg'

import './DropdownIndicator.scss'

const DropdownIndicator = <T,>(
  props: DropdownIndicatorProps<Option<T>>
): JSX.Element => (
  <components.DropdownIndicator {...props}>
    <Chevron
      className={cn('dropdown-indicator', {
        'dropdown-indicator-is-closed': !props.selectProps.menuIsOpen,
      })}
    />
  </components.DropdownIndicator>
)

export default DropdownIndicator
