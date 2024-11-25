import * as DropdownMenu from '@radix-ui/react-dropdown-menu'
import cn from 'classnames'

import fullOtherIcon from 'icons/full-other.svg'
import { SvgIcon } from 'ui-kit/SvgIcon/SvgIcon'

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
   * The content to be displayed inside the dropdown menu.
   */
  children: React.ReactNode
  /**
   * Custom CSS class for additional styling of the dropdown menu.
   */
  className?: string
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
  children,
  className,
}: DropdownMenuWrapperProps): JSX.Element {
  return (
    <DropdownMenu.Root>
      <DropdownMenu.Trigger
        className={cn(styles['menu-button'], className)}
        title={title}
        data-testid="dropdown-menu-trigger"
      >
        <SvgIcon
          src={fullOtherIcon}
          alt={title}
          className={styles['menu-button-icon']}
        />
      </DropdownMenu.Trigger>
      <DropdownMenu.Portal>
        <DropdownMenu.Content className={styles['menu-list']} align="end">
          {children}
        </DropdownMenu.Content>
      </DropdownMenu.Portal>
    </DropdownMenu.Root>
  )
}
