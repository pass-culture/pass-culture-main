import * as DropdownMenu from '@radix-ui/react-dropdown-menu'
import cn from 'classnames'

import fullDownIcon from 'icons/full-down.svg'
import { Button } from 'ui-kit/Button/Button'
import { ButtonVariant, IconPositionEnum } from 'ui-kit/Button/types'

import dropdownStyles from '../HeaderDropdown/HeaderDropdown.module.scss'

import styles from './HeaderHelpDropdown.module.scss'
import { HelpDropdownMenu } from './HelpDropdownMenu'

export const HeaderHelpDropdown = () => {
  return (
    <DropdownMenu.Root>
      <DropdownMenu.Trigger asChild>
        <Button
          variant={ButtonVariant.QUATERNARY}
          icon={fullDownIcon}
          iconPosition={IconPositionEnum.RIGHT}
        >
          Centre d’aide
        </Button>
      </DropdownMenu.Trigger>
      <DropdownMenu.Portal>
        <DropdownMenu.Content
          className={cn(dropdownStyles['pop-in'], styles['pop-in'])}
          align="end"
          sideOffset={16}
        >
          <div className={cn(dropdownStyles['menu'], styles['menu'])}>
            <HelpDropdownMenu />
          </div>
        </DropdownMenu.Content>
      </DropdownMenu.Portal>
    </DropdownMenu.Root>
  )
}
