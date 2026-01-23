import * as DropdownMenu from '@radix-ui/react-dropdown-menu'
import { useState } from 'react'

import { Button } from '@/design-system/Button/Button'
import {
  type ButtonProps,
  ButtonVariant,
  IconPositionEnum,
} from '@/design-system/Button/types'
import fullDownIcon from '@/icons/full-down.svg'
import fullUpIcon from '@/icons/full-up.svg'

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
  triggerProps?: Partial<ButtonProps & { as: 'button' }>
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
      <div className={styles['offer-button-wrapper']}>
        <DropdownMenu.Trigger data-testid="dropdown-menu-trigger" asChild>
          <Button
            fullWidth
            label={name}
            variant={ButtonVariant.PRIMARY}
            icon={isOpen ? fullUpIcon : fullDownIcon}
            iconPosition={IconPositionEnum.RIGHT}
            {...triggerProps}
          />
        </DropdownMenu.Trigger>
      </div>
      <DropdownMenu.Portal>
        <DropdownMenu.Content align="start" className={styles.panel}>
          {options.map((option) => (
            <div className={styles.option} key={option.id}>
              <DropdownMenu.Item asChild>{option.element}</DropdownMenu.Item>
            </div>
          ))}
        </DropdownMenu.Content>
      </DropdownMenu.Portal>
    </DropdownMenu.Root>
  )
}
