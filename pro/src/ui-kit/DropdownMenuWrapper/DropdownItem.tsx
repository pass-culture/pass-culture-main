import * as DropdownMenu from '@radix-ui/react-dropdown-menu'
import cn from 'classnames'

import styles from './DropdownMenuWrapper.module.scss'

type DropdownItemProps = {
  title: string
  onSelect?: () => void
  children: React.ReactNode
  disabled?: boolean
}

export function DropdownItem({
  title,
  children,
  onSelect,
  disabled,
}: DropdownItemProps) {
  return (
    <DropdownMenu.Item
      className={cn(styles['menu-item'], {
        [styles['menu-item-disabled']]: disabled,
      })}
      title={title}
      onSelect={onSelect}
      disabled={disabled}
    >
      {children}
    </DropdownMenu.Item>
  )
}
