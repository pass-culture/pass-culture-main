import type * as React from 'react'

import { Button } from '@/design-system/Button/Button'
import {
  ButtonColor,
  ButtonSize,
  ButtonVariant,
} from '@/design-system/Button/types'
import fullOtherIcon from '@/icons/full-other.svg'

import { Dropdown } from './Dropdown'

type DropdownMenuWrapperProps = {
  title: string
  triggerIcon?: string
  triggerTooltip?: boolean
  children: React.ReactNode
  contentClassName?: string
  dropdownTriggerRef?: React.RefObject<HTMLButtonElement>
}

export function DropdownMenuWrapper({
  title,
  triggerIcon,
  triggerTooltip,
  children,
  contentClassName,
  dropdownTriggerRef,
}: DropdownMenuWrapperProps): JSX.Element {
  const icon = triggerIcon || fullOtherIcon

  return (
    <Dropdown
      contentClassName={contentClassName}
      align="end"
      trigger={
        <Button
          ref={dropdownTriggerRef}
          variant={ButtonVariant.SECONDARY}
          color={ButtonColor.NEUTRAL}
          size={ButtonSize.SMALL}
          icon={icon}
          tooltip={triggerTooltip ? title : undefined}
          aria-label={title}
        />
      }
    >
      {children}
    </Dropdown>
  )
}
