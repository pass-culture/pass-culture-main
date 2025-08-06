import * as DropdownMenu from '@radix-ui/react-dropdown-menu'
import cn from 'classnames'

import fullOtherIcon from '@/icons/full-other.svg'
import { ListIconButton } from '@/ui-kit/ListIconButton/ListIconButton'
import { SvgIcon } from '@/ui-kit/SvgIcon/SvgIcon'

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
 *
 * @accessibility
 * - **Dropdown Trigger**: The trigger button includes a `title` attribute to provide additional context for screen readers.
 * - **Keyboard Navigation**: The dropdown menu can be opened and closed using keyboard interactions, ensuring accessibility for all users.
 */
export function DropdownMenuWrapper({
  title,
  triggerIcon,
  triggerTooltip,
  children,
  triggerClassName,
  contentClassName,
  dropdownTriggerRef,
}: DropdownMenuWrapperProps): JSX.Element {
  const icon = triggerIcon || fullOtherIcon

  return (
    <DropdownMenu.Root>
      <DropdownMenu.Trigger
        className={cn(styles['menu-button'], triggerClassName)}
        data-testid="dropdown-menu-trigger"
        {...(triggerTooltip ? { asChild: true } : {})}
        ref={dropdownTriggerRef}
      >
        {triggerTooltip ? (
          <ListIconButton icon={icon} tooltipContent={<>{title}</>} />
        ) : (
          <SvgIcon
            src={icon}
            alt={title}
            className={styles['menu-button-icon']}
          />
        )}
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
