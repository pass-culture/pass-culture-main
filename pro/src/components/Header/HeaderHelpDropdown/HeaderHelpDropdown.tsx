import * as DropdownMenu from '@radix-ui/react-dropdown-menu'
import cn from 'classnames'

import { HelpDropdownMenu } from 'components/Header/HeaderHelpDropdown/HelpDropdownMenu'
import fullDownIcon from 'icons/full-down.svg'
import { Button } from 'ui-kit/Button/Button'
import { ButtonVariant, IconPositionEnum } from 'ui-kit/Button/types'

import dropdownStyles from '../HeaderDropdown/HeaderDropdown.module.scss'

import styles from './HeaderHelpDropdown.module.scss'

export const HeaderHelpDropdown = () => {
  return (
    <DropdownMenu.Root>
      <DropdownMenu.Trigger asChild>
        <Button
          variant={ButtonVariant.QUATERNARY}
          title="Centre d'aide"
          className={styles['dropdown-button']}
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
