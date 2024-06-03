import * as DropdownMenu from '@radix-ui/react-dropdown-menu'

import fullOtherIcon from 'icons/full-other.svg'
import { SvgIcon } from 'ui-kit/SvgIcon/SvgIcon'

import styles from './DropdownMenuWrapper.module.scss'

type DropdownMenuWrapperProps = {
  title: string
  children: React.ReactNode
}

export function DropdownMenuWrapper({
  title,
  children,
}: DropdownMenuWrapperProps) {
  return (
    <DropdownMenu.Root>
      <DropdownMenu.Trigger
        className={styles['menu-button']}
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
