import { Button } from '@/design-system/Button/Button'
import {
  ButtonColor,
  ButtonSize,
  ButtonVariant,
  IconPositionEnum,
} from '@/design-system/Button/types'
import fullDownIcon from '@/icons/full-down.svg'
import { Dropdown } from '@/ui-kit/Dropdown/Dropdown'

import { HelpDropdownMenu } from './HelpDropdownMenu'

export const HeaderHelpDropdown = () => {
  return (
    <Dropdown
      title="Centre d'aide"
      sideOffset={16}
      trigger={
        <Button
          variant={ButtonVariant.TERTIARY}
          color={ButtonColor.NEUTRAL}
          size={ButtonSize.SMALL}
          icon={fullDownIcon}
          iconPosition={IconPositionEnum.RIGHT}
          label="Centre d'aide"
        />
      }
    >
      <HelpDropdownMenu />
    </Dropdown>
  )
}
