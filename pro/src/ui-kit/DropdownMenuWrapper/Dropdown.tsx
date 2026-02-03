import * as DropdownMenu from '@radix-ui/react-dropdown-menu'
import cn from 'classnames'
import type * as React from 'react'

import { DropdownItem } from './DropdownItem'
import styles from './DropdownMenuWrapper.module.scss'

type DropdownOption = {
  id: string
  title?: string
  disabled?: boolean
  onSelect?: () => void
  element: React.ReactNode
}

export type DropdownProps = {
  /** Trigger slot rendered with Radix Trigger asChild */
  trigger: React.ReactNode

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
}

export function Dropdown({
  trigger,
  open,
  defaultOpen,
  onOpenChange,
  children,
  options,
  align = 'end',
  sideOffset = 4,
  contentClassName,
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
        {trigger}
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
