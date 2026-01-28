import * as DropdownMenu from '@radix-ui/react-dropdown-menu'
import cn from 'classnames'

import { HelpDropdownMenu } from '@/app/App/layouts/components/Header/components/HeaderHelpDropdown/HelpDropdownMenu'
import { Button } from '@/design-system/Button/Button'
import { ButtonColor, ButtonVariant } from '@/design-system/Button/types'
import fullHelpIcon from '@/icons/full-help.svg'
import fullRightIcon from '@/icons/full-right.svg'
import { SvgIcon } from '@/ui-kit/SvgIcon/SvgIcon'

import styles from './SideNavLinks.module.scss'

interface HelpDropdownNavItemProps {
  isMobileScreen: boolean
}

export const HelpDropdownNavItem = ({
  isMobileScreen,
}: HelpDropdownNavItemProps) => (
  <DropdownMenu.Root>
    <DropdownMenu.Trigger asChild>
      <div className={cn(styles['nav-links-item'], styles['nav-links-help'])}>
        <Button
          variant={ButtonVariant.TERTIARY}
          color={ButtonColor.NEUTRAL}
          icon={fullHelpIcon}
          label="Centre d’aide"
        />
        <SvgIcon src={fullRightIcon} alt="" width="18" />
      </div>
    </DropdownMenu.Trigger>
    <DropdownMenu.Content
      side={isMobileScreen ? 'top' : 'right'}
      className={styles['help-dropdown-content']}
    >
      <HelpDropdownMenu />
    </DropdownMenu.Content>
  </DropdownMenu.Root>
)
