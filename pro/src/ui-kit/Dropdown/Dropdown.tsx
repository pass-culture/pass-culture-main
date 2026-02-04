import * as DropdownMenu from '@radix-ui/react-dropdown-menu'
import cn from 'classnames'
import type * as React from 'react'

import { Button } from '@/design-system/Button/Button'
import {
  ButtonColor,
  ButtonSize,
  ButtonVariant,
} from '@/design-system/Button/types'
import fullThreeDotsIcon from '@/icons/full-three-dots.svg'

import styles from './Dropdown.module.scss'
import { DropdownItem } from './DropdownItem'

type DropdownOption = {
  id: string
  title?: string
  disabled?: boolean
  onSelect?: () => void
  element: React.ReactNode
}

export type DropdownProps = {
  title?: string

  /** Trigger slot rendered with Radix Trigger asChild */
  trigger?: React.ReactNode

  /** Controlled/uncontrolled open state (optional) */
  open?: boolean
  defaultOpen?: boolean
  onOpenChange?: (open: boolean) => void

  /** Content */
  children?: React.ReactNode
  options?: DropdownOption[]

  /** Radix content config */
  align?: 'start' | 'center' | 'end'
  sideOffset?: number

  /** Styling */
  contentClassName?: string

  dropdownTriggerRef?: React.RefObject<HTMLButtonElement>

  triggerTooltip?: boolean
}

export function Dropdown({
  title,
  trigger,
  open,
  defaultOpen,
  onOpenChange,
  children,
  options,
  align = 'end',
  sideOffset = 4,
  contentClassName,
  dropdownTriggerRef,
  triggerTooltip,
}: DropdownProps): JSX.Element {
  const content =
    children ??
    options?.map((opt) => (
      <DropdownItem
        key={opt.id}
        title={opt.title}
        disabled={opt.disabled}
        onSelect={opt.onSelect}
      >
        {opt.element}
      </DropdownItem>
    ))

  return (
    <DropdownMenu.Root
      open={open}
      defaultOpen={defaultOpen}
      onOpenChange={onOpenChange}
    >
      <DropdownMenu.Trigger data-testid="dropdown-menu-trigger" asChild>
        {trigger ? (
          trigger
        ) : (
          <Button
            ref={dropdownTriggerRef}
            variant={ButtonVariant.SECONDARY}
            color={ButtonColor.NEUTRAL}
            size={ButtonSize.SMALL}
            icon={fullThreeDotsIcon}
            tooltip={triggerTooltip ? title : undefined}
            aria-label={title}
          />
        )}
      </DropdownMenu.Trigger>

      <DropdownMenu.Portal>
        <DropdownMenu.Content
          className={cn(styles['menu-list'], contentClassName)}
          align={align}
          sideOffset={sideOffset}
        >
          {content}
        </DropdownMenu.Content>
      </DropdownMenu.Portal>
    </DropdownMenu.Root>
  )
}
