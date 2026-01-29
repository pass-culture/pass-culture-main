import * as DropdownMenu from '@radix-ui/react-dropdown-menu'
import cn from 'classnames'

import { Button } from '@/design-system/Button/Button'
import {
  ButtonColor,
  ButtonSize,
  ButtonVariant,
  IconPositionEnum,
} from '@/design-system/Button/types'
import fullDownIcon from '@/icons/full-down.svg'

import dropdownStyles from '../HeaderDropdown/HeaderDropdown.module.scss'
import styles from './HeaderHelpDropdown.module.scss'
import { HelpDropdownMenu } from './HelpDropdownMenu'

export const HeaderHelpDropdown = () => {
  return (
    <DropdownMenu.Root>
      <DropdownMenu.Trigger asChild>
        <Button
          variant={ButtonVariant.TERTIARY}
          color={ButtonColor.NEUTRAL}
          size={ButtonSize.SMALL}
          icon={fullDownIcon}
          iconPosition={IconPositionEnum.RIGHT}
          label="Centre d’aide"
        />
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
