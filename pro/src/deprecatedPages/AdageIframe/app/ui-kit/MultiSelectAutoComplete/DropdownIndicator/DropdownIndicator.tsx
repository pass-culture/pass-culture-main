import cn from 'classnames'
import React from 'react'
import { components } from 'react-select'
import type { DropdownIndicatorProps } from 'react-select'

import { Option } from 'deprecatedPages/AdageIframe/app/types'
import { ReactComponent as ChevronIconAdage } from 'icons/ico-chevron-adage.svg'

const DropdownIndicator = <T,>(
  props: DropdownIndicatorProps<Option<T>>
): JSX.Element => (
  <components.DropdownIndicator {...props}>
    <ChevronIconAdage
      className={cn('dropdown-indicator', {
        'dropdown-indicator-is-closed': !props.selectProps.menuIsOpen,
      })}
    />
  </components.DropdownIndicator>
)

export default DropdownIndicator
