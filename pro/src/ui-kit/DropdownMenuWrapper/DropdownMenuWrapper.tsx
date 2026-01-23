import * as DropdownMenu from '@radix-ui/react-dropdown-menu'
import cn from 'classnames'

import { Button } from '@/design-system/Button/Button'
import {
  ButtonColor,
  ButtonSize,
  ButtonVariant,
} from '@/design-system/Button/types'
import fullOtherIcon from '@/icons/full-other.svg'

import styles from './DropdownMenuWrapper.module.scss'

/**
 * Props for the DropdownMenuWrapper component.
 */
type DropdownMenuWrapperProps = {
  /**
   * The title of the dropdown menu.
   */
  title: string
  /**
   * The tooltip to be displayed on the trigger button.
   */
  triggerTooltip?: boolean
  /**
   * The icon to be displayed on the trigger button.
   */
  triggerIcon?: string
  /**
   * The content to be displayed inside the dropdown menu.
   */
  children: React.ReactNode
  /**
   * Custom CSS class for additional styling of the trigger button.
   */
  triggerClassName?: string
  /**
   * Custom CSS class for additional styling of the menu content.
   */
  contentClassName?: string
  /**
   * Ref of the button triggering the openign of the dropdown
   */
  dropdownTriggerRef?: React.RefObject<HTMLButtonElement>
}

/**
 * The DropdownMenuWrapper component provides a wrapper for a dropdown menu.
 * It includes a trigger button with an icon, and displays menu content when triggered.
 *
 * ---
 * **Important: Use the `title` prop to describe the purpose of the dropdown menu.**
 * ---
 *
 * @param {DropdownMenuWrapperProps} props - The props for the DropdownMenuWrapper component.
 * @returns {JSX.Element} The rendered DropdownMenuWrapper component.
 *
 * @example
 * <DropdownMenuWrapper title="Options">
 *   <DropdownItem title="Settings" onSelect={() => console.log('Settings selected')}>Settings</DropdownItem>
 * </DropdownMenuWrapper>
 */
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
    <DropdownMenu.Root>
      <DropdownMenu.Trigger
        data-testid="dropdown-menu-trigger"
        {...(triggerTooltip ? { asChild: true } : {})}
        ref={dropdownTriggerRef}
      >
        <Button
          variant={ButtonVariant.SECONDARY}
          color={ButtonColor.NEUTRAL}
          size={ButtonSize.SMALL}
          icon={icon}
          tooltip={title}
        />
      </DropdownMenu.Trigger>
      <DropdownMenu.Portal>
        <DropdownMenu.Content
          className={cn(styles['menu-list'], contentClassName)}
          align="end"
        >
          {children}
        </DropdownMenu.Content>
      </DropdownMenu.Portal>
    </DropdownMenu.Root>
  )
}
