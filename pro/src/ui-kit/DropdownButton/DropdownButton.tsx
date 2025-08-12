import * as DropdownMenu from '@radix-ui/react-dropdown-menu'
import classNames from 'classnames'
import { useState } from 'react'

import fullDownIcon from '@/icons/full-down.svg'
import fullUpIcon from '@/icons/full-up.svg'

import { Button, ButtonProps } from '../Button/Button'
import { SvgIcon } from '../SvgIcon/SvgIcon'
import styles from './DropdownButton.module.scss'

export type DropdownButtonProps = {
  /**
   * The text content of the dropdown trigger button
   */
  name: string
  /**
   * The list of elements (buttons or links) to be displayed as a dropdown menu when the dropdown is open
   */
  options: { element: React.ReactNode; id: string }[]
  /**
   * The dropdown trigger button props
   */
  triggerProps?: Partial<ButtonProps>
}

export function DropdownButton({
  name,
  options,
  triggerProps,
}: DropdownButtonProps) {
  const [isOpen, setIsOpen] = useState<boolean>(false)

  return (
    <DropdownMenu.Root
      open={isOpen}
      onOpenChange={(open) => {
        setIsOpen(open)
      }}
    >
      <DropdownMenu.Trigger
        className={classNames(styles['trigger'])}
        data-testid="dropdown-menu-trigger"
        asChild
      >
        <Button className={styles['trigger-button']} {...triggerProps}>
          <span className={styles['trigger-button-name']}>{name}</span>
          <span className={styles['trigger-icon']}>
            {isOpen ? (
              <SvgIcon src={fullUpIcon} alt="" />
            ) : (
              <SvgIcon src={fullDownIcon} alt="" />
            )}
          </span>
        </Button>
      </DropdownMenu.Trigger>
      <DropdownMenu.Portal>
        <DropdownMenu.Content align="start" className={styles['panel']}>
          {options.map((option) => (
            <DropdownMenu.Item
              asChild
              key={option.id}
              className={styles['option']}
            >
              {option.element}
            </DropdownMenu.Item>
          ))}
        </DropdownMenu.Content>
      </DropdownMenu.Portal>
    </DropdownMenu.Root>
  )
}
