import cn from 'classnames'
import React from 'react'
import { components } from 'react-select'
import type { DropdownIndicatorProps } from 'react-select'

import strokeUpIcon from 'icons/stroke-up.svg'
import { Option } from 'pages/AdageIframe/app/types'
import './DropdownIndicator.scss'
import { SvgIcon } from 'ui-kit/SvgIcon/SvgIcon'

const DropdownIndicator = <T,>(
  props: DropdownIndicatorProps<Option<T>>
): JSX.Element => (
  <components.DropdownIndicator {...props}>
    <SvgIcon
      alt=""
      src={strokeUpIcon}
      className={cn('dropdown-indicator', {
        'dropdown-indicator-is-closed': !props.selectProps.menuIsOpen,
      })}
    />
  </components.DropdownIndicator>
)

export default DropdownIndicator
