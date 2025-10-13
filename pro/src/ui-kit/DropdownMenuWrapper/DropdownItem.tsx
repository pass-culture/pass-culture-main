import * as DropdownMenu from '@radix-ui/react-dropdown-menu'
import cn from 'classnames'

import styles from './DropdownMenuWrapper.module.scss'

/**
 * Props for the DropdownItem component.
 *
 * @extends DropdownMenu.DropdownMenuItemProps
 */
type DropdownItemProps = DropdownMenu.DropdownMenuItemProps & {
  /**
   * The title of the dropdown item.
   */
  title?: string
  /**
   * Callback function triggered when the dropdown item is selected.
   */
  onSelect?: () => void
  /**
   * The content to be displayed inside the dropdown item.
   */
  children: React.ReactNode
  /**
   * Indicates if the dropdown item is disabled.
   */
  disabled?: boolean
}

/**
 * The DropdownItem component represents an item within a dropdown menu.
 * It allows users to select an option, which can trigger a callback function.
 *
 * ---
 * **Important: Use the `onSelect` prop to handle actions when the dropdown item is selected.**
 * ---
 *
 * @param {DropdownItemProps} props - The props for the DropdownItem component.
 * @returns {JSX.Element} The rendered DropdownItem component.
 *
 * @example
 * <DropdownItem title="Settings" onSelect={() => console.log('Settings selected')}>
 *   Settings
 * </DropdownItem>
 *
 * @accessibility
 * - If present, the `title` attribute provides additional context for the dropdown item.
 */
export function DropdownItem({
  title,
  children,
  onSelect,
  disabled,
  ...radixDropdownItemProps
}: DropdownItemProps): JSX.Element {
  return (
    <DropdownMenu.Item
      className={cn(styles['menu-item'], {
        [styles['menu-item-disabled']]: disabled,
      })}
      onSelect={onSelect}
      disabled={disabled}
      {...(title ? { title } : {})}
      {...radixDropdownItemProps}
    >
      {children}
    </DropdownMenu.Item>
  )
}
