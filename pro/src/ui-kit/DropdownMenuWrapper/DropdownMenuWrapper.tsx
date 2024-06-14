import * as DropdownMenu from '@radix-ui/react-dropdown-menu'
import cn from 'classnames'

import fullOtherIcon from 'icons/full-other.svg'
import { SvgIcon } from 'ui-kit/SvgIcon/SvgIcon'

import styles from './DropdownMenuWrapper.module.scss'

type DropdownMenuWrapperProps = {
  title: string
  children: React.ReactNode
  className?: string
}

export function DropdownMenuWrapper({
  title,
  children,
  className,
}: DropdownMenuWrapperProps) {
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
